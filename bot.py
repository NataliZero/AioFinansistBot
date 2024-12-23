import asyncio
import random
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import sqlite3
import requests

# Настройки
from config import API_KEY, CURRENCY_API_URL

bot = Bot(token=API_KEY)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# База данных
conn = sqlite3.connect('user.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE,
    name TEXT,
    income REAL DEFAULT 0,
    category1 TEXT,
    category2 TEXT,
    category3 TEXT,
    expenses1 REAL,
    expenses2 REAL,
    expenses3 REAL
)
''')
conn.commit()

# Состояния
class FinancesForm(StatesGroup):
    category1 = State()
    expenses1 = State()
    category2 = State()
    expenses2 = State()
    category3 = State()
    expenses3 = State()

class IncomeForm(StatesGroup):
    income = State()

# Кнопки меню
button_exchange_rates = KeyboardButton(text="Курсы валют")
button_tips = KeyboardButton(text="Советы по экономии")
button_budget = KeyboardButton(text="Бюджет")

menu = ReplyKeyboardMarkup(
    keyboard=[
        [button_exchange_rates],
        [button_tips, button_budget]
    ], resize_keyboard=True
)

# Команды бота
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "Привет! Я — твой Финансовый помощник. Я помогу тебе следить за курсами валют, вести финансовые отчеты и планировать бюджет.",
        reply_markup=menu
    )

@dp.message(F.text == "Курсы валют")
async def exchange_rates(message: Message):
    try:
        response = requests.get(CURRENCY_API_URL)
        data = response.json()
        if response.status_code != 200:
            await message.answer("Не удалось получить данные о курсе валют!")
            return

        usd_to_rub = data['conversion_rates']['RUB']
        eur_to_usd = data['conversion_rates']['EUR']
        euro_to_rub = eur_to_usd * usd_to_rub

        await message.answer(f"1 USD - {usd_to_rub:.2f} RUB\n1 EUR - {euro_to_rub:.2f} RUB")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

@dp.message(F.text == "Советы по экономии")
async def send_tips(message: Message):
    tips = [
        "Совет 1: Ведите бюджет и следите за своими расходами.",
        "Совет 2: Откладывайте часть доходов на сбережения.",
        "Совет 3: Покупайте товары по скидкам и распродажам.",
        "Совет 4: Используйте кэшбэк и бонусные программы.",
        "Совет 5: Планируйте крупные покупки заранее.",
        "Совет 6: Избегайте импульсивных покупок.",
        "Совет 7: Погашайте кредиты с наибольшими процентами в первую очередь.",
        "Совет 8: Сравнивайте цены перед покупкой.",
        "Совет 9: Экономьте на повседневных расходах, например, готовьте дома.",
        "Совет 10: Регулярно проверяйте свои финансовые цели и корректируйте их."
    ]
    tip = random.choice(tips)
    await message.answer(tip)

@dp.message(F.text == "Бюджет")
async def budget_menu(message: Message):
    budget_buttons = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить доход")],
            [KeyboardButton(text="Добавить расходы")],
            [KeyboardButton(text="Показать баланс")]
        ], resize_keyboard=True
    )
    await message.answer("Выберите действие:", reply_markup=budget_buttons)

@dp.message(F.text == "Добавить доход")
async def add_income(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    name = message.from_user.full_name

    # Проверяем, есть ли запись о пользователе
    cursor.execute('''
    INSERT OR IGNORE INTO users (telegram_id, name)
    VALUES (?, ?)
    ''', (telegram_id, name))
    conn.commit()

    await state.set_state(IncomeForm.income)
    await message.reply("Введите сумму дохода:")

@dp.message(IncomeForm.income)
async def income_handler(message: Message, state: FSMContext):
    try:
        income_amount = float(message.text)
        telegram_id = message.from_user.id

        cursor.execute('''
        UPDATE users
        SET income = income + ?
        WHERE telegram_id = ?
        ''', (income_amount, telegram_id))
        conn.commit()

        await state.clear()
        await message.reply(f"Доход в размере {income_amount} добавлен!")
    except ValueError:
        await message.reply("Пожалуйста, введите числовое значение дохода.")

@dp.message(F.text == "Добавить расходы")
async def finances(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    name = message.from_user.full_name

    # Проверяем, есть ли запись о пользователе
    cursor.execute('''
    INSERT OR IGNORE INTO users (telegram_id, name)
    VALUES (?, ?)
    ''', (telegram_id, name))
    conn.commit()

    await state.set_state(FinancesForm.category1)
    await message.reply("Введите первую категорию расходов:")

@dp.message(FinancesForm.category1)
async def category1_handler(message: Message, state: FSMContext):
    await state.update_data(category1=message.text)
    await state.set_state(FinancesForm.expenses1)
    await message.reply("Введите сумму расходов для первой категории:")

@dp.message(FinancesForm.expenses1)
async def expenses1_handler(message: Message, state: FSMContext):
    await state.update_data(expenses1=float(message.text))
    await state.set_state(FinancesForm.category2)
    await message.reply("Введите вторую категорию расходов или отправьте 'Пропустить', если у вас нет второй категории:")

@dp.message(FinancesForm.category2)
async def category2_handler(message: Message, state: FSMContext):
    if message.text.lower() == 'пропустить':
        await state.update_data(category2=None, expenses2=0.0)
        await state.set_state(FinancesForm.category3)
        await message.reply("Введите третью категорию расходов или отправьте 'Пропустить', если у вас нет третьей категории:")
    else:
        await state.update_data(category2=message.text)
        await state.set_state(FinancesForm.expenses2)
        await message.reply("Введите сумму расходов для второй категории:")

@dp.message(FinancesForm.expenses2)
async def expenses2_handler(message: Message, state: FSMContext):
    await state.update_data(expenses2=float(message.text))
    await state.set_state(FinancesForm.category3)
    await message.reply("Введите третью категорию расходов или отправьте 'Пропустить', если у вас нет третьей категории:")

@dp.message(FinancesForm.category3)
async def category3_handler(message: Message, state: FSMContext):
    if message.text.lower() == 'пропустить':
        await state.update_data(category3=None, expenses3=0.0)
        await save_expenses(message, state)
    else:
        await state.update_data(category3=message.text)
        await state.set_state(FinancesForm.expenses3)
        await message.reply("Введите сумму расходов для третьей категории:")

@dp.message(FinancesForm.expenses3)
async def expenses3_handler(message: Message, state: FSMContext):
    await state.update_data(expenses3=float(message.text))
    await save_expenses(message, state)

async def save_expenses(message: Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = message.from_user.id
    name = message.from_user.full_name

    # Проверяем, есть ли запись о пользователе
    cursor.execute('''
    INSERT OR IGNORE INTO users (telegram_id, name)
    VALUES (?, ?)
    ''', (telegram_id, name))

    cursor.execute('''
    UPDATE users
    SET category1 = ?, expenses1 = ?, category2 = ?, expenses2 = ?, category3 = ?, expenses3 = ?
    WHERE telegram_id = ?
    ''', (data.get('category1'), data.get('expenses1', 0.0),
          data.get('category2'), data.get('expenses2', 0.0),
          data.get('category3'), data.get('expenses3', 0.0), telegram_id))
    conn.commit()

    await state.clear()
    await message.reply("Ваши расходы успешно сохранены!")

@dp.message(F.text == "Показать баланс")
async def show_balance(message: Message):
    telegram_id = message.from_user.id

    cursor.execute('''
    SELECT income, (expenses1 + expenses2 + expenses3) AS total_expenses
    FROM users
    WHERE telegram_id = ?
    ''', (telegram_id,))
    result = cursor.fetchone()

    if result:
        income, total_expenses = result
        balance = income - total_expenses
        await message.reply(f"Ваш баланс: {balance:.2f} RUB\nДоход: {income:.2f} RUB\nРасходы: {total_expenses:.2f} RUB")
    else:
        await message.reply("Вы еще не добавили данные о доходах и расходах.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
