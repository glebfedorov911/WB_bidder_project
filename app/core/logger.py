import logging


class StatBerryLogger:
    def __init__(self, loggername: str, filename: str):
        self.loggername = loggername
        self.filename = filename
    
    def get_loger(self) -> logging.Logger:
        logger = logging.getLogger(self.loggername)  
        logger.setLevel(logging.DEBUG) 

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG) 

        file_handler = logging.FileHandler(self.filename)
        file_handler.setLevel(logging.INFO)  

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger