from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from hashlib import sha256
from datetime import datetime

from core.models.enum.accountstatus import AccountStatus
from core.models.databasehelper import database_helper
from core.models.user import User
from core.settings import settings
from ..services.user_service import UserManagerService, UserQueryService, get_current_user, get_user_repository, get_user_manager_service, get_user_query_service
from ..services.verificationcode_service import VerificationService, VerificationCodeCompare, SMSService, VerificationCodeManagerService, get_verification_service, get_verification_compare, get_ver_code_manager
from ..services.token_service import TokenFabricService, TokenVerifyService, TokenEncodeService, TokenService, get_token_encode_service, get_token_fabric_service, get_token_repository
from ..repositories.user_repository import UserRepository
from ..repositories.token_repository import TokenRepository
from ..repositories.verificationcode_repository import VerCodeRepository
from ..dependencies.password_hasher import PasswordHasher
from ..dependencies.code_generator import CodeGenerator
from ..dependencies.exceptions import CustomHTTPException
from ..dependencies.jwt_token_creator import JWTTokenCreator
from ..dependencies.sms_sender import SMSCSender
from ..schemas.user_schema import UserCreate, UserSMSSend, UserRead, UserUpdate
from ..schemas.token_schema import Token, RefreshTokenUpdate, RefreshTokenCreate
from ..schemas.verificationcode_schema import PhoneSchema, VerificationSMS


router = APIRouter(tags=["Auth"], prefix="/auth")

@router.post("/register", response_model=None)
async def register(
    user_create: UserCreate,
    user_manager_service: UserManagerService = Depends(get_user_manager_service),
    verification_service: VerificationService = Depends(get_verification_service),
):
    try:
        user = await user_manager_service.create(user_create=user_create)
        return await verification_service.send_code(user_id=user.id, phone=user.phone)
    except CustomHTTPException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.post('/login')
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserQueryService = Depends(get_user_query_service),
    token_fabric: TokenFabricService = Depends(get_token_fabric_service),
    token_repository: TokenRepository = Depends(get_token_repository),
    token_encode_service: TokenEncodeService = Depends(get_token_encode_service),
) -> Token:
    user = await user_service.get_user_by_phone(phone=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone or password"
        )
    data = {"sub": str(user.id)}
    token_service = TokenService(token_fabric=token_fabric, expire_access_time=settings.auth.ACCESS_TOKEN_EXPIRE_SECONDS, expire_refresh_time=settings.auth.REFRESH_TOKEN_EXPIRE_SECONDS, data=data)
    access_token, expire_access, refresh_token, expire_refresh = token_service.create_tokens()

    token_schema = RefreshTokenCreate(
        token=token_service.encode_token(token=refresh_token),
        expires_at=expire_refresh,
        user_id=user.id
    )
    await token_repository.create(data=token_schema)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/send-sms")
async def send_sms(
    phone_schema: PhoneSchema,
    verification_service: VerificationService = Depends(get_verification_service),
    user_service: UserQueryService = Depends(get_user_query_service),
):
    try:
        phone = phone_schema.phone
        user = await user_service.get_user_by_phone(phone)
        return await verification_service.send_code(user_id=user.id, phone=phone)
    except:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Unable to send SMS. Please try again later."
        )

@router.post("/verify-sms")
async def verify_sms(
    verification_sms: VerificationSMS,
    user_service: UserQueryService = Depends(get_user_query_service),
    verification_compare: VerificationCodeCompare = Depends(get_verification_compare),
    user_manager_service: UserManagerService = Depends(get_user_manager_service),
    ver_code_manager: VerificationCodeManagerService = Depends(get_ver_code_manager),
):
    phone = verification_sms.phone
    code = verification_sms.code
    user = await user_service.get_user_by_phone(phone=phone)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not found this phone"
        )
    if not (ver_code := await verification_compare.get_ver_code(user_id=user.id, code=code)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect code"
        )

    await user_manager_service.set_account_status(user_id=user.id, account_status=AccountStatus.ACTIVE)
    await ver_code_manager.update_used_status(id=ver_code.id, is_used=False)
    return {"message": "Success verification"}