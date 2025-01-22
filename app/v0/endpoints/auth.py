from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from hashlib import sha256
from datetime import datetime
import uuid

from core.models.enum.accountstatus import AccountStatus
from core.models.databasehelper import database_helper
from core.models.user import User
from core.models.enum.typecode import TypeCode
from core.settings import settings
from ..services.user_service import UserManagerService, UserAuthService, UserQueryService, get_auth_user_service, get_current_user, get_user_repository, get_user_manager_service, get_user_query_service
from ..services.verificationcode_service import VerificationService, VerificationCodeCompare, SMSService, VerificationCodeManagerService, get_verification_service, get_verification_compare, get_ver_code_manager
from ..services.token_service import TokenFabricService, TokenManagerService, TokenVerifyService, TokenEncodeService, TokenService, get_token_encode_service, get_token_fabric_service, get_token_repository, get_token_manager_service
from ..repositories.user_repository import UserRepository
from ..repositories.token_repository import TokenRepository
from ..repositories.verificationcode_repository import VerCodeRepository
from ..dependencies.password_hasher import PasswordHasher
from ..dependencies.code_generator import CodeGenerator
from ..dependencies.exceptions import CustomHTTPException, SMSError
from ..dependencies.jwt_token_creator import JWTTokenCreator
from ..dependencies.sms_sender import SMSCSender
from ..dependencies.encoder import Encoder, get_encoder
from ..dependencies.validators import get_phone_validator, get_email_validator, Validator
from ..schemas.user_schema import UserCreate, UserRead, UserUpdate
from ..schemas.token_schema import Token, RefreshTokenUpdate, RefreshTokenCreate, RefreshTokenSchema
from ..schemas.verificationcode_schema import PhoneSchema, VerificationSMS, RecoveryPassword


router = APIRouter(tags=["Auth"], prefix="/auth")

@router.post("/register", response_model=None)
async def register(
    user_create: UserCreate,
    user_manager_service: UserManagerService = Depends(get_user_manager_service),
    verification_service: VerificationService = Depends(get_verification_service),
    phone_validator: Validator = Depends(get_phone_validator),
    email_validator: Validator = Depends(get_email_validator),
) -> dict[str, str]:
    try:
        user_create.phone = phone_validator.valid(user_create.phone)
        
        if user_create.email:
            user_create.email = email_validator.valid(user_create.email)
        
        user = await user_manager_service.create(user_create=user_create)
        return await verification_service.send_code(user_id=user.id, phone=user.phone, type_code=TypeCode.ACCOUNT_CONFIRM)
    except CustomHTTPException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
    except SMSError as e:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail=e)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.post('/login')
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserAuthService = Depends(get_auth_user_service),
    token_fabric: TokenFabricService = Depends(get_token_fabric_service),
    token_repository: TokenRepository = Depends(get_token_repository),
    token_encode_service: TokenEncodeService = Depends(get_token_encode_service),
    encoder: Encoder = Depends(get_encoder),
) -> Token:
    try:
        phone = form_data.username
        password = form_data.password
        user = await user_service.authenticate(phone=phone, password=password)

        user_agent = request.headers.get("user-agent")
        data = {
            "sub": str(user.id), 
            "user_agent": encoder.encode(user_agent)
        }
        
        token_service = TokenService(token_fabric=token_fabric, expire_access_time=settings.auth.ACCESS_TOKEN_EXPIRE_SECONDS, expire_refresh_time=settings.auth.REFRESH_TOKEN_EXPIRE_SECONDS, data=data)
        access_token, expire_access, refresh_token, expire_refresh = token_service.create_tokens()

        token_schema = RefreshTokenCreate(
            token=token_encode_service.encode_token(token=refresh_token),
            expires_at=expire_refresh,
            user_id=user.id
        )
        await token_repository.create(data=token_schema)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )
    except:
        raise

@router.post("/logout")
async def logout(
    refresh_token: RefreshTokenSchema,
    token_encode_service: TokenEncodeService = Depends(get_token_encode_service),
    token_manager_service: TokenManagerService = Depends(get_token_manager_service),
) -> dict[str, str]:
    try:
        encode_refresh_token = token_encode_service.encode_token(token=refresh_token.refresh_token)
        await token_manager_service.set_token_incative(encode_refresh_token=encode_refresh_token)
        return {"message": "Successfully logout"}
    except:
        raise

async def send_code_and_create_user(
    phone: str, 
    user_service: UserQueryService,
    verification_service: VerificationService,
    type_code: TypeCode
) -> dict:
    try:
        user = await user_service.get_user_by_phone(phone)
        return await verification_service.send_code(user_id=user.id, phone=phone, type_code=type_code)
    except CustomHTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Unable to send SMS. Please try again later."
        )

@router.post("/send-sms")
async def send_sms(
    phone_schema: PhoneSchema,
    verification_service: VerificationService = Depends(get_verification_service),
    user_service: UserQueryService = Depends(get_user_query_service),
) -> dict[str, str]:
    try:
        return await send_code_and_create_user(phone=phone_schema.phone, user_service=user_service, verification_service=verification_service, type_code=TypeCode.ACCOUNT_CONFIRM)
    except:
        raise

@router.post("/verify-sms")
async def verify_sms(
    verification_sms: VerificationSMS,
    user_service: UserQueryService = Depends(get_user_query_service),
    verification_compare: VerificationCodeCompare = Depends(get_verification_compare),
    user_manager_service: UserManagerService = Depends(get_user_manager_service),
    ver_code_manager: VerificationCodeManagerService = Depends(get_ver_code_manager),
) -> dict[str, str]:
    try:
        phone = verification_sms.phone
        code = verification_sms.code

        user = await user_service.get_user_by_phone(phone=phone)
        if not (ver_code := await verification_compare.get_ver_code(user_id=user.id, code=code, type_code=TypeCode.ACCOUNT_CONFIRM)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect code"
            )

        await user_manager_service.set_account_status(user=user, account_status=AccountStatus.ACTIVE)
        await ver_code_manager.update_used_status(id=ver_code.id, is_used=False)
        return {"message": "Success verification"}
    except CustomHTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/forgot-password")
async def forgot_password(
    phone_schema: PhoneSchema,
    verification_service: VerificationService = Depends(get_verification_service),
    user_service: UserQueryService = Depends(get_user_query_service),
):  
    try:
        return await send_code_and_create_user(phone=phone_schema.phone, user_service=user_service, verification_service=verification_service, type_code=TypeCode.PASSWORD_RESTORE)
    except:
        raise

@router.post("/reset-password")
async def reset_password(
    recovery_password: RecoveryPassword,
    user_manager_service: UserManagerService = Depends(get_user_manager_service),
    verification_compare: VerificationCodeCompare = Depends(get_verification_compare),
    ver_code_manager: VerificationCodeManagerService = Depends(get_ver_code_manager),
) -> UserRead:
    try:
        phone = recovery_password.phone
        code = recovery_password.code

        user = await user_manager_service.get_user_by_phone(phone=phone)
        if not (ver_code := await verification_compare.get_ver_code(user_id=user.id, code=code, type_code=TypeCode.PASSWORD_RESTORE)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect code"
            )
        await ver_code_manager.update_used_status(id=ver_code.id, is_used=False)

        return await user_manager_service.change_password(user=user, recovery_password=recovery_password)
    except:
        raise

@router.get("/current-user")
async def current_user(
    current_user: UserRead = Depends(get_current_user)
) -> UserRead:
    return current_user