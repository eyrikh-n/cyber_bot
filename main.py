import logging

import aiohttp
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup

BOT_TOKEN = '6695783288:AAE_aD-9wJGgWy-5uEUp2YK0sDxWoHPbXeY'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)



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
    await update.message.reply_text("Добрый день. Данный бот поможет вам за N дней усилить защиту ваших аккаунтов, данных, а"
                                    " также обучит основам обеспечения цифровой гигиены. Вам достаточно ежедневно выполнять по"
                                    " одной рекомендации.", reply_markup=markup)
    return 1


async def get_name(update, context):
    context.user_data['state'] = update.message.text

    if context.user_data['state'] == 'Запустить':
        await update.message.reply_text("Вы сделали уверенный шаг на пути обеспечения безопасности ваших данных. "
                                        "Пожалуйста, ответьте на несколько вопросов, и мы начнем.")


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("help", help))

    condition = (filters.TEXT | filters.PHOTO) & ~filters.COMMAND
    handler_1 = MessageHandler(condition, get_name)
    # handler_2 = MessageHandler(condition, respond)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [handler_1],
            # 2: [handler_2]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()