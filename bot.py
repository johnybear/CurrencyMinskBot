import telegram
from telegram.ext import CommandHandler, Updater, RegexHandler, MessageHandler, ConversationHandler, Filters
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('bot')


class FindBankBot:
    START_COMMAND = 'start'
    CURRENCIES = ['USD', 'EUR', 'RUB']
    OPERATIONS = ['SELL', 'BUY']
    SEND_LOCATION_MESSAGE = 'SEND LOCATION'

    CURRENCIES_BUTTONS = [telegram.KeyboardButton(text=currency, callback_data=currency) for currency in CURRENCIES]
    OPERATIONS_BUTTONS = [telegram.KeyboardButton(text=operation, callback_data=operation) for operation in OPERATIONS]
    LOCATION_BUTTON = telegram.KeyboardButton(text=SEND_LOCATION_MESSAGE, request_location=True)

    CURRENCY_KEYBOARD = telegram.ReplyKeyboardMarkup([[button for button in CURRENCIES_BUTTONS]], resize_keyboard=True, one_time_keyboard=True)
    OPERATIONS_KEYBOARD = telegram.ReplyKeyboardMarkup([[button for button in OPERATIONS_BUTTONS]], resize_keyboard=True, one_time_keyboard=True)
    LOCATION_KEYBOARD = telegram.ReplyKeyboardMarkup([[LOCATION_BUTTON]], resize_keyboard=True, one_time_keyboard=True)

    OPERATION_TYPE, CURRENCY, LOCATION = range(3)

    def __init__(self):
        self.updater = Updater(token='445708182:AAEsrNtCjd0LWgJtTiKuSolgamftU5WnCpU', workers=1000)
        self.dispatcher = self.updater.dispatcher
        self.__add_handlers()

    def __add_handlers(self):
        logger.info('add handlers')
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler(self.START_COMMAND, self.start)],

            states={
                self.OPERATION_TYPE: [RegexHandler('^(SELL|BUY)$', self.operation, pass_user_data=True)],

                self.CURRENCY: [RegexHandler('^(USD|EUR|RUB)$', self.currency, pass_user_data=True)],

                self.LOCATION: [MessageHandler(Filters.location, self.location, pass_user_data=True)]

            },

            fallbacks=[RegexHandler('^Show$', self.done, pass_user_data=True)]
        )
        self.dispatcher.add_handler(conv_handler)
        self.dispatcher.add_handler(RegexHandler('', self.default_response))
        logger.info('handlers successfuly added')

    def send_message(self, bot, update, message, keyboard):
        logger.info('send message')
        try:
            bot.send_message(
                chat_id=update.message.from_user.id,
                text=message,
                reply_markup=keyboard,
                parse_mode=telegram.ParseMode.HTML)
        except Exception as e:
            logger.info(f'Message not sent: {e}')

    def default_response(self, bot, update):
        self.send_message(bot, update, message=f'Unknown command', keyboard=self.CURRENCY_KEYBOARD)

    def currency(self, bot, update, user_data):
        text = update.message.text
        user_data['choise']['currency'] = text
        update.message.reply_text('Now send your location to find banks near you!', reply_markup=self.LOCATION_KEYBOARD)
        return self.LOCATION

    def location(self, bot, update, user_data):
        user = update.message.from_user
        user_location = update.message.location
        user_data['choise']['location'] = user_location
        text_to_log = f'Location of {user.first_name}: {user_location.latitude} / {user_location.longitude}\n' \
                      f'Operation type "{user_data["choise"]["operation"]}"\n' \
                      f'Currency "{user_data["choise"]["currency"]}"'
        logger.info(text_to_log)
        update.message.reply_text(text_to_log)

    def done(self, bot, update):
        pass

    def operation(self, bot, update, user_data):
        text = update.message.text
        user_data['choise'] = {}
        user_data['choise']['operation'] = text
        update.message.reply_text('Now choose a currency you want to exchange', reply_markup=self.CURRENCY_KEYBOARD)
        return self.CURRENCY

    def start(self, bot, update):
        logger.info('Start command')
        user = update.message.from_user
        self.send_message(bot, update,
                          message=f'<b>Hello, {user.first_name}!</b>\n'
                                  f'Choose a type of operation', keyboard=self.OPERATIONS_KEYBOARD)
        return self.OPERATION_TYPE

    def polling(self):
        self.updater.start_polling(bootstrap_retries=-1)
        logger.info('Polling: "polling started"')
        self.updater.idle()
