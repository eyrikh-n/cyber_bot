from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker
from sqlalchemy import select
import asyncio

engine = create_async_engine(url='sqlite+aiosqlite:///db///Baza_TG.sqlite3')
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass

class Recommendation(Base):
    __tablename__ = 'recommendations'

    id: Mapped[int] = mapped_column(primary_key=True)
    recommendation: Mapped[str] = mapped_column(String(1000))

class Status_recommendation(Base):
    __tablename__ = 'status_recommendations'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50))
    rec_status_1: Mapped[str] = mapped_column(String(50))
    rec_status_2: Mapped[str] = mapped_column(String(50))
    rec_status_3: Mapped[str] = mapped_column(String(50))
    rec_status_4: Mapped[str] = mapped_column(String(50))
    rec_status_5: Mapped[str] = mapped_column(String(50))
    rec_status_6: Mapped[str] = mapped_column(String(50))
    rec_status_7: Mapped[str] = mapped_column(String(50))
    rec_status_8: Mapped[str] = mapped_column(String(50))
    rec_status_9: Mapped[str] = mapped_column(String(50))
    rec_status_10: Mapped[str] = mapped_column(String(50))
    rec_status_11: Mapped[str] = mapped_column(String(50))
    rec_status_12: Mapped[str] = mapped_column(String(50))
    rec_status_13: Mapped[str] = mapped_column(String(50))
    rec_status_14: Mapped[str] = mapped_column(String(50))
    rec_status_15: Mapped[str] = mapped_column(String(50))
    rec_status_16: Mapped[str] = mapped_column(String(50))
    rec_status_17: Mapped[str] = mapped_column(String(50))
    rec_status_18: Mapped[str] = mapped_column(String(50))
    rec_status_19: Mapped[str] = mapped_column(String(50))
    rec_status_20: Mapped[str] = mapped_column(String(50))
    rec_status_21: Mapped[str] = mapped_column(String(50))
    rec_status_22: Mapped[str] = mapped_column(String(50))
    rec_status_23: Mapped[str] = mapped_column(String(50))
    rec_status_24: Mapped[str] = mapped_column(String(50))
    rec_status_25: Mapped[str] = mapped_column(String(50))
    rec_status_26: Mapped[str] = mapped_column(String(50))
    rec_status_27: Mapped[str] = mapped_column(String(50))
    rec_status_28: Mapped[str] = mapped_column(String(50))
    rec_status_29: Mapped[str] = mapped_column(String(50))
    rec_status_30: Mapped[str] = mapped_column(String(50))


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    age_group: Mapped[str] = mapped_column(String(50))
    date: Mapped[str] = mapped_column(String(100))
    schedule: Mapped[str] = mapped_column(String(50))
    sex: Mapped[str] = mapped_column(String(50))
    user_name: Mapped[str] = mapped_column(String(100))
    chat_id: Mapped[str] = mapped_column(String(100))

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    asyncio.run(async_main())