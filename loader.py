import os, dotenv


class Config:

    def __init__(self):
        dotenv.load_dotenv()
        self._token = os.getenv('BOT_TOKEN')

    def get_token(self, ) -> str:
        return self._token
