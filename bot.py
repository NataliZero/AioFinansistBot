from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Application
import logging
from config import API_KEY  # Импортируем API-ключ из config.py

# Включаем логирование для отслеживания ошибок
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Асинхронная функция, которая будет отправлять приветственное сообщение при команде /start
async def start(update: Update, context: CallbackContext) -> None:
    # Используем context для доступа к данным
    await update.message.reply_text("Привет! Я — твой Финансовый помощник. Я помогу тебе следить за курсами валют, вести финансовые отчеты и планировать бюджет.")

# Основная асинхронная функция, которая запускает бота
async def main() -> None:
    # Создаем объект Application и передаем API-ключ
    application = Application.builder().token(API_KEY).build()

    # Добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Запускаем бота
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
