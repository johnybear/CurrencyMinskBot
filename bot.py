import telegram
from telegram.ext import CommandHandler, Updater, RegexHandler, MessageHandler, ConversationHandler, Filters
import logging
from currency_parser import currency_response

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('bot')


class FindBankBot:
    START_COMMAND = 'start'
    CURRENCIES = ['USD', 'EUR', 'RUB']
    OPERATIONS = ['Банки продают', 'Банки покупают']
    SEND_LOCATION_MESSAGE = 'Вышлите местоположение'
    RESTART_TEXT = 'Сбросить все и начать сначала'

    CURRENCIES_BUTTONS = [telegram.KeyboardButton(text=currency, callback_data=currency) for currency in CURRENCIES]
    OPERATIONS_BUTTONS = [telegram.KeyboardButton(text=operation, callback_data=operation) for operation in OPERATIONS]
    LOCATION_BUTTON = telegram.KeyboardButton(text=SEND_LOCATION_MESSAGE, request_location=True)
    RESTART_BUTTON = telegram.KeyboardButton(text=RESTART_TEXT, callback_data=RESTART_TEXT)

    CURRENCY_KEYBOARD = telegram.ReplyKeyboardMarkup(
        [[button for button in CURRENCIES_BUTTONS], [RESTART_BUTTON]], resize_keyboard=True,)
    OPERATIONS_KEYBOARD = telegram.ReplyKeyboardMarkup(
        [[button for button in OPERATIONS_BUTTONS], [RESTART_BUTTON]], resize_keyboard=True,)
    LOCATION_KEYBOARD = telegram.ReplyKeyboardMarkup(
        [[LOCATION_BUTTON], [RESTART_BUTTON]], resize_keyboard=True,)

    OPERATION_TYPE, CURRENCY, LOCATION = range(3)

    def __init__(self):
        self.updater = Updater(token='***', workers=1000)
        self.dispatcher = self.updater.dispatcher
        self.__add_handlers()

    def __add_handlers(self):
        logger.info('add handlers')
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler(self.START_COMMAND, self.start),
            			  RegexHandler('', self.start)],

            states={
                self.OPERATION_TYPE: [RegexHandler('^(Банки продают|Банки покупают)$', self.operation, pass_user_data=True),
                    				  RegexHandler('^('+self.RESTART_TEXT+')$', self.start),
	                                  RegexHandler('', self.default_response)],

                self.CURRENCY: [RegexHandler('^(USD|EUR|RUB)$', self.currency, pass_user_data=True),
                                RegexHandler('^('+self.RESTART_TEXT+')$', self.start),
                                RegexHandler('', self.default_response)],

                self.LOCATION: [MessageHandler(Filters.location, self.location, pass_user_data=True), 
                                RegexHandler('^('+self.RESTART_TEXT+')$', self.start),
                                RegexHandler('', self.default_response)],

            },

            fallbacks=[RegexHandler('^Show$', self.done, pass_user_data=True)]
        )
        self.dispatcher.add_handler(conv_handler)
        #self.dispatcher.add_handler(RegexHandler('', self.default_response))
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
            logger.info('Message not sent: %s' % e)

    def default_response(self, bot, update):
        self.send_message(
            bot, 
            update, 
            message='Небольшой сбой в работе.',
            keyboard=self.OPERATION_TYPE)
        return self.OPERATION_TYPE
 

    def currency(self, bot, update, user_data):
        text = update.message.text
        user_data['choise']['currency'] = text
        update.message.reply_text(
            'Теперь вышлите свое местоположение, чтоб найти ближайшие к вам обменники! GPS должен быть включен', 
            reply_markup=self.LOCATION_KEYBOARD)
        return self.LOCATION

    def location(self, bot, update, user_data):
        user = update.message.from_user
        text = update.message.text
        user_location = update.message.location
        user_data['choise']['user_location'] = user_location
        # text_to_log = f'Location of {user.first_name}: {user_location.latitude} / {user_location.longitude}\n' \
        #               f'Operation type "{user_data["choise"]["operation"]}"\n' \
        #               f'Currency "{user_data["choise"]["currency"]}"'
        response = currency_response(**user_data['choise'])
        #logger.info(text_to_log)
        update.message.reply_text(response, reply_markup=self.OPERATIONS_KEYBOARD)
        return self.OPERATION_TYPE

    def done(self, bot, update):
        pass

    def operation(self, bot, update, user_data):
        operation_dict = {'Банки продают':"sell", 'Банки покупают':"buy"}
        text = update.message.text
        user_data['choise'] = {}
        user_data['choise']['operation'] = operation_dict[text]
        update.message.reply_text('Выберите валюту, которую хотели бы поменять.', reply_markup=self.CURRENCY_KEYBOARD)
        return self.CURRENCY

    def start(self, bot, update):
        logger.info('Start command')
        user = update.message.from_user
        self.send_message(bot, update,
                          message='<b>Здравствуйте, %s!</b>\n Выберите тип операции' % user.first_name, 
                          keyboard=self.OPERATIONS_KEYBOARD)
        return self.OPERATION_TYPE

    def polling(self):
        self.updater.start_polling(bootstrap_retries=-1)
        logger.info('Polling: "polling started"')
        self.updater.idle()
