import logging
import os
import threading
from datetime import datetime, timedelta, time
from typing import Optional

from flask import Flask
import pytz
from sqlalchemy import func, join
import telegram
from data import db_session
from data.users import User
from data.recommendations import Recommendation
from data.status_recommendation import Status_recommendation
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler, CallbackContext, \
    CallbackQueryHandler, ContextTypes
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, Update

web = Flask(__name__)

BOT_TOKEN = os.environ.get('API_BOT_TOKEN', '6522784356:AAHB7lKSBukJDq-Tq3SAB9mxql95Cn9Dutg')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
bot = telegram.Bot(token=BOT_TOKEN)
bot_url = os.environ.get('BOT_URL', 'https://t.me/Cyber_safeness_bot')
db_session.global_init()
logger = logging.getLogger(__name__)

(GREETING_STATE, REGISTRATION_STATE, NAME_STATE, SCHEDULE_STATE, SEX_STATE,
 AGE_STATE, TIME_STATE, TIMEZONE_STATE, PERIOD_STATE) = range(9)

PROFILE_SHOW_STATE, PROFILE_EDIT_STATE, PROFILE_EDIT_FIELD_STATE, PROFILE_EDIT_APPLY_STATE = range(4)
ADVENT_TIMER_STATE, ADVENT_WORK_STATE = range(2)
RESULTS_SHOW, RESULTS_REC_NUM, RESULTS_CHANGE = range(3)

BUTTON_REC_DONE, BUTTON_REC_SKIP, BUTTON_REC_REPORT, BUTTON_REC_SHARE, BUTTON_RUN_TEST = ("button_rec_done",
                                                                                          "button_rec_skip",
                                                                                          "button_rec_report",
                                                                                          "button_rec_share",
                                                                                          "button_run_test")

REC_STATUS_INIT, REC_STATUS_DONE, REC_STATUS_SKIP = '0', '1', '2'


@web.route("/health")
def health():
    return '{"Up!"}'


async def get_timezone_by_utc_offset(utc_offset: timedelta) -> str:
    current_utc_time = datetime.now(pytz.utc)
    for tz in map(pytz.timezone, pytz.all_timezones_set):
        if current_utc_time.astimezone(tz).utcoffset() == utc_offset:
            return tz.zone
    return ""


async def help_message(update, context):
    user = await find_user_by_chat_id(update.message.chat.id)
    if user is None:
        advent_start = None
    else:
        advent_start = user.Advent_Start

    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Этот чат-бот предназначен для повышения уровня знаний цифровой гигиены и помощи "
                                    "в усилении безопасности существующих аккаунтов и чувствительных данных.\n\n"
                                    "Доступные команды:\n\n"
                                    "/start - регистрация;\n"
                                    "/stop - остановка бота;\n"
                                    "/menu - основное меню;\n"
                                    "/help - показать справку.\n\n"
                                    "После регистрации вам будет доступно меню, благодаря которому вы можете общаться "
                                    "с ботом. Чтобы изменить данные, заданные по регистрации, можно перейти по кнопке "
                                    "Мой профиль и далее в *Редактировать данные* и поменять нужный параметр.\n\n"
                                    "Чтобы запустить рассылку рекомендаций, нужно нажать на кнопку *Запустить новогодний"
                                    " адвент* по цифровой гигиене. После нажатия вам будут подаваться рекомендации в "
                                    "зависимости от выбранного графика(ежедневно, рабочие, выходные дни).\n\n"
                                    "Вам следует выполнять наши рекомендации и отмечать это в боте (по кнопке *выполнить* "
                                    "или *отложить*). Также вы можете посмотреть выданные рекомендации по кнопке "
                                    "Рекомендации и изменить статус их выполнения в *Результаты выполнения*.\n\n"
                                    "Кнопка *Пригласить друзей* поможет вам сделать ваших друзей более грамотными в "
                                    "цифровой среде и поделиться с ними ссылкой на нашего бота. Чтобы проверить свои "
                                    "знания, можно пройти тест по кнопке *Пройти тест по цифровой гигиене*.",
                                    reply_markup=build_main_menu(advent_start), parse_mode='markdown')


async def stop(update, context):
    await update.message.reply_text("Всего доброго!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def init_recommendations():
    db_sess = db_session.create_session()
    rec_count = db_sess.query(Recommendation).count()
    if rec_count > 0:
        return

    db_sess.add(Recommendation(recommendation='Установите обновление ПО на своём устройстве'))
    db_sess.add(Recommendation(recommendation='Обновите пароли от аккаунтов социальных сетей'))
    db_sess.add(Recommendation(recommendation='Отключите автоматическое подключение к Bluetooth и Wi-Fi'))
    db_sess.add(Recommendation(recommendation='Зашифруйте свои персональные данные'))
    db_sess.add(Recommendation(recommendation='Подключите двухфакторную аутентификацию для своих аккаунтов'))
    db_sess.add(Recommendation(recommendation='Проверьте наличие несанкционированных приложений на своём устройств'))
    db_sess.add(Recommendation(recommendation='Сделайте резервное копирование чатов в любом мессенджере'))
    db_sess.add(Recommendation(recommendation='Ограничьте разрешения любого приложения на устройстве'))
    db_sess.add(Recommendation(recommendation='Поставьте надёжный пароль на телефон'))
    db_sess.add(Recommendation(recommendation='Включите дистанционнное удаление данных с телефона'))
    db_sess.add(Recommendation(recommendation='Установите антивирусное ПО на всех своих устройствах'))
    db_sess.add(Recommendation(recommendation='Проверьте любую компанию на наличие сертификата кибезопасности'))
    db_sess.add(Recommendation(recommendation='Ограничьте доступ к вашим страницам в социальных сетях'))
    db_sess.add(Recommendation(recommendation='Установите вход по отпечатку пальца для ваших устройств'))
    db_sess.add(Recommendation(recommendation='Зарегистрируйтесь на сайте, прочитав политику конфиденциальности'))
    db_sess.add(Recommendation(recommendation='Обновите антивирусное ПО на вашем устройстве'))
    db_sess.add(Recommendation(recommendation='Сделайте резервное копирование данных вашего устройства'))
    db_sess.add(Recommendation(recommendation='"Почистите" список друзей в любой социальной сети'))
    db_sess.add(Recommendation(recommendation='Смените пароль вашей электронной почты'))
    db_sess.add(Recommendation(recommendation='"Почистите" электронный ящик от ненужных или подозрительных писем'))
    db_sess.add(Recommendation(recommendation='Выйдите с аккаунта в социальной сети со всех устройств, кроме своего'))
    db_sess.add(Recommendation(
        recommendation='Заблокируйте подозрительные аккауты, которые оставили заявку в друзья, в любом мессенджере или социальной сети'))
    db_sess.add(
        Recommendation(recommendation='Очистите чаты мессенджера от ненужной информации или просто удалите чат'))
    db_sess.add(Recommendation(
        recommendation='Обновите приложение мессенджера (если имеется), так как оно может содержать улучшение в области безопасности'))
    db_sess.add(Recommendation(recommendation='Проверьте вкладку "Спам" вашего электронного ящика'))
    db_sess.add(Recommendation(recommendation='Проведите разбор файлов вашего электронного диска и удалите ненужное'))
    db_sess.add(Recommendation(recommendation='Отключите геолокацию на вашем устройстве'))
    db_sess.add(Recommendation(recommendation='Удалите неиспользуемые аккаунты'))
    db_sess.add(
        Recommendation(recommendation='Удалите подозрительные или неиспользуемые приложения на вашем устройстве'))
    db_sess.add(Recommendation(recommendation='Заблокируте подозрительные чаты, предлагающие работу и т.д.'))
    db_sess.commit()
    db_sess.close()


# Получить пользователя по идентификатору чата
async def find_user_by_chat_id(chat_id: str) -> Optional[User]:
    db_sess = db_session.create_session()
    result = db_sess.query(User).filter(User.Chat_Id == str(chat_id)).first()
    db_sess.close()
    return result


# Получить пользователя по идентификатору пользователя
async def find_user_by_id(user_id: str) -> Optional[User]:
    db_sess = db_session.create_session()
    result = db_sess.query(User).filter(User.User_ID == user_id).first()
    db_sess.close()
    return result


def build_job_rec_name(user_id: str) -> str:
    return f"rec_{user_id}"


def build_job_not_name(user_id: str) -> str:
    return f"not_{user_id}"


# Количество рекомендаций в адвенте
async def get_recommendation_count() -> int:
    db_sess = db_session.create_session()
    recommendations_count = db_sess.query(Recommendation).count()
    db_sess.close()
    return recommendations_count


# Получить описание рекомендации по ID
async def get_recommendation_info_by_id(rec_id: int) -> Optional[Recommendation]:
    db_sess = db_session.create_session()
    rec = db_sess.query(Recommendation).filter(Recommendation.id == rec_id).first()
    db_sess.close()
    return rec


# Все ли рекомендации отправлены пользователю
async def is_all_recommendation_sent(user_id: str) -> bool:
    # Определяем количество рекомендаций, которые в принципе нужно было отправить
    recommendations_count = await get_recommendation_count()
    sent_recommendations_count = await sent_recommendation_count(user_id)
    return sent_recommendations_count >= recommendations_count


# Количество отправленных рекомендаций пользователю
async def sent_recommendation_count(user_id: str) -> int:
    db_sess = db_session.create_session()
    sent_recommendations_count = (db_sess.query(Status_recommendation)
                                  .filter(Status_recommendation.user_id == user_id)
                                  .count()
                                  )
    db_sess.close()
    return sent_recommendations_count


# Выполнил ли пользователь адвент
async def is_advent_completed(user_id: str) -> bool:
    # Определяем количество рекомендаций, которые в принципе нужно было отправить
    recommendations_count = await get_recommendation_count()

    db_sess = db_session.create_session()
    completed_recommendations_count = (db_sess.query(Status_recommendation)
                                       .filter(Status_recommendation.user_id == user_id,
                                               Status_recommendation.rec_status == REC_STATUS_DONE)
                                       .count()
                                       )
    db_sess.close()
    return completed_recommendations_count >= recommendations_count


async def skip_rec(context, user_id, rec_id):
    user = await find_user_by_id(user_id)
    if user is None:
        return

    db_sess = db_session.create_session()
    # Находим рекомендацию в базе, которую нужно отложить
    rec = (db_sess.query(Status_recommendation).
           filter(Status_recommendation.user_id == user.User_ID, Status_recommendation.rec_id == rec_id).
           first())
    db_sess.close()

    if rec is None:
        return
    elif rec.rec_status != REC_STATUS_INIT:
        return

    # Удаляем сообщение с рекомендацией из чата
    if rec.message_id != "":
        await context.bot.delete_message(chat_id=user.Chat_Id, message_id=rec.message_id)

    # Откладываем рекомендацию, меняя статус и затираем идентификатор сообщения (т.к. оно было удалено)
    rec.rec_status = REC_STATUS_SKIP
    rec.message_id = ""

    db_sess = db_session.create_session()
    db_sess.add(rec)
    db_sess.commit()
    db_sess.close()


async def start(update, context):
    chat_id = str(update.message.chat.id)
    user = await find_user_by_chat_id(chat_id)
    if user is None:
        reply_keyboard = [['Запустить']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await bot.send_photo(chat_id=chat_id,
                             photo='https://img.freepik.com/free-vector/flat-background-for-safer-internet-day_23-2151127509.jpg?w=2000&t=st=1717694697~exp=1717695297~hmac=edd5b2ffe89d8b2901334e3df3190bffc0ed426ca69706be691a573487acdd33',
                             caption="Добрый день. Данный бот поможет вам за N дней усилить защиту ваших аккаунтов, данных,"
                                     " а также обучит основам обеспечения цифровой гигиены. 🤖 Вам достаточно ежедневно"
                                     " выполнять по одной рекомендации.",
                             reply_markup=markup)
        return GREETING_STATE
    else:
        await bot.send_photo(chat_id=chat_id,
                             photo='https://img.freepik.com/free-vector/technical-support-service-site_80328-68.jpg?t=st=1717695596~exp=1717699196~hmac=419f0dc67a3bb3e7fecfe47e9e64615daaee5692bdb3c828e3c2dae5265d1376&w=2000',
                             caption=f"Добрый день, {user.Name}, давно не виделись! Воспользуйтесь меню.",
                             reply_markup=build_main_menu(user.Advent_Start))
        return ConversationHandler.END


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
        await update.message.reply_text(f"Неизвестная команда [{message_text}], попробуйте еще раз",
                                        reply_markup=markup)
        return GREETING_STATE


async def registration(update, context):
    message_text = update.message.text
    if message_text == 'Давайте поскорее начнём!' or message_text == 'Редактировать данные':
        await update.message.reply_text("Как к вам обращаться?")
        return NAME_STATE
    else:
        reply_keyboard = [['Давайте поскорее начнём!']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(f"Неизвестная команда [{message_text}], попробуйте еще раз",
                                        reply_markup=markup)
        return REGISTRATION_STATE


async def name(update, context):
    name_value = update.message.text
    if any(ch.isdigit() for ch in name_value):
        await update.message.reply_text("🫣 Не похоже на [имя/фамилию]. Попробуйте еще раз")
        return NAME_STATE
    else:
        context.user_data['name'] = name_value
        reply_keyboard = [['Ежедневно'], ['Рабочие дни', 'Выходные дни']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Сформируйте удобный для вас график получения"
                                        " рекомендаций и уведомлений. Какой график для вас удобен?",
                                        reply_markup=markup)
        return SCHEDULE_STATE


async def schedule(update, context):
    days_value = update.message.text
    if days_value == "Ежедневно" or days_value == "Рабочие дни" or days_value == "Выходные дни":
        context.user_data['days'] = days_value
        await update.message.reply_text(
            "Укажите время в часах(от 0 до 23), в которое вы хотите получать рекомендации ⌚")
        return TIME_STATE
    else:
        await update.message.reply_text("Неизвестное значение, выберите график из предложенных вариантов")
        return SCHEDULE_STATE


async def time_schedule(update, context):
    time_value = update.message.text
    if time_value.isdigit():
        if 0 <= int(time_value) <= 23:
            context.user_data['time'] = f'{time_value}:00'
            await update.message.reply_text("Укажите интервал, в который вам будут присылаться напоминания "
                                            "о прохождении рекомендаций в днях. Например: каждые 2 дня.")
            return PERIOD_STATE
        else:
            await update.message.reply_text("В сутках только 24 часа 😝, попробуйте ещё раз")
            return TIME_STATE
    else:
        await update.message.reply_text("Значение, которое вы ввели не является числом 😜, попробуйте ещё раз")
        return TIME_STATE


async def period(update, context):
    period_value = update.message.text
    if period_value.isdigit():
        if 1 <= int(period_value) <= 30:
            context.user_data['period'] = str(period_value)
            await update.message.reply_text("Укажите разницу по времени вашего региона относительно Москвы "
                                            "(в часах, начиная с + или -). "
                                            "Например, для Новосибирска: +4, для Калининграда: -1")
            return TIMEZONE_STATE
        else:
            await update.message.reply_text("Вы указали слишком большой или маленький диапазон. Попробуйте ещё раз.")
            return PERIOD_STATE
    else:
        await update.message.reply_text("Значение, которое вы ввели не является числом 😜, попробуйте ещё раз")
        return PERIOD_STATE


async def timezone_schedule(update, context):
    if update.message.text[0] != "+" and update.message.text[0] != "-":
        await update.message.reply_text("Разница во времени должна начинаться либо с +, либо с -. Попробуйте еще раз.")
        return TIMEZONE_STATE

    if update.message.text[1:].isdigit():
        moscow_offset_value = update.message.text.replace("+", "")
        utc_offset_hours = timedelta(hours=3 + int(moscow_offset_value))
        user_timezone = await get_timezone_by_utc_offset(utc_offset_hours)
        if user_timezone == "":
            await update.message.reply_text(f"Не удалось определить часовой пояс по МСК{update.message.text}, "
                                            f"попробуйте еще раз ввести разницу по часам с Москвой.")
            return TIMEZONE_STATE
        else:
            context.user_data['timezone'] = user_timezone

            reply_keyboard = [['Мужской', 'Женский'], ['Пропустить']]
            markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text("Укажите пол", reply_markup=markup)
            return SEX_STATE
    else:
        await update.message.reply_text("Значение, которое вы ввели не является числом 😜, попробуйте ещё раз")
        return TIMEZONE_STATE


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

    await update.message.reply_text("Меню", reply_markup=build_main_menu())
    return ConversationHandler.END


def create_profile(update, context):
    user = User()
    user.Name = context.user_data['name']
    user.Age_Group = context.user_data['age']
    user.Schedule = context.user_data['days']
    user.Sex = context.user_data['sex']
    user.UserName = str(update.message.from_user.username)
    user.Chat_Id = str(update.message.chat.id)
    user.Time = context.user_data['time']
    user.Timezone = context.user_data['timezone']
    user.Period = str(context.user_data['period'])

    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()
    db_sess.close()


def build_main_menu(advent_start: Optional[datetime] = None) -> ReplyKeyboardMarkup:
    reply_keyboard = [['Мой профиль', 'Рекомендации']]
    if advent_start is None:
        # Кнопку запуска адвента показываем только, если пользователь не запустил ранее адвент
        reply_keyboard.append(['Запустить новогодний адвент по цифровой гигиене'])

    reply_keyboard.extend([
        ['Результаты выполнения'],
        ['Пройти тест по цифровой гигиене'],
        ['Пригласить друзей', 'Помощь']])

    return ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)


async def show_main_menu(update, context):
    user = await find_user_by_chat_id(update.message.chat.id)
    if user is None:
        await update.message.reply_text("Для отображения основного меню необходимо предварительно "
                                        "зарегистрироваться, воспользуйтесь командой /start",
                                        reply_markup=ReplyKeyboardRemove())
        return

    await update.message.reply_text("Меню", reply_markup=build_main_menu(user.Advent_Start))
    return ConversationHandler.END


async def show_profile(update, context):
    reply_keyboard = [['Редактировать данные'], ['Меню']]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

    user = await find_user_by_chat_id(update.message.chat.id)
    reply_text = ("Профиль 🔽 \n"
                  f"💠 Имя - {user.Name} \n"
                  f"💠 График - {user.Schedule} \n"
                  f"💠 Возраст - {user.Age_Group} лет \n"
                  f"💠 Время выдачи рекомендаций - {user.Time} \n")
    if user.Sex != 'Пропустить':
        reply_text = reply_text + f"💠 Пол - {user.Sex}"

    await update.message.reply_text(reply_text, reply_markup=markup)
    return PROFILE_EDIT_STATE


async def edit_profile(update, context):
    user = await find_user_by_chat_id(update.message.chat.id)
    if user is None:
        return PROFILE_EDIT_STATE

    db_sess = db_session.create_session()
    sent_recommendations = db_sess.query(Status_recommendation).filter(
        Status_recommendation.user_id == user.User_ID).all()
    db_sess.close()

    if len(sent_recommendations) == 0:
        reply_keyboard = [['Имя', 'Возраст', 'Пол', 'График', 'Время'], ["Период напоминаний", 'Назад']]
    else:
        reply_keyboard = [['Имя', 'Возраст', 'Пол', "Период напоминаний"], ['Назад']]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text("Что отредактировать?", reply_markup=markup)
    return PROFILE_EDIT_FIELD_STATE


async def edit_profile_request(update, context):
    message_text = update.message.text
    context.user_data["edit_profile_request"] = message_text
    if message_text == "Имя":
        await update.message.reply_text("Введите новое имя")
    elif message_text == "Возраст":
        reply_keyboard = [['до 18'], ['от 18 до 25'], ['от 26 до 30', 'от 31 до 35'],
                          ['от 36 до 40', 'от 41 до 45'], ['от 46 до 55', 'старше 55']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Введите новый возраст", reply_markup=markup)
    elif message_text == "Пол":
        reply_keyboard = [['Мужской', 'Женский'], ['Пропустить']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Укажите новый пол", reply_markup=markup)
    elif message_text == "График":
        reply_keyboard = [['Ежедневно'], ['Рабочие', 'Выходные дни']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Сформируйте удобный для вас график получения"
                                        " рекомендаций и уведомлений. Какой график для вас удобен?",
                                        reply_markup=markup)
    elif message_text == "График":
        reply_keyboard = [['Ежедневно'], ['Рабочие', 'Выходные дни']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Сформируйте удобный для вас график получения"
                                        " рекомендаций и уведомлений. Какой график для вас удобен?",
                                        reply_markup=markup)
    elif message_text == "Время":
        await update.message.reply_text(
            "Укажите время в часах(от 0 до 23), в которое вы хотите получать рекомендации ⌚")
    elif message_text == "Период напоминаний":
        await update.message.reply_text("Укажите интервал, в который вам будут присылаться напоминания "
                                        "о прохождении рекомендаций в днях. Например: каждые 2 дня.")
    return PROFILE_EDIT_APPLY_STATE


async def edit_profile_apply(update, context):
    message_text = update.message.text
    request_type = context.user_data["edit_profile_request"]

    if request_type == "Имя":
        if any(ch.isdigit() for ch in message_text):
            await update.message.reply_text("🫣 Не похоже на [имя/фамилию]. Попробуйте еще раз")
            return PROFILE_EDIT_APPLY_STATE
        context.user_data['name'] = message_text
    elif request_type == "Возраст":
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
    elif request_type == "Пол":
        if message_text == "Мужской" or message_text == "Женский" or message_text == "Пропустить":
            context.user_data['sex'] = message_text
        else:
            await update.message.reply_text("Выберите один из доступных вариантов")
            return PROFILE_EDIT_APPLY_STATE
    elif request_type == "График":
        if message_text == "Ежедневно" or message_text == "Рабочие" or message_text == "Выходные дни":
            context.user_data['days'] = message_text
        else:
            await update.message.reply_text("Выберите один из доступных вариантов")
            return PROFILE_EDIT_APPLY_STATE
    elif request_type == "Время":
        if message_text.isdigit():
            if 0 <= int(message_text) <= 23:
                context.user_data['time'] = f'{message_text}:00'
            else:
                await update.message.reply_text("В сутках только 24 часа 😝, попробуйте ещё раз")
                return PROFILE_EDIT_APPLY_STATE
        else:
            await update.message.reply_text("Значение, которое вы ввели не является числом 😜, попробуйте ещё раз")
            return PROFILE_EDIT_APPLY_STATE
    elif request_type == "Период напоминаний":
        if message_text.isdigit():
            if 1 <= int(message_text) <= 30:
                context.user_data['period'] = str(message_text)
            else:
                await update.message.reply_text("Вы выбрали слишком большой или маленький период. Попробуйте ещё раз.")
                return PROFILE_EDIT_APPLY_STATE
        else:
            await update.message.reply_text("Значение, которое вы ввели не является числом 😜, попробуйте ещё раз")
            return PROFILE_EDIT_APPLY_STATE

    user = await find_user_by_chat_id(update.message.chat.id)

    user.Name = context.user_data.get('name', user.Name)
    user.Age_Group = context.user_data.get('age', user.Age_Group)
    user.Schedule = context.user_data.get('days', user.Schedule)
    user.Sex = context.user_data.get('sex', user.Sex)
    user.Time = context.user_data.get('time', user.Time)
    user.Period = context.user_data.get('period', user.Period)

    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()
    db_sess.close()

    reply_keyboard = [['Показать профиль', 'Меню']]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text("Изменения профиля успешно применены!", reply_markup=markup)
    return PROFILE_SHOW_STATE


async def send_recommendation(context):
    # Выполняем поиск пользователя по идентификатору чата
    user = await find_user_by_chat_id(context.job.chat_id)
    # Если пользователь не найден, то адвент прекращается - выход
    if user is None:
        await context.bot.send_message(chat_id=context.job.chat_id,
                                       text='Такой пользователь не найден, воспользуйтесь командой /start')
        context.job.schedule_removal()
        return

    db_sess = db_session.create_session()
    # Определяем количество рекомендаций, которые в принципе нужно было отправить
    recommendations_count = await get_recommendation_count()

    # Получаем все ранее отправленные рекомендации этому пользователю
    sent_recommendations = (db_sess.query(Status_recommendation)
                            .filter(Status_recommendation.user_id == user.User_ID)
                            .order_by(Status_recommendation.rec_id).all()
                            )
    db_sess.close()

    # Если ранее уже отправлялись рекомендации, то определяем последнюю отправленную, иначе используем первую
    if len(sent_recommendations) != 0:
        last_rec = sent_recommendations[-1]
        new_req_id = last_rec.rec_id + 1
    else:
        last_rec = None
        new_req_id = 1

    # Если все рекомендации уже были отправлены ранее, то завершаем адвент - выход
    if new_req_id > recommendations_count:
        await context.bot.send_message(chat_id=user.Chat_Id, text=f'Вы получили все рекомендации!',
                                       reply_markup=build_main_menu(user.Advent_Start))
        context.job.schedule_removal()
        return

    # Получаем текст очередной рекомендации и отправляем ее пользователю
    rec_new = await get_recommendation_info_by_id(new_req_id)
    if rec_new is None:
        return

    keyboard = [
        [
            InlineKeyboardButton("Выполнить", callback_data=f"{BUTTON_REC_DONE}:{new_req_id}"),
            InlineKeyboardButton("Отложить", callback_data=f"{BUTTON_REC_SKIP}:{new_req_id}"),
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    # Отправляем рекомендацию
    message = await context.bot.send_message(chat_id=user.Chat_Id,
                                             text=f'{context.job.data}, '
                                                  f'рекомендация № {new_req_id}: '
                                                  f'{rec_new.recommendation}!',
                                             reply_markup=markup)

    # Сохраняем отправленную рекомендацию в базу
    stat_rec = Status_recommendation()
    stat_rec.chat_id = user.Chat_Id
    stat_rec.user_id = user.User_ID
    stat_rec.send_time = datetime.now()
    stat_rec.message_id = message.message_id
    stat_rec.rec_id = new_req_id
    stat_rec.rec_status = REC_STATUS_INIT

    db_sess = db_session.create_session()
    db_sess.add(stat_rec)
    db_sess.commit()
    db_sess.close()

    # Если отправленная рекомендация не первая
    if last_rec:
        # Если рекомендация была проигнорирована пользователем, то откладываем ее
        if last_rec.rec_status == REC_STATUS_INIT:
            await skip_rec(context, user.User_ID, last_rec.rec_id)


async def send_notification(context: ContextTypes.DEFAULT_TYPE):
    user = await find_user_by_chat_id(context.job.chat_id)
    if user is None:
        await context.bot.send_message(chat_id=context.job.chat_id,
                                       text='Такой пользователь не найден, воспользуйтесь командой /start')
        context.job.schedule_removal()
        return

    # Если адвент выполнен, то прекращаем отправку уведомлений
    if await is_advent_completed(user.User_ID):
        context.job.schedule_removal()
        return

    db_sess = db_session.create_session()
    skipped_recommendations = db_sess.query(Status_recommendation).filter(
        Status_recommendation.user_id == user.User_ID, Status_recommendation.rec_status == REC_STATUS_SKIP).all()
    db_sess.close()

    if len(skipped_recommendations) == 0:
        return

    result = ''
    for rec in skipped_recommendations:
        rec_info = await get_recommendation_info_by_id(rec.rec_id)
        if rec_info is None:
            continue
        result += f'День {rec.rec_id}. {rec_info.recommendation}\n'

    result = f'Не выполнено {len(skipped_recommendations)} рекомендаций:\n' + result
    keyboard = [[InlineKeyboardButton("Сообщить о выполнении", callback_data=f"{BUTTON_REC_REPORT}")]]
    markup = InlineKeyboardMarkup(keyboard)

    # Отправляем уведомление
    await context.bot.send_message(chat_id=user.Chat_Id, text=result, reply_markup=markup)


async def done_recommendation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    del_idx = query.data.find(":") + 1
    rec_id = int(query.data[del_idx:])

    user = await find_user_by_chat_id(chat_id)
    if user is None:
        return

    db_sess = db_session.create_session()
    rec = (db_sess.query(Status_recommendation).
           filter(Status_recommendation.user_id == user.User_ID, Status_recommendation.rec_id == rec_id).
           first())
    db_sess.close()

    rec.rec_status = REC_STATUS_DONE

    db_sess = db_session.create_session()
    db_sess.add(rec)
    db_sess.commit()
    db_sess.close()

    await query.delete_message()
    await context.bot.send_message(chat_id=chat_id, text=f"Выполнена рекомендация №: {rec_id}")


async def skip_recommendation(update, context):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    del_idx = query.data.find(":") + 1
    rec_id = int(query.data[del_idx:])

    user = await find_user_by_chat_id(chat_id)
    if user is None:
        return

    await skip_rec(context, user.User_ID, rec_id)
    await context.bot.send_message(chat_id=user.Chat_Id, text=f"Отложена рекомендация №: {rec_id}")


async def run_recommendation_job(context, chat_id):
    user = await find_user_by_chat_id(chat_id)
    if user is None:
        return

    user_tz = pytz.timezone(user.Timezone)
    user_time = datetime.strptime(user.Time, '%H:%M')

    # Запуск рекомендаций только если не все рекомендации были отправлены
    if not await is_all_recommendation_sent(user.User_ID):
        sent_time = time(user_time.hour, user_time.minute, 00, tzinfo=user_tz)
        sent_days = (0, 1, 2, 3, 4, 5, 6)
        if user.Schedule == "Рабочие дни":
            sent_days = (0, 1, 2, 3, 4)
        elif user.Schedule == 'Выходные дни':
            sent_days = (5, 6)

        # Ежедневный запуск задачи
        context.job_queue.run_daily(send_recommendation, name=build_job_rec_name(user.Chat_Id),
                                    time=sent_time, days=sent_days, data=user.Name, chat_id=user.Chat_Id)

    # Запуск напоминаний только если не завершен адвент
    if not await is_advent_completed(user.User_ID):
        # Напоминание отправляем после отправки рекомендации на 30 мин позже
        sent_datetime = (user_tz.localize(
            datetime.combine(datetime.today(), time(user_time.hour, user_time.minute, 00)), is_dst=None) +
                         timedelta(minutes=30))

        # Запускаем задачу с отправкой напоминаний с пользовательским интервалом
        context.job_queue.run_repeating(send_notification, name=build_job_not_name(user.Chat_Id),
                                        first=sent_datetime, interval=timedelta(days=int(user.Period)),
                                        data=user.Name, chat_id=user.Chat_Id)

    # TODO: Для тестирования
    # context.job_queue.run_repeating(send_recommendation, 5, name=build_job_rec_name(user.Chat_Id), data=user.Name, chat_id=user.Chat_Id)
    # context.job_queue.run_repeating(send_notification, 10, name=build_job_not_name(user.Chat_Id), data=user.Name, chat_id=user.Chat_Id)


async def start_advent(update, context):
    chat_id = update.message.chat_id
    user = await find_user_by_chat_id(chat_id)
    if user is None:
        await context.bot.send_message(chat_id=chat_id, text='Такой пользователь не найден, '
                                                             'воспользуйтесь командой /start')
        return

    if not (user.Advent_Start is None):
        await context.bot.send_message(chat_id=chat_id, text='Новогодний адвент уже был запущен ранее!',
                                       reply_markup=build_main_menu(user.Advent_Start))
        return

    user.Advent_Start = datetime.now()
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()
    db_sess.close()

    await context.bot.send_message(chat_id=chat_id, text='Новогодний адвент запущен',
                                   reply_markup=build_main_menu(datetime.now()))
    await run_recommendation_job(context, chat_id)


async def resume_sending(context):
    chats = {}

    db_sess = db_session.create_session()
    # Определяем пользователей, у которых запущен адвент, но еще не было отправлено ни одно рекомендации
    users = (db_sess.query(User.Chat_Id).
             filter(User.Advent_Start != None).
             distinct())
    for row in users:
        chats[row[0]] = row[0]

    # Определяем количество рекомендаций, которые в принципе нужно было отправить
    recommendations_count = await get_recommendation_count()
    # Определяем пользователей, которым были отправлены рекомендации, но еще не все
    chat_users = (db_sess.query(Status_recommendation.chat_id).
                  group_by(Status_recommendation.chat_id).
                  having(func.max(Status_recommendation.rec_id) < recommendations_count).
                  all())
    for row in chat_users:
        chats[row[0]] = row[0]
    db_sess.close()

    for chat_id in chats:
        await run_recommendation_job(context, chat_id)


async def share(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat.id)

    user = await find_user_by_chat_id(chat_id)
    if user is None:
        await context.bot.send_message(chat_id=chat_id, text='Такой пользователь не найден, адвент будет остановлен!')
        context.job.schedule_removal()
        return

    keyboard = [
        [
            InlineKeyboardButton("Поделиться", url=f'https://t.me/share/url?url={bot_url}')
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=chat_id,
                                   text=f"Поделитесь нашим ботом со своими друзьями, чтобы и они "
                                        f"были грамотными в цифровой среде!",
                                   reply_markup=markup)
    await show_main_menu(update, context)


async def show_recommendation(update, context):
    chat_id = update.message.chat_id
    user = await find_user_by_chat_id(chat_id)
    if user is None:
        return

    db_sess = db_session.create_session()
    list_rec = (db_sess.query(Status_recommendation)
                .filter(Status_recommendation.user_id == user.User_ID)
                .order_by(Status_recommendation.rec_id.desc())
                .limit(3)
                .all())
    db_sess.close()

    if len(list_rec) == 0:
        await context.bot.send_message(chat_id=user.Chat_Id,
                                       text='Список рекомендаций пуст. Убедитесь, что вы запустили "Новогодний адвент"',
                                       reply_markup=build_main_menu(user.Advent_Start))
        return

    result = ''
    for idx, rec in enumerate(list_rec):
        rec_info = await get_recommendation_info_by_id(rec.rec_id)
        if rec_info is None:
            continue
        if idx == 0:
            result += f'*День {rec.rec_id}. Сегодня.* {rec_info.recommendation}\n'
        else:
            result += f'*День {rec.rec_id}.* {rec_info.recommendation}\n'

    await context.bot.send_message(chat_id=user.Chat_Id, text=f'Список трех последних рекомендаций:\n\n{result}',
                                   reply_markup=build_main_menu(user.Advent_Start),
                                   parse_mode='markdown')


async def test_knowledge(update, context):
    user = await find_user_by_chat_id(update.message.chat_id)
    if user is None:
        return

    if await is_advent_completed(user.User_ID):
        keyboard = [[InlineKeyboardButton("Пройти тест", callback_data=f"{BUTTON_RUN_TEST}")]]
        markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            'Поздравляем, вы выполнили все рекомендации! '
            'Хотите пройти проверку знаний и получить звание Джедая ордена Цифровой гигиены и '
            'возможность скачать стикерпак от Киберпротекта? '
            'Тогда попробуйте пройти тест!',
            reply_markup=markup)
        await show_main_menu(update, context)
    else:
        await update.message.reply_text(
            'Пройти тест можно будет только после выполнения всех рекомендаций адвента',
            reply_markup=build_main_menu(user.Advent_Start))


async def forma_yandex(update, context):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    user = await find_user_by_chat_id(chat_id)
    if user is None:
        return

    await context.bot.send_message(chat_id=user.Chat_Id, text='https://forms.yandex.ru/u/6663258b5056903972729751/',
                                   reply_markup=build_main_menu(user.Advent_Start))


# Получить страницу с отправленными рекомендациями
async def get_recommendation_page(user_id: str, page_num: int, page_size: int) -> str:
    db_sess = db_session.create_session()

    # Получаем пять последних отправленных рекомендаций пользователю
    j = join(Status_recommendation, Recommendation, Status_recommendation.rec_id == Recommendation.id)
    sent_recommendations = (db_sess.query(Status_recommendation.rec_id,
                                          Status_recommendation.rec_status,
                                          Recommendation.recommendation)
                            .select_from(j)
                            .filter(Status_recommendation.user_id == user_id)
                            .order_by(Status_recommendation.rec_id.desc())
                            .offset(page_num * page_size)
                            .limit(page_size)
                            .all())
    result = ''
    for idx, rec in enumerate(sent_recommendations):
        rec_id, rec_status, rec_name = rec[0], rec[1], rec[2]
        if rec_status == REC_STATUS_DONE:
            visualize = '🟢'
        elif rec_status == REC_STATUS_SKIP:
            visualize = '🔴'
        else:
            visualize = '⚪️'
        result += f'{visualize} № {rec_id}: {rec_name}\n'
    return result


async def show_result_query(update, context):
    query = update.callback_query
    await query.answer()
    return await show_results(update, context)


async def show_results(update, context):
    if not (update.callback_query is None):
        query = update.callback_query
        await query.answer()
        chat_id = query.message.chat_id
    else:
        chat_id = update.message.chat_id

    user = await find_user_by_chat_id(chat_id)
    if user is None:
        await context.bot.send_message(chat_id=chat_id, text='Пользователь не найден, воспользуйтесь командой /start')
        return

    # Определяем количество отправленных рекомендаций
    rec_count = await sent_recommendation_count(user.User_ID)
    if rec_count == 0:
        await context.bot.send_message(chat_id=user.Chat_Id, text='Еще ни одной рекомендации не было отправлено',
                                       reply_markup=build_main_menu(user.Advent_Start))
        return

    page_size = 5
    page_num = 0
    page_count = rec_count // page_size
    if rec_count % page_size > 0:
        page_count += 1

    if page_count > 1:
        reply_keyboard = [['Показать далее...', 'Изменить статус выполнения', 'Меню']]
    else:
        reply_keyboard = [['Изменить статус выполнения', 'Меню']]

    result = await get_recommendation_page(user.User_ID, page_num, page_size)
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    await context.bot.send_message(chat_id=user.Chat_Id, text=f'Результат выполнения:\n\n{result}\n\n'
                                                              f'Страница {page_num+1} из {page_count}',
                                   parse_mode='HTML', reply_markup=markup)

    context.user_data['page_size'] = page_size
    context.user_data['page_count'] = page_count
    context.user_data['page_num'] = page_num
    return RESULTS_SHOW


async def show_result_next(update, context):
    user = await find_user_by_chat_id(update.message.chat_id)
    if user is None:
        return

    page_size = context.user_data['page_size']
    page_count = context.user_data['page_count']
    page_num = context.user_data['page_num'] + 1

    if page_num < (page_count - 1):
        reply_keyboard = [['Показать далее...', 'Изменить статус выполнения', 'Меню']]
    else:
        reply_keyboard = [['Изменить статус выполнения', 'Меню']]

    result = await get_recommendation_page(user.User_ID, page_num, page_size)
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    await context.bot.send_message(chat_id=user.Chat_Id, text=f'Результат выполнения:\n\n{result}\n\n'
                                                              f'Страница {page_num+1} из {page_count}',
                                   parse_mode='HTML', reply_markup=markup)

    context.user_data['page_num'] = page_num
    return RESULTS_SHOW


async def change_results(update, context):
    user = await find_user_by_chat_id(update.message.chat_id)
    if user is None:
        return

    page_count = context.user_data['page_count']
    page_num = context.user_data['page_num'] + 1

    if page_num < (page_count - 1):
        reply_keyboard = [['Показать далее...', 'Изменить статус выполнения', 'Меню']]
    else:
        reply_keyboard = [['Изменить статус выполнения', 'Меню']]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

    await context.bot.send_message(chat_id=user.Chat_Id,
                                   text='Введите номер рекомендации, статус которой Вы хотели бы изменить',
                                   reply_markup=markup)
    return RESULTS_REC_NUM


async def change_status_results(update, context):
    user = await find_user_by_chat_id(update.message.chat_id)
    if user is None:
        return

    page_count = context.user_data['page_count']
    page_num = context.user_data['page_num'] + 1

    if page_num < (page_count - 1):
        reply_keyboard = [['Показать далее...', 'Изменить статус выполнения', 'Меню']]
    else:
        reply_keyboard = [['Изменить статус выполнения', 'Меню']]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

    rec_id = update.message.text
    if not rec_id.isdigit():
        await context.bot.send_message(chat_id=user.Chat_Id, text="Введите номер рекомендации",
                                       reply_markup=markup)
        return RESULTS_REC_NUM

    rec_info = await get_recommendation_info_by_id(update.message.text)
    if rec_info is None:
        await context.bot.send_message(chat_id=user.Chat_Id,
                                       text="Рекомендации с таким номером не найдена, попробуйте еще раз",
                                       reply_markup=markup)
        return RESULTS_REC_NUM

    keyboard = [
        [InlineKeyboardButton("Отметить как выполненное", callback_data=f"{BUTTON_REC_DONE}:{rec_id}")],
        [InlineKeyboardButton("Отложить выполнение", callback_data=f"{BUTTON_REC_SKIP}:{rec_id}")]
    ]
    inline_markup = InlineKeyboardMarkup(keyboard)
    rec = f'№ {rec_id}: {rec_info.recommendation}\n'
    await context.bot.send_message(chat_id=user.Chat_Id, text=rec, reply_markup=inline_markup)
    return RESULTS_SHOW


async def handle_everything_else(update, context):
    user = await find_user_by_chat_id(update.message.chat_id)
    if user is None:
        await context.bot.send_message(chat_id=update.message.chat_id,
                                       text="🤖 Ой, возможно мы еще не знакомы с вами, попробуйте выполнить команду /start")
        return

    await update.message.reply_text("🤖 Что-то я вас не понял, воспользуйтесь главным меню",
                                    reply_markup=build_main_menu(user.Advent_Start))

def run_web_server():
    port = int(os.environ.get("PORT", 5000))
    print(f"Web-server starting on port {port}")
    web.run(host='0.0.0.0', port=port)


def main():
    threading.Thread(target=run_web_server, daemon=True).start()

    init_recommendations()

    application = Application.builder().token(BOT_TOKEN).build()

    # Возобновление отправки рекомендаций после рестарта
    application.job_queue.run_once(resume_sending, 1)

    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("help", help_message))
    application.add_handler(CommandHandler("menu", show_main_menu))

    condition = (filters.TEXT | filters.PHOTO) & ~filters.COMMAND

    # Сценарий регистрации нового пользователя или приветствия существующего пользователя
    start_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GREETING_STATE: [MessageHandler(condition, greeting)],
            REGISTRATION_STATE: [MessageHandler(condition, registration)],
            NAME_STATE: [MessageHandler(condition, name)],
            SCHEDULE_STATE: [MessageHandler(condition, schedule)],
            TIME_STATE: [MessageHandler(condition, time_schedule)],
            TIMEZONE_STATE: [MessageHandler(condition, timezone_schedule)],
            SEX_STATE: [MessageHandler(condition, sex)],
            AGE_STATE: [MessageHandler(condition, age)],
            PERIOD_STATE: [MessageHandler(condition, period)],
        },
        fallbacks=[
            CommandHandler('stop', stop),
        ]
    )
    application.add_handler(start_handler)

    # Сценарий обработки кнопки "Мой профиль"
    profile_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text(["Мой профиль"]), show_profile)],
        states={
            PROFILE_SHOW_STATE: [
                MessageHandler(filters.Text(["Показать профиль"]), show_profile)
            ],
            PROFILE_EDIT_STATE: [
                MessageHandler(filters.Text(["Редактировать данные"]), edit_profile)
            ],
            PROFILE_EDIT_FIELD_STATE: [
                MessageHandler(filters.Text(["Имя", "Возраст", "Пол", "График", "Время", "Период напоминаний"]),
                               edit_profile_request),
                MessageHandler(filters.Text(["Назад"]), show_profile)
            ],
            PROFILE_EDIT_APPLY_STATE: [
                MessageHandler(condition, edit_profile_apply)
            ],
        },
        fallbacks=[
            MessageHandler(filters.Text(["Меню"]), show_main_menu),
        ]
    )

    application.add_handler(profile_handler)
    application.add_handler(
        MessageHandler(filters.Text(["Запустить новогодний адвент по цифровой гигиене"]), start_advent))
    application.add_handler(MessageHandler(filters.Text(["Рекомендации"]), show_recommendation))
    application.add_handler(MessageHandler(filters.Text(["Пройти тест по цифровой гигиене"]), test_knowledge))
    application.add_handler(MessageHandler(filters.Text(["Пригласить друзей"]), share))
    application.add_handler(MessageHandler(filters.Text(["Помощь"]), help_message))

    # Обработка кнопки "Результаты выполнения"
    results_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Text(["Результаты выполнения"]), show_results),
            CallbackQueryHandler(show_result_query, pattern=f"^{BUTTON_REC_REPORT}")
        ],
        states={
            RESULTS_SHOW: [
                MessageHandler(filters.Text(["Показать далее..."]), show_result_next),
                MessageHandler(filters.Text(["Изменить статус выполнения"]), change_results)
            ],
            RESULTS_REC_NUM: [
                MessageHandler(condition, change_status_results)
            ],
            RESULTS_CHANGE: [
                MessageHandler(filters.Text(["Назад"]), show_results)
            ],
        },
        fallbacks=[
            MessageHandler(filters.Text(["Меню"]), show_main_menu),
        ],
    )
    application.add_handler(results_handler)

    application.add_handler(CallbackQueryHandler(done_recommendation, pattern=f"^{BUTTON_REC_DONE}:\\d+$"))
    application.add_handler(CallbackQueryHandler(skip_recommendation, pattern=f"^{BUTTON_REC_SKIP}:\\d+$"))
    application.add_handler(CallbackQueryHandler(forma_yandex, pattern=f"^{BUTTON_RUN_TEST}$"))
    application.add_handler(
        CallbackQueryHandler(results_handler.entry_points[0].callback, pattern=f"^{BUTTON_REC_REPORT}"))

    application.add_handler(MessageHandler(filters.ALL, handle_everything_else))
    application.run_polling()


if __name__ == '__main__':
    main()
