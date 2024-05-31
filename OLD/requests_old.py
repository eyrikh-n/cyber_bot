from models import async_session, Status_recommendation, Recommendation, User
import asyncio
from sqlalchemy import select, update, delete


async def set_status_recomendation(tg_id):
    async with async_session() as session:
        session.add(Status_recommendation(chat_id='1000456', status=10000, rec_status_1='Gray',
                                          rec_status_2='Gray', rec_status_3='Gray', rec_status_4='Gray',
                                          rec_status_5='Gray', rec_status_6='Gray', rec_status_7='Gray',
                                          rec_status_8='Gray', rec_status_9='Gray', rec_status_10='Gray',
                                          rec_status_11='Gray', rec_status_12='Gray', rec_status_13='Gray',
                                          rec_status_14='Gray', rec_status_15='Gray', rec_status_16='Gray',
                                          rec_status_17='Gray', rec_status_18='Gray', rec_status_19='Gray',
                                          rec_status_20='Gray', rec_status_21='Gray', rec_status_22='Gray',
                                          rec_status_23='Gray', rec_status_24='Gray', rec_status_25='Gray',
                                          rec_status_26='Gray', rec_status_27='Gray', rec_status_28='Gray',
                                          rec_status_29='Gray', rec_status_30='Gray'))
        await session.commit()


async def set_recomendation():
    async with async_session() as session:
        for i in range(30):
            a = str(i + 1)
            session.add(Recommendation(recommendation='Рекомендация №' + a))
        await session.commit()

async def set_user_1():
    async with async_session() as session:
        session.add(User(name='Мария', age_group='18-25', date='2024-05-22 17:46:43.574170', schedule='Выходные дни',
                         sex='Женский', user_name='Жемчужная длань', chat_id='559150172'))
        await session.commit()

async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(Status_recommendation).where(Status_recommendation.chat_id == tg_id))
        user_1 = await session.scalar(select(User).where(User.chat_id == tg_id))
        if not user and not user_1:
            session.add(Status_recommendation(chat_id=tg_id, status=0, rec_status_1='Gray',
                                              rec_status_2='Gray', rec_status_3='Gray', rec_status_4='Gray',
                                              rec_status_5='Gray', rec_status_6='Gray', rec_status_7='Gray',
                                              rec_status_8='Gray', rec_status_9='Gray', rec_status_10='Gray',
                                              rec_status_11='Gray', rec_status_12='Gray', rec_status_13='Gray',
                                              rec_status_14='Gray', rec_status_15='Gray', rec_status_16='Gray',
                                              rec_status_17='Gray', rec_status_18='Gray', rec_status_19='Gray',
                                              rec_status_20='Gray', rec_status_21='Gray', rec_status_22='Gray',
                                              rec_status_23='Gray', rec_status_24='Gray', rec_status_25='Gray',
                                              rec_status_26='Gray', rec_status_27='Gray', rec_status_28='Gray',
                                              rec_status_29='Gray', rec_status_30='Gray'))
            session.add(
                User(name='Мария', age_group='18-25', date='2024-05-22 17:46:43.574170', schedule='Выходные дни',
                     sex='Женский', user_name='Жемчужная длань', chat_id=tg_id))

        await session.commit()

# asyncio.run(set_status_recomendation())
# asyncio.run(set_user_1())
# asyncio.run(set_recomendation())
