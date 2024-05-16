from models import async_session, Status_recommendation, Recommendation
import asyncio
from sqlalchemy import select, update, delete


async def set_user():
    async with async_session() as session:
        for i in range(30):
            a = str(i + 1)
            session.add(Recommendation(recommendation='Рекомендация №' + a))
        session.add(Status_recommendation(tg_id=300000002, status=1, rec_status_1='Gray',
                                          rec_status_2='Gray', rec_status_3='Gray', rec_status_4='Gray',
                                          rec_status_5='Gray', rec_status_6=0, rec_status_7='Gray',
                                          rec_status_8='Gray', rec_status_9='Gray', rec_status_10=0,
                                          rec_status_11='Gray', rec_status_12='Gray', rec_status_13='Gray',
                                          rec_status_14=0, rec_status_15='Gray', rec_status_16='Gray',
                                          rec_status_17='Gray', rec_status_18=0, rec_status_19='Gray',
                                          rec_status_20='Gray', rec_status_21='Gray', rec_status_22='Gray',
                                          rec_status_23='Gray', rec_status_24='Gray', rec_status_25='Gray',
                                          rec_status_26='Gray', rec_status_27='Gray', rec_status_28='Gray',
                                          rec_status_29='Gray', rec_status_30='Gray'))
        await session.commit()


asyncio.run(set_user())