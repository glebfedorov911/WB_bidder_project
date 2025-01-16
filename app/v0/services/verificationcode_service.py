import uuid

from ..dependencies.code_generator import CodeGenerator
from ..dependencies.sms_sender import SMSCSender
from ..interfaces.repository_interface import IVerCodeRepository
from ..schemas.verificationcode_schema import VerCodeCreate, VerCodeUpdate


class SMSService:
    def __init__(
        self,
        sms_sender: SMSCSender,
    ):
        self.sms_sender = sms_sender

    async def send_sms(self, phone: str, code: str) -> bool:
        return self.sms_sender.sms_send(phone=phone, code=code)
    
class VerificationCodeManagerService:
    def __init__(
        self,
        vc_repo: IVerCodeRepository
    ):
        self.vc_repo = vc_repo

    async def create(self, data: VerCodeCreate):
        return await self.vc_repo.create(data=data)

    async def update(self, id: uuid.UUID, data: VerCodeUpdate):
        return await self.vc_repo.update(id=id, data=data)