from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from config import API_KEY, CURRENCY_API_KEY
import requests
import random

user_budget = {}

# Команда /start: Приветственное сообщение
async def start(update: Update, context) -> None:
    await update.message.reply_text(
        "Привет! Я — твой Финансовый помощник. Я помогу тебе следить за курсами валют, вести финансовые отчеты и планировать бюджет."
    )

# Команда /help: Список доступных команд
async def help_command(update: Update, context) -> None:
    await update.message.reply_text(
        "Вот список доступных команд:\n"
        "/start - Начать работу с ботом\n"
        "/help - Список команд\n"
        "/budget - Ведение бюджета\n"
        "/currency - Курсы валют\n"
        "/tips - Советы по экономии\n"
        "/menu - Показать меню с кнопками"
    )

# Команда /currency: Показывает курс валют
async def currency(update: Update, context) -> None:
    try:
        url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/USD"
        response = requests.get(url)
        data = response.json()
        rate = data["conversion_rates"]["RUB"]
        await update.message.reply_text(f"Курс USD к RUB: {rate}")
    except Exception as e:
        await update.message.reply_text("Не удалось получить курс валют. Попробуйте позже.")

# Команда /budget: Начало работы с бюджетом
async def budget(update: Update, context) -> None:
    user_id = update.effective_user.id
    user_budget[user_id] = user_budget.get(user_id, {"income": 0, "expense": 0})
    await update.message.reply_text(
        "Вы хотите добавить доход или расход? Введите:\n"
        "- `доход [сумма]`\n"
        "- `расход [сумма]`\n"
        "Например: доход 5000 или расход 1500",
        parse_mode="Markdown"
    )

# Обработка текста для добавления доходов и расходов
async def handle_budget(update: Update, context) -> None:
    user_id = update.effective_user.id
    text = update.message.text.lower()

    if user_id not in user_budget:
        await update.message.reply_text("Сначала введите команду /budget.")
        return

    try:
        if text.startswith("доход"):
            amount = int(text.split()[1])
            user_budget[user_id]["income"] += amount
            await update.message.reply_text(f"Доход добавлен: +{amount} руб.")
        elif text.startswith("расход"):
            amount = int(text.split()[1])
            user_budget[user_id]["expense"] += amount
            await update.message.reply_text(f"Расход добавлен: -{amount} руб.")
        else:
            await update.message.reply_text("Неправильный формат. Используйте: доход [сумма] или расход [сумма].")
    except (IndexError, ValueError):
        await update.message.reply_text("Укажите сумму правильно. Пример: доход 5000 или расход 1500.")

# Команда /tips: Советы по экономии
async def tips(update: Update, context) -> None:
    tips_list = [
        "Составляйте бюджет и следите за своими расходами каждый месяц.",
        "Откладывайте 10% своего дохода на сбережения.",
        "Избегайте импульсивных покупок — подождите 24 часа перед покупкой.",
        "Используйте скидки и программы лояльности.",
        "Инвестируйте в своё образование — это лучший актив.",
        "Старайтесь оплачивать долги вовремя, чтобы избежать процентов.",
        "Готовьте еду дома вместо заказов из ресторанов — это дешевле и полезнее.",
        "Сравнивайте цены перед покупкой, чтобы находить лучшие предложения.",
    ]
    tip = random.choice(tips_list)
    await update.message.reply_text(f"💡 Совет: {tip}")

# Команда /menu: Показывает кнопки меню
async def menu(update: Update, context) -> None:
    keyboard = [
        [InlineKeyboardButton("Курсы валют", callback_data="currency")],
        [InlineKeyboardButton("Бюджет", callback_data="budget")],
        [InlineKeyboardButton("Советы", callback_data="tips")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

# Обработчик кнопок
async def button_handler(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "currency":
        await currency(update, context)
    elif query.data == "budget":
        await budget(update, context)
    elif query.data == "tips":
        await tips(update, context)

# Основная функция
def main():
    application = Application.builder().token(API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("currency", currency))
    application.add_handler(CommandHandler("budget", budget))
    application.add_handler(CommandHandler("tips", tips))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_budget))

    application.run_polling()

if __name__ == "__main__":
    main()
