import uuid

from ..dependencies.code_generator import CodeGenerator
from ..dependencies.sms_sender import SMSCSender
from ..interfaces.repository_interface import IVerCodeRepository
from ..schemas.verificationcode_schema import VerCodeCreate



class SMSService:
    def __init__(
        self,
        code_generator: CodeGenerator,
        sms_sender: SMSCSender,
        ver_code_repo: IVerCodeRepository
    ):
        self.code_generator = code_generator
        self.sms_sender = sms_sender
        self.ver_code_repo = ver_code_repo
    #ЗДЕСЬ ПРОПИСАНА ОТПРАВКА СМС(ПОТОМ УДАЛИТЬ КОММЕНТЫ)
    async def send_sms(self, phone: str):
        code = self.__code_generate()
        # self.sms_sender.sms_send(phone=phone, code=code)
    
    async def create(self, user_id: uuid.UUID, code: str):
        data = VerCodeCreate(

        )

    def __code_generate(self):
        return self.code_generator.generate_code()

class VerificationCodeService:
    #тут будет прописано создание кода, редактирование и получение
    ...