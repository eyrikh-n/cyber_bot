import logging

from data import db_session
from data.users import User

from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler, ContextTypes
from telegram import ReplyKeyboardMarkup, Update

BOT_TOKEN = '6522784356:AAHB7lKSBukJDq-Tq3SAB9mxql95Cn9Dutg'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
db_session.global_init("db/data_base.db")
logger = logging.getLogger(__name__)

flag_first_event = False
GREETING_STATE = 1
REGISTRATION_STATE = 2
NAME_STATE = 3
SCHEDULE_STATE = 4
SEX_STATE = 5
AGE_STATE = 6
MENU_STATE = 7
PROFILE_STATE = 8
FIRST_EVENT = 9

async def help(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Я умею вести диалог из двух вопросов.")


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


async def start(update, context):
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
    if message_text == 'Давайте поскорее начнём!' or message_text == 'Редактировать данные':
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
        reply_keyboard = [['Ежедневно'], ['Рабочие', 'Выходные дни']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Сформируйте удобный для вас график получения"
                                        " рекомендаций и уведомлений. Какой график для вас удобен?",
                                        reply_markup=markup)
        return SCHEDULE_STATE


async def schedule(update, context):
    days_value = update.message.text
    if days_value == "Ежедневно" or days_value == "Рабочие" or days_value == "Выходные дни":
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

    create_profile(update, context)

    reply_keyboard = [['Мой профиль', 'Рекомендации'], ['Запустить новогодний адвент по цифровой гигиене'],
                      ['Результаты выполнения'],
                      ['Пройти тест по цифровой гигиене'], ['Пригласить друзей', 'Помощь']]

    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Меню", reply_markup=markup)

    return MENU_STATE


def create_profile(update, context):
    db_sess = db_session.create_session()
    user = User()
    user.Name = context.user_data['name']
    user.Age_Group = context.user_data['age']
    user.Schedule = context.user_data['days']
    user.Sex = context.user_data['sex']
    user.UserName = str(update.message.from_user.username)
    user.Chat_Id = str(update.message.chat.id)
    db_sess.add(user)
    db_sess.commit()


async def menu(update:Update, context:ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    global flag_first_event

    if message_text == 'Запустить новогодний адвент по цифровой гигиене':
        db_sess = db_session.create_session()
        username = str(update.message.from_user.username)
        user = db_sess.query(User).filter(User.UserName == username).first()
        name = user.Name

        flag_first_event = True
        reply_keyboard = [['Отметить как выполненное', 'Отложить'], ['Меню']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(f"{name} <Рекомендация 1*>", reply_markup=markup)
        return FIRST_EVENT

    elif message_text == 'Мой профиль':

        reply_keyboard = [['Редактировать данные'], ['Меню']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

        db_sess = db_session.create_session()
        username = str(update.message.from_user.username)
        user = db_sess.query(User).filter(User.UserName == username).first()
        name = user.Name
        age_Group = user.Age_Group
        schedule = user.Schedule
        sex = user.Sex
        if sex == 'Пропустить':
            await update.message.reply_text("Профиль 🔽 \n"
                f"💠 Имя - {name} \n"
                f"💠 График - {schedule} \n"
                f"💠 Возраст - {age_Group} лет", reply_markup=markup)
            return PROFILE_STATE
        else:
            await update.message.reply_text("Профиль 🔽 \n"
                f"💠 Имя - {name} \n"
                f"💠 График - {schedule} \n"
                f"💠 Возраст - {age_Group} лет \n"
                f"💠 Пол {sex}", reply_markup=markup)
            return PROFILE_STATE
    else:
        if not flag_first_event:
            reply_keyboard = [['Мой профиль', 'Рекомендации'], ['Запустить новогодний адвент по цифровой гигиене'],
                              ['Результаты выполнения'],
                              ['Пройти тест по цифровой гигиене'], ['Пригласить друзей', 'Помощь']]
        else:
            reply_keyboard = [['Мой профиль', 'Рекомендации'], ['Результаты выполнения'],
                              ['Пройти тест по цифровой гигиене'], ['Пригласить друзей', 'Помощь']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(f"Неизвестная команда [{message_text}], попробуйте еще раз", reply_markup=markup)
        return MENU_STATE


async def profile(update, context):
    message_text = update.message.text

    if message_text == 'Редактировать данные':
        await update.message.reply_text("Как к вам обращаться?")
        return NAME_STATE
    if message_text == 'Меню':
        if not flag_first_event:
            reply_keyboard = [['Мой профиль', 'Рекомендации'], ['Запустить новогодний адвент по цифровой гигиене'],
                              ['Результаты выполнения'],
                              ['Пройти тест по цифровой гигиене'], ['Пригласить друзей', 'Помощь']]
        else:
            reply_keyboard = [['Мой профиль', 'Рекомендации'], ['Результаты выполнения'],
                              ['Пройти тест по цифровой гигиене'], ['Пригласить друзей', 'Помощь']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text("Меню", reply_markup=markup)
        return MENU_STATE
    else:
        reply_keyboard = [['Редактировать данные'], ['Меню']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(f"Неизвестная команда [{message_text}], попробуйте еще раз",
                                        reply_markup=markup)
        return PROFILE_STATE


async def first_event(update, conrext):
    message_text = update.message.text
    reply_keyboard = [['Мой профиль', 'Рекомендации'], ['Результаты выполнения'],
                      ['Пройти тест по цифровой гигиене'], ['Пригласить друзей', 'Помощь']]

    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

    if message_text == 'Отметить как выполненное':
        pass
    if message_text == 'Отложить':
        pass
    if message_text == 'Меню':
        await update.message.reply_text(f"Меню",
                                        reply_markup=markup)
        return MENU_STATE
    else:
        await update.message.reply_text(f"Неизвестная команда [{message_text}], попробуйте еще раз",
                                        reply_markup=markup)
        return MENU_STATE


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("help", help))

    condition = (filters.TEXT | filters.PHOTO) & ~filters.COMMAND
    greeting_handler = MessageHandler(condition, greeting)
    registration_handler = MessageHandler(condition, registration)
    name_handler = MessageHandler(condition, name)
    schedule_handler = MessageHandler(condition, schedule)
    sex_handler = MessageHandler(condition, sex)
    age_handler = MessageHandler(condition, age)
    menu_handler = MessageHandler(condition, menu)
    profile_handler = MessageHandler(condition, profile)
    first_event_handler = MessageHandler(condition, first_event)

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
            PROFILE_STATE: [profile_handler],
            FIRST_EVENT: [first_event_handler]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()