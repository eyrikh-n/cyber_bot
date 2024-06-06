import logging
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

import pytz
from sqlalchemy import func

from data import db_session
from data.users import User
from data.recommendations import Recommendation
from data.status_recommendation import Status_recommendation
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler, CallbackContext, \
    CallbackQueryHandler, ContextTypes
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, Update

BOT_TOKEN = '6522784356:AAHB7lKSBukJDq-Tq3SAB9mxql95Cn9Dutg'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
db_session.global_init("db/data_base.db")
logger = logging.getLogger(__name__)

(GREETING_STATE, REGISTRATION_STATE, NAME_STATE, SCHEDULE_STATE, SEX_STATE,
 AGE_STATE, SHOW_MENU_STATE, TIME_STATE, TIMEZONE_STATE, PERIOD_STATE) = range(10)

PROFILE_SHOW_STATE, PROFILE_EDIT_STATE, PROFILE_EDIT_FIELD_STATE, PROFILE_EDIT_APPLY_STATE = range(4)
ADVENT_TIMER_STATE, ADVENT_WORK_STATE = range(2)

REC_BUTTON_DONE, REC_BUTTON_SKIP, REC_BUTTON_REPORT = "rec_button_done", "rec_button_skip", "rec_button_report"


async def get_timezone_by_utc_offset(utc_offset: timedelta) -> str:
    current_utc_time = datetime.now(pytz.utc)
    for tz in map(pytz.timezone, pytz.all_timezones_set):
        if current_utc_time.astimezone(tz).utcoffset() == utc_offset:
            return tz.zone
    return ""


async def help(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Я умею вести диалог из двух вопросов.")


async def stop(update, context):
    await update.message.reply_text("Всего доброго!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def find_user_by_chat_id(chat_id: str) -> Optional[User]:
    db_sess = db_session.create_session()
    return db_sess.query(User).filter(User.Chat_Id == chat_id).first()


async def start(update, context):
    chat_id = str(update.message.chat.id)
    user = await find_user_by_chat_id(chat_id)
    if user is None:
        reply_keyboard = [['Запустить']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "Добрый день. Данный бот поможет вам за N дней усилить защиту ваших аккаунтов, данных, а"
            " также обучит основам обеспечения цифровой гигиены. 🤖 Вам достаточно ежедневно выполнять по"
            " одной рекомендации.", reply_markup=markup)
        return GREETING_STATE
    else:
        reply_keyboard = [['Меню']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(
            f"Добрый день, {user.Name}, давно не виделись! Воспользуйтесь меню.", reply_markup=markup)
        return SHOW_MENU_STATE


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
            await update.message.reply_text("Укажите интервал, в который вам будут присылаться напоминания"
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
    return await show_menu(update, context)


def create_profile(update, context):
    db_sess = db_session.create_session()
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
    db_sess.add(user)
    db_sess.commit()


async def show_menu(update, context):
    db_sess = db_session.create_session()
    username = str(update.message.from_user.username)
    user = db_sess.query(User).filter(User.UserName == username).first()
    reply_keyboard = [['Мой профиль', 'Рекомендации']]
    if user:
        reply_keyboard.append(['Запустить новогодний адвент по цифровой гигиене'])
    reply_keyboard.extend([
        ['Результаты выполнения'],
        ['Пройти тест по цифровой гигиене'],
        ['Пригласить друзей', 'Помощь']])

    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Меню", reply_markup=markup)
    return ConversationHandler.END


async def show_profile(update, context):
    reply_keyboard = [['Редактировать данные'], ['Меню']]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

    db_sess = db_session.create_session()
    username = str(update.message.from_user.username)
    user = db_sess.query(User).filter(User.UserName == username).first()

    reply_text = ("Профиль (новый) 🔽 \n"
                  f"💠 Имя - {user.Name} \n"
                  f"💠 График - {user.Schedule} \n"
                  f"💠 Возраст - {user.Age_Group} лет \n"
                  f"💠 Время выдачи рекомендаций - {user.Time}\n")
    if user.Sex != 'Пропустить':
        reply_text = reply_text + f"💠 Пол {user.Sex}"

    await update.message.reply_text(reply_text, reply_markup=markup)
    return PROFILE_EDIT_STATE


async def edit_profile(update, context):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.Chat_Id == str(update.message.chat.id)).first()
    sent_recommendations = db_sess.query(Status_recommendation).filter(Status_recommendation.user_id == user.User_ID).all()
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
        # TODO: Не давать изменить график, если ты уже подписался на advent
        reply_keyboard = [['Ежедневно'], ['Рабочие', 'Выходные дни']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Сформируйте удобный для вас график получения"
                                        " рекомендаций и уведомлений. Какой график для вас удобен?",
                                        reply_markup=markup)
    elif message_text == "График":
        # TODO: Не давать изменить график, если ты уже подписался на advent
        reply_keyboard = [['Ежедневно'], ['Рабочие', 'Выходные дни']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Сформируйте удобный для вас график получения"
                                        " рекомендаций и уведомлений. Какой график для вас удобен?",
                                        reply_markup=markup)
    elif message_text == "Время":
        await update.message.reply_text(
            "Укажите время в часах(от 0 до 23), в которое вы хотите получать рекомендации ⌚")
    elif message_text == "Период напоминаний":
        await update.message.reply_text("Укажите интервал, в который вам будут присылаться напоминания"
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
                context.user_data['time'] = f'{message_text}:00:00'
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

    db_sess = db_session.create_session()
    username = str(update.message.from_user.username)
    user = db_sess.query(User).filter(User.UserName == username).first()

    user.Name = context.user_data.get('name', user.Name)
    user.Age_Group = context.user_data.get('age', user.Age_Group)
    user.Schedule = context.user_data.get('days', user.Schedule)
    user.Sex = context.user_data.get('sex', user.Sex)
    user.Time = context.user_data.get('time', user.Time)
    user.Period = context.user_data.get('period', user.Period)

    db_sess.add(user)
    db_sess.commit()

    reply_keyboard = [['Показать профиль', 'Меню']]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text("Изменения профиля успешно применены!", reply_markup=markup)
    return PROFILE_SHOW_STATE


async def send_recommendation(context):
    chat_id = context.job.chat_id

    # Выполняем поиск пользователя по идентификатору чата
    user = await find_user_by_chat_id(chat_id)
    # Если пользователь не найден, то адвент прекращается - выход
    if user is None:
        await context.bot.send_message(chat_id=chat_id, text='Такой пользователь не найден, адвент будет остановлен!')
        context.job.schedule_removal()
        return

    db_sess = db_session.create_session()
    # Определяем количество рекомендаций, которые в принципе нужно было отправить
    recommendations_count = db_sess.query(Recommendation).count()

    # Получаем все ранее отправленные рекомендации этому пользователю
    sent_recommendations = db_sess.query(Status_recommendation).filter(
        Status_recommendation.user_id == user.User_ID).all()

    # Если ранее уже отправлялись рекомендации, то определяем последнюю отправленную, иначе используем первую
    if len(sent_recommendations) != 0:
        last_rec_id = sent_recommendations[-1].rec_id
    else:
        last_rec_id = 0

    new_req_id = last_rec_id + 1
    # Если все рекомендации уже были отправлены ранее, то завершаем адвент - выход
    if new_req_id > recommendations_count:
        await context.bot.send_message(chat_id=chat_id, text=f'Вы прошли все рекомендации!')
        context.job.schedule_removal()
        return

    # Получаем текст очередной рекомендации и отправляем ее пользователю
    rec_new = db_sess.query(Recommendation).filter(Recommendation.id == new_req_id).first()

    keyboard = [
        [
            InlineKeyboardButton("Выполнить", callback_data=f"{REC_BUTTON_DONE}:{new_req_id}"),
            InlineKeyboardButton("Отложить", callback_data=f"{REC_BUTTON_SKIP}:{new_req_id}"),
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    # Отправляем рекомендацию
    message = await context.bot.send_message(chat_id=chat_id,
                                             text=f'{context.job.data}, '
                                                  f'рекомендация № {new_req_id}: '
                                                  f'{rec_new.recommendation}!',
                                             reply_markup=markup)

    # Сохраняем отправленную рекомендацию в базу
    stat_rec = Status_recommendation()
    stat_rec.chat_id = chat_id
    stat_rec.user_id = user.User_ID
    stat_rec.send_time = datetime.now()
    stat_rec.message_id = message.message_id
    stat_rec.rec_id = new_req_id
    stat_rec.rec_status = 0

    db_sess.add(stat_rec)
    db_sess.commit()

    # Если отправленная рекомендация не первая, то подчищаем в чате предыдущую рекомендацию
    if last_rec_id > 0:
        old_message = sent_recommendations[-1].message_id
        # TODO: Сообщения может не быть, получим BadRequest в логах
        await context.bot.delete_message(chat_id=chat_id, message_id=old_message)


async def send_notification(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id

    user = await find_user_by_chat_id(chat_id)
    if user is None:
        await context.bot.send_message(chat_id=chat_id, text='Такой пользователь не найден, адвент будет остановлен!')
        context.job.schedule_removal()
        return

    db_sess = db_session.create_session()
    sent_recommendations = db_sess.query(Status_recommendation).filter(
        Status_recommendation.user_id == user.User_ID).all()

    count_uncomleted_recommendations = 0
    result = ''

    for rec in sent_recommendations:
        if rec.rec_status == '2':
            count_uncomleted_recommendations += 1
            recomm = db_sess.query(Recommendation).filter(Recommendation.id == rec.rec_id).first()
            recc = recomm.recommendation
            result += f'День {rec.rec_id}. {recc}\n'

    if result == '':
        context.job.schedule_removal()
        return

    result = f'Не выполнено {count_uncomleted_recommendations} рекомендаций:\n' + result
    keyboard = [
        [
            InlineKeyboardButton("Сообщить о выполнении", callback_data=f"{REC_BUTTON_REPORT}")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    # Отправляем рекомендацию
    message = await context.bot.send_message(chat_id=chat_id,
                                             text=result,
                                             reply_markup=markup)

    # Если отправленная рекомендация не первая, то подчищаем в чате предыдущую рекомендацию
    # if last_rec_id > 0:
    #     old_message = sent_recommendations[-1].message_id
    #     # TODO: Сообщения может не быть, получим BadRequest в логах
    #     await context.bot.delete_message(chat_id=chat_id, message_id=old_message)


async def send_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


async def done_recommendation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    del_idx = query.data.find(":") + 1
    rec_id = int(query.data[del_idx:])

    db_sess = db_session.create_session()
    rec = (db_sess.query(Status_recommendation).
           filter(Status_recommendation.chat_id == chat_id, Status_recommendation.rec_id == rec_id).
           first())

    rec.rec_status = "1"
    db_sess.add(rec)
    db_sess.commit()

    await query.delete_message()
    await context.bot.send_message(chat_id=chat_id, text=f"Выполнена рекомендация №: {rec_id}")


async def skip_recommendation(update, context):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    del_idx = query.data.find(":") + 1
    rec_id = int(query.data[del_idx:])

    db_sess = db_session.create_session()
    rec = (db_sess.query(Status_recommendation).
           filter(Status_recommendation.chat_id == chat_id, Status_recommendation.rec_id == rec_id).
           first())

    rec.rec_status = "2"
    db_sess.add(rec)
    db_sess.commit()

    await query.delete_message()
    await context.bot.send_message(chat_id=chat_id, text=f"Отложена рекомендация №: {rec_id}")


async def run_recommendation_job(context, user):
    # TODO: Нужно запускать в зависимости от временных настроек пользователя
    context.job_queue.run_repeating(send_recommendation, 5, data=user.Name, chat_id=user.Chat_Id)


async def run_notification_job(context, user):
    # TODO: Нужно запускать в зависимости от временных настроек пользователя
    context.job_queue.run_repeating(send_notification, 10, data=user.Name, chat_id=user.Chat_Id)


async def set_timer(update, context):
    chat_id = update.message.chat_id
    user = await find_user_by_chat_id(chat_id)
    if user is None:
        await context.bot.send_message(chat_id=chat_id, text='Такой пользователь не найден, адвент не будет запущен!')
        return

    await context.bot.send_message(chat_id=chat_id, text='Новогодний адвент запущен')
    await run_notification_job(context, user)
    await run_recommendation_job(context, user)


async def resume_sending(context):
    db_sess = db_session.create_session()

    # Определяем количество рекомендаций, которые в принципе нужно было отправить
    recommendations_count = db_sess.query(Recommendation).count()
    chat_users = (db_sess.query(Status_recommendation.chat_id).
                  group_by(Status_recommendation.chat_id).
                  having(func.max(Status_recommendation.rec_id) < recommendations_count).
                  all())

    for row in chat_users:
        chat_id = row[0]
        user = await find_user_by_chat_id(chat_id)
        if user is None:
            continue
        await run_recommendation_job(context, user)


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Возобновление отправки рекомендаций после рестарта
    application.job_queue.run_once(resume_sending, 1)

    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("help", help))

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
            SHOW_MENU_STATE: [MessageHandler(filters.Text(["Меню"]), show_menu)]
        },
        fallbacks=[
            CommandHandler('stop', stop),
            MessageHandler(filters.Text(["Меню"]), show_menu),
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
                MessageHandler(filters.Text(["Имя", "Возраст", "Пол", "График", "Время", "Период напоминаний"]), edit_profile_request),
                MessageHandler(filters.Text(["Назад"]), show_profile)
            ],
            PROFILE_EDIT_APPLY_STATE: [
                MessageHandler(condition, edit_profile_apply)
            ],
        },
        fallbacks=[
            MessageHandler(filters.Text(["Меню"]), show_menu),
        ]
    )

    application.add_handler(profile_handler)
    application.add_handler(
        MessageHandler(filters.Text(["Запустить новогодний адвент по цифровой гигиене"]), set_timer))

    application.add_handler(CallbackQueryHandler(done_recommendation, pattern=f"^{REC_BUTTON_DONE}:\\d+$"))
    application.add_handler(CallbackQueryHandler(skip_recommendation, pattern=f"^{REC_BUTTON_SKIP}:\\d+$"))

    application.add_handler(CallbackQueryHandler(send_results, pattern=f"^{REC_BUTTON_REPORT}"))

    # Сценарий обработки кнопки "Запустить новогодний адвент по цифровой гигиене"
    # TODO: Оформить этот код как ConversationHandler как сделано выше с профилем
    # if message_text == 'Запустить новогодний адвент по цифровой гигиене':
    #     db_sess = db_session.create_session()
    #     username = str(update.message.from_user.username)
    #     user = db_sess.query(User).filter(User.UserName == username).first()
    #     name = user.Name
    #
    #     flag_first_event = True
    #     reply_keyboard = [['Отметить как выполненное', 'Отложить'], ['Меню']]
    #     markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    #     await update.message.reply_text(f"{name} <Рекомендация 1*>", reply_markup=markup)
    #     return FIRST_EVENT

    application.run_polling()


if __name__ == '__main__':
    main()
