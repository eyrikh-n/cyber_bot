from datetime import datetime
from data.users import User

class UserModel:

    def __init__(self, user_id: int = None, name: str = None, registration_day: datetime = None,
                 age_group: str = None, schedule: str = None, sex: str = None, telegram_username: str = None,
                 telegram_id: str = None, time: str = None, timezone: str = None, period: str = None,
                 advent_start: datetime = None):
        self.user_id = user_id
        self.name = name
        self.registration_day = registration_day
        self.age_group = age_group
        self.schedule = schedule
        self.sex = sex
        self.telegram_username = telegram_username
        self.telegram_id = telegram_id
        self.time = time
        self.timezone = timezone
        self.period = period
        self.advent_start = advent_start

def db_user_to_model(db_user: User) -> UserModel:
    return UserModel(db_user.User_ID, db_user.Name, db_user.Registration_Day, db_user.Age_Group,
                     db_user.Schedule, db_user.Sex, db_user.UserName, db_user.Chat_Id,
                     db_user.Time, db_user.Timezone, db_user.Period, db_user.Advent_Start)
