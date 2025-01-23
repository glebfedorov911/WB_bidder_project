import asyncio
import httpx

from core.settings import settings
from .requestor import HttpxRequestor
from .exceptions import CustomHTTPException



class SMSCSender:
    URL = settings.smsc.SMSC_URL
    CODE_ERROR_POSITION = 2
    TYPE_RESPONSE_POSITION = 0
    ERROR = "ERROR"
    OK = "OK"
    ERROR_CODE = {
        "1": "Error in params",
        "2": "Incorrect login or password",
        "3": "Not enough money",
        "4": "IP temporary blocked",
        "5": "Bad data format",
        "6": "Message is denied",
        "7": "Bad format phone",
        "8": "Cannot send message",
        "9": "Cannot send a lot of sms in minute",
    }
    UNKNOWN = "Internal Server Error"

    def __init__(self, smsc_login: str, smsc_psw: str, smsc_tg: str):
        self.httpx_request: HttpxRequestor = HttpxRequestor()
        self.smsc_login = smsc_login
        self.smsc_psw = smsc_psw
        self.smsc_tg = smsc_tg

    async def sms_send(self, phone: str, code: str) -> bool:
        try:
            response = await self.__sms_send(phone=phone, code=code)
            print(response)
            return self.__check_status_responce(response=response)
        except CustomHTTPException as e:
            settings.statberry_logger.get_loger().error(e)
            raise CustomHTTPException("Unable to send sms. Please, try later")
        except Exception as e:
            settings.statberry_logger.get_loger().error(e)
            raise CustomHTTPException("Internal Server Error")

    async def __sms_send(self, phone: str, code: str) -> list:
        url = self.__url_creator(phone=phone, code=code)
        return await self.httpx_request.send(url=url)

    def __url_creator(self, phone: str, code: str):
        params = {
            "login": self.smsc_login,
            "psw": self.smsc_psw,
            "phones": phone,
            "mes": code,
            "tg": self.smsc_tg
        }
        return self.URL + "?" + '&'.join([
            f"{key}={value}" for key, value in params.items()
        ])

    def __check_status_responce(self, response):
        type_response = response[self.TYPE_RESPONSE_POSITION]
        if type_response == self.ERROR:
            code_error = response[self.CODE_ERROR_POSITION]
            raise CustomHTTPException(self.ERROR_CODE[code_error])
        elif type_response == self.OK:
            return True
        else:
            raise CustomHTTPException(self.UNKNOWN)