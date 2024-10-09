from data.advices import Advices


class AdvicesModel:
    def __init__(self, num: str, text: str):
        self.num = num
        self.text = text


def db_advice_to_model(db_advices: Advices) -> AdvicesModel:
    return AdvicesModel(db_advices.id, db_advices.advice)