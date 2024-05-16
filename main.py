import logging

from data import db_session
from data.users import User
import asyncio

from telegram.ext import (Application, MessageHandler, filters, CommandHandler, ConversationHandler, ContextTypes,
                          CallbackQueryHandler)
from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup

BOT_TOKEN = '6425799983:AAGUzo77JZPhT20_6SVFfpoD5DMcqzNE07M'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
db_session.global_init("db/data_base.db")
logger = logging.getLogger(__name__)

GREETING_STATE = 1
REGISTRATION_STATE = 2
NAME_STATE = 3
SCHEDULE_STATE = 4
SEX_STATE = 5
AGE_STATE = 6
MENU_STATE = 7
CHOICE = 8
RECOMEND = 9

chat_id = ''


async def help(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Я умею вести диалог из двух вопросов.")


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


async def start(update, context):
    global chat_id
    chat_id_1 = update.message.chat_id
    chat_id = chat_id_1
    print(chat_id)
    reply_keyboard = [['Запустить']]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "Добрый день. Данный бот поможет вам за N дней усилить защиту ваших аккаунтов, данных, а"
        " также обучит основам обеспечения цифровой гигиены. 🤖 Вам достаточно ежедневно выполнять по"
        " одной рекомендации.", reply_markup=markup)
    return GREETING_STATE


async def greeting(update, context):
    message_text = update.message.text
    if message_text == 'Запустить':
        reply_keyboard = [['Давайте поскорее начнём!']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Вы сделали уверенный шаг на пути обеспечения безопасности ваших данных. "
                                        "Пожалуйста, ответьте на несколько вопросов, и мы начнем.", reply_markup=markup)
        return REGISTRATION_STATE
    else:
        reply_keyboard = [['Запустить']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(f"Неизвестная команда [{message_text}], попробуйте еще раз", reply_markup=markup)
        return GREETING_STATE


async def registration(update, context):
    message_text = update.message.text
    if message_text == 'Давайте поскорее начнём!':
        await update.message.reply_text("Как к вам обращаться?")
        return NAME_STATE
    else:
        reply_keyboard = [['Давайте поскорее начнём!']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(f"Неизвестная команда [{message_text}], попробуйте еще раз", reply_markup=markup)
        return REGISTRATION_STATE


async def name(update, context):
    name_value = update.message.text
    if any(ch.isdigit() for ch in name_value):
        await update.message.reply_text("🫣 Не похоже на [имя/фамилию]. Попробуйте еще раз")
        return NAME_STATE
    else:
        context.user_data['name'] = name_value
        reply_keyboard = [['Ежедневно'], ['Рабочие/выходные дни']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Сформируйте удобный для вас график получения"
                                        " рекомендаций и уведомлений. Какой график для вас удобен?",
                                        reply_markup=markup)
        return SCHEDULE_STATE


async def schedule(update, context):
    days_value = update.message.text
    if days_value == "Ежедневно" or days_value == "Рабочие/выходные дни":
        context.user_data['days'] = days_value
        reply_keyboard = [['Мужской', 'Женский'], ['Пропустить']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Укажите пол.", reply_markup=markup)
        return SEX_STATE
    else:
        await update.message.reply_text("Неизвестное значение, выберите график из предложенных вариантов")
        return SCHEDULE_STATE


async def sex(update, context):
    sex_value = update.message.text
    if sex_value == "Мужской" or sex_value == "Женский" or sex_value == "Пропустить":
        if sex_value != 'Пропустить':
            context.user_data['sex'] = sex_value

        reply_keyboard = [['до 18'], ['от 18 до 25'], ['от 26 до 30', 'от 31 до 35'],
                          ['от 36 до 40', 'от 41 до 45'], ['от 46 до 55', 'старше 55']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Укажите возраст.", reply_markup=markup)
        return AGE_STATE
    else:
        await update.message.reply_text("Неизвестное значение, выберите пол из предложенных вариантов")
        return SEX_STATE


async def age(update, context):
    age_value = update.message.text
    if len(age_value.split()) != 2:
        age = age_value.split()
        context.user_data['age'] = f"{age[1]}-{age[3]}"
    else:
        age = age_value.split()
        if age[1] == '18':
            context.user_data['age'] = "0-18"
        else:
            context.user_data['age'] = "55-100"

    create_profile(context)

    reply_keyboard = [['Мой профиль', 'Рекомендации'], ['Результаты выполнения'],
                      ['Пройти тест по цифровой гигиене'], ['Пригласить друзей', 'Помощь']]

    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Меню", reply_markup=markup)

    # return MENU_STATE
    return CHOICE


def create_profile(context):
    db_sess = db_session.create_session()
    user = User()
    user.Name = context.user_data['name']
    user.Age_Group = context.user_data['age']
    user.Schedule = context.user_data['days']
    db_sess.add(user)
    db_sess.commit()


async def menu(update:Update, context:ContextTypes.DEFAULT_TYPE):

    # inline_kb_full = InlineKeyboardMarkup(row_width=2)
    # inline_profile = InlineKeyboardButton('Мой профиль', callback_data='profile')
    # inline_kb_full.add(InlineKeyboardButton('Мой профиль', url='https://www.youtube.com/watch?v=H9yVRqPixS4'))
    # inline_recommendations = InlineKeyboardButton('Рекомендации', callback_data='recommendations')
    # inline_kb_full.row(inline_recommendations)
    # inline_kb_full.add(InlineKeyboardButton('Результаты выполнения', callback_data='results'))
    # inline_kb_full.add(InlineKeyboardButton('Пройти тест по цифровой гигиене', callback_data='test'))
    # inline_invite = InlineKeyboardButton('Пригласить друзей', callback_data='invitation')
    # inline_help = InlineKeyboardButton('Помощь', callback_data='help')
    # inline_kb_full.row(inline_invite, inline_help)

    return GREETING_STATE
    # return CHOICE


async def choice(update, context):
    # reply_keyboard = [['Запустить новогодний адвент по цифровой гигиене']]
    # markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    # await update.message.reply_text("Запустить новогодний адвент", reply_markup=markup)
    if update.message.text == 'Мой профиль':
        pass
    if update.message.text == 'Рекомендации':
        reply_keyboard = [['Запустить новогодний адвент по цифровой гигиене']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Запустить новогодний адвент", reply_markup=markup)
        return RECOMEND
    if update.message.text == 'Результаты выполнения':
        pass
    if update.message.text == 'Пройти тест по цифровой гигиене':
        pass
    if update.message.text == 'Пригласить друзей':
        pass
    if update.message.text == 'Помощь':
        # Может быть тут должна быть функция /help, не знаю
        pass
async def recomend(update, context):
    inline_keyboard = [
        [InlineKeyboardButton('Отметить как выполненное', callback_data='completed')],
        [InlineKeyboardButton('Отложить выполнение', callback_data='not completed')],
        [InlineKeyboardButton('Меню', callback_data='menu')]
    ]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    await update.message.reply_text('Демонстрация рекомендации № 1. <Имя пользователя>, текст рекомендации...', reply_markup=inline_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == 'menu':
        return AGE_STATE

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CallbackQueryHandler(button))

    condition = (filters.TEXT | filters.PHOTO) & ~filters.COMMAND
    greeting_handler = MessageHandler(condition, greeting)
    registration_handler = MessageHandler(condition, registration)
    name_handler = MessageHandler(condition, name)
    schedule_handler = MessageHandler(condition, schedule)
    sex_handler = MessageHandler(condition, sex)
    age_handler = MessageHandler(condition, age)
    menu_handler = MessageHandler(condition, menu)
    choice_handler = MessageHandler(condition, choice)
    recomend_handler = MessageHandler(condition, recomend)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GREETING_STATE: [greeting_handler],
            REGISTRATION_STATE: [registration_handler],
            NAME_STATE: [name_handler],
            SCHEDULE_STATE: [schedule_handler],
            SEX_STATE: [sex_handler],
            AGE_STATE: [age_handler],
            MENU_STATE: [menu_handler],
            CHOICE: [choice_handler],
            RECOMEND: [recomend_handler]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')