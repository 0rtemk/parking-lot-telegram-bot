from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import requests
import datetime

API_URL = 'http://localhost:5000'
BOT_TOKEN = '6786951973:AAGXPP6O25KsTxM6jjYbempzYSic71pB-aQ'

# Функция для получения парковок
def get_parkings():
    response = requests.get(f'{API_URL}/api/parkings')
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Функция для получения информации о конкретной парковке
def get_parking_info(parking_id):
    response = requests.post(f'{API_URL}/api/parking/select', json={'parkingId': parking_id})
    if response.status_code == 200:
        return response.json()
    else:
        return None

def start(update: Update, context: CallbackContext) -> None:
    parkings = get_parkings()
    buttons = [[InlineKeyboardButton(text=addr['street'], callback_data=f"select_{addr['id']}")] for addr in parkings['addresses']]
    keyboard = InlineKeyboardMarkup(buttons)

    update.message.reply_text(parkings['message'], reply_markup=keyboard)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    _, parking_id = query.data.split('_')

    if parking_id.isdigit():
        parking_info = get_parking_info(parking_id)
        n = parking_info['availableSpots']
        m = parking_info['lastUpdatedAt'].strftime('%d %B %H:%M')

        message = f"По данному адресу доступно {n} парковочных мест. Информация актуальна на {m}."
        buttons = [[InlineKeyboardButton(text="Назад", callback_data="back")]]
        keyboard = InlineKeyboardMarkup(buttons)

        query.edit_message_text(text=message, reply_markup=keyboard)

    elif query.data == 'back':
        start(update, context)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()