import os
import logging

from data import db_session
from service.cyber_advent_service import CyberAdventService
from service.user_service import UserService
from view.telegram_bot import TelegramBot
from web.rest_controller import RestController


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARN)
logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self.web_port = int(os.environ.get("PORT", 5000))
        self.bot_token = os.environ.get('API_BOT_TOKEN', 'PUT_YOUR_LOCAL_BOT_TOKEN')
        self.bot_name = os.environ.get('BOT_NAME', 'PUT_YOUR_LOCAL_BOT_NAME')
        self.database_url = os.environ.get('DB_URL')


def main():
    # Инициализация конфигурации
    config = Config()
    # Инициализация базы данных
    db_session.global_init(config.database_url)

    # Сервис для работы с пользователями
    user_service = UserService()
    # Сервис для работы с Cyber-адвентом
    advent_service = CyberAdventService()
    # Инициализируем сервис
    advent_service.init_recommendations()

    # Запуск REST-контроллера в фоне
    RestController(config.web_port, user_service, advent_service).run_background()
    # Запуск telegram бота
    TelegramBot(config.bot_token, config.bot_name, user_service, advent_service).run()


if __name__ == '__main__':
    main()
