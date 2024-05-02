import logging
from data import db_session
from data.users import User
import aiohttp
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup

BOT_TOKEN = '6522784356:AAHB7lKSBukJDq-Tq3SAB9mxql95Cn9Dutg'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
db_session.global_init("db/data_base.db")
logger = logging.getLogger(__name__)


async def help(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Я умею вести диалог из двух вопросов.")


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


async def start(update, context):
    reply_keyboard = [['Запустить']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Добрый день. Данный бот поможет вам за N дней усилить защиту ваших аккаунтов, данных, а"
        " также обучит основам обеспечения цифровой гигиены. Вам достаточно ежедневно выполнять по"
        " одной рекомендации.", reply_markup=markup)
    return 1


async def day(update, context):
    name = update.message.text
    if any(ch.isdigit() for ch in name):
        return 6
    else:
        context.user_data['name'] = update.message.text
        reply_keyboard = [['Ежедневно'], ['Рабочие/выходные дни']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Сформируйте удобный для вас график получения"
                                        " рекомендаций и уведомлений. Какой график для вас удобен?", reply_markup=markup)
        return 3


async def error_name(update, context):
    await update.message.reply_text("Не похоже на [имя/фамилию]. Попробуйте еще раз")
    return 2


async def sex(update, context):
    context.user_data['days'] = update.message.text
    reply_keyboard = [['Мужской', 'Женский'], ['Пропустить']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Укажите пол.", reply_markup=markup)
    return 4


async def age(update, context):
    if update.message.text != 'Пропустить':
        context.user_data['sex'] = update.message.text
    else:
        context.user_data['sex'] = 'Не указан'
    reply_keyboard = [['до 18'], ['от 18 до 25'], ['от 26 до 30', 'от 31 до 35'],
                      ['от 36 до 40', 'от 41 до 45'], ['от 46 до 55', 'старше 55']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Укажите возраст.", reply_markup=markup)
    return 5


async def menu(update, context):
    if len(update.message.text.split()) != 2:
        age = update.message.text.split()
        context.user_data['age'] = f"{age[1]}-{age[3]}"
    else:
        age = update.message.text.split()
        if age[1] == '18':
            context.user_data['age'] = "0-18"
        else:
            context.user_data['age'] = "55-100"
    db_sess = db_session.create_session()
    user = User()
    user.Name = context.user_data['name']
    user.Age_Group = context.user_data['age']
    user.Recommendation = context.user_data['days']
    db_sess.add(user)
    db_sess.commit()
    # markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    # await update.message.reply_text("Укажите возраст.", reply_markup=markup)
    # return 6


async def greating(update, context):
    context.user_data['state'] = update.message.text

    if context.user_data['state'] == 'Запустить':
        reply_keyboard = [['Давайте поскорее начнём!']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Вы сделали уверенный шаг на пути обеспечения безопасности ваших данных. "
                                        "Пожалуйста, ответьте на несколько вопросов, и мы начнем.", reply_markup=markup)
        return 1

    if context.user_data['state'] == 'Давайте поскорее начнём!':
        await update.message.reply_text("Как к вам обращаться?")
        name = update.message.text
        if any(ch.isdigit() for ch in name):
            return 6
        else:
            return 2


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("help", help))

    condition = (filters.TEXT | filters.PHOTO) & ~filters.COMMAND
    handler_1 = MessageHandler(condition, greating)
    handler_2 = MessageHandler(condition, day)
    handler_3 = MessageHandler(condition, sex)
    handler_4 = MessageHandler(condition, age)
    handler_5 = MessageHandler(condition, menu)
    handler_6 = MessageHandler(condition, error_name)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [handler_1],
            2: [handler_2],
            3: [handler_3],
            4: [handler_4],
            5: [handler_5],
            6: [handler_6]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()