import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies.code_generator import CodeGenerator
from ..dependencies.sms_sender import SMSCSender
from ..interfaces.repository_interface import IVerCodeRepository
from ..schemas.verificationcode_schema import VerCodeCreate, VerCodeUpdate
from core.models.databasehelper import database_helper
from ..repositories.verificationcode_repository import VerCodeRepository
from core.settings import settings
from core.models.enum.typecode import TypeCode
from ..dependencies.exceptions import SMSError
from ..dependencies.exceptions import (
    CustomHTTPException, HTTP405Exception, HTTP404Exception, 
    HTTP500Exception, HTTP403Exception, HTTP401Exception,
    RepositoryException, HTTP400Exception
)


class SMSService:
    def __init__(
        self,
        sms_sender: SMSCSender,
    ):
        self.sms_sender = sms_sender

    async def send_sms(self, phone: str, code: str) -> bool:
        try:
            return await self.sms_sender.sms_send(phone=phone, code=code)
        except CustomHTTPException as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP400Exception(e)
        except Exception as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP500Exception("Internal Server Error")

class VerificationCodeManagerService:
    def __init__(
        self,
        vc_repo: IVerCodeRepository
    ):
        self.vc_repo = vc_repo

    async def create(self, data: VerCodeCreate):
        try:
            return await self.vc_repo.create(data=data)
        except RepositoryException as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP404Exception(e)

    async def update_used_status(self, id: uuid.UUID, is_used: bool):
        try:
            data = VerCodeUpdate(
                is_used=is_used
            )
            return await self.vc_repo.update(id=id, data=data)
        except RepositoryException as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP404Exception(e)


class VerificationCodeCompare:
    def __init__(
        self, vc_repo: IVerCodeRepository
    ):
        self.vc_repo = vc_repo

    async def get_ver_code(self, user_id: uuid.UUID, code: str, type_code: TypeCode) -> bool:
        try:
            return await self.vc_repo.get_by_user_id_and_code(user_id=user_id, code=code, type_code=type_code)
        except RepositoryException as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP404Exception(e)

class VerificationService:
    def __init__(self, generator: CodeGenerator, manager: VerificationCodeManagerService, sms: SMSService):
        self.manager = manager
        self.sms = sms
        self.generator = generator

    async def send_code(self, user_id: uuid.UUID, phone: str, type_code: str | None = None) -> dict:
        try:
            code = self.generator.generate_code()
            await self.sms.send_sms(phone=phone, code=code)
            ver_code = self.__create_ver_code_create_scheme(code=code, user_id=user_id, phone=phone, type_code=type_code)
            await self.manager.create(data=ver_code)
            return {"message": "Verification code send successfully"}
        except CustomHTTPException as e:
            settings.statberry_logger.get_loger().error(e)
            raise HTTP400Exception(e)

    def __create_ver_code_create_scheme(self, user_id: uuid.UUID, code: str, phone: str, type_code: str | None = None):
        ver_code = VerCodeCreate(code=code, user_id=user_id)
        if type_code:
            ver_code.type_code = type_code
        return ver_code

def get_code_generator() -> CodeGenerator:
    return CodeGenerator()

def get_ver_code_repository(db_session: AsyncSession = Depends(database_helper.async_session_depends)) -> IVerCodeRepository:
    return VerCodeRepository(db_session=db_session)

def get_ver_code_manager(ver_code_repo: IVerCodeRepository = Depends(get_ver_code_repository)) -> VerificationCodeManagerService:
    return VerificationCodeManagerService(vc_repo=ver_code_repo)

def get_sms_sender() -> SMSCSender:
    return SMSCSender(
        smsc_login=settings.smsc.SMSC_LOGIN,
        smsc_psw=settings.smsc.SMSC_PSW,
        smsc_tg=settings.smsc.SMSC_TG
    )

def get_sms_service(sms_sender: SMSCSender = Depends(get_sms_sender)) -> SMSService:
    return SMSService(sms_sender=sms_sender)

def get_verification_service(
    code_generator: CodeGenerator = Depends(get_code_generator),
    ver_code_manager: VerificationCodeManagerService = Depends(get_ver_code_manager),
    sms_service: SMSService = Depends(get_sms_service),
) -> VerificationService:
    return VerificationService(
        generator=code_generator,
        manager=ver_code_manager,
        sms=sms_service
    )

def get_verification_compare(ver_code_repo: IVerCodeRepository = Depends(get_ver_code_repository)) -> VerificationCodeCompare:
    return VerificationCodeCompare(vc_repo=ver_code_repo)