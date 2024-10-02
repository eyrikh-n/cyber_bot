from datetime import datetime

from data.status_recommendation import Status_recommendation


class SentRecommendationModel:
    def __init__(self, rec_id: int, rec_status: str, text: str):
        self.rec_id = rec_id
        self.rec_status = rec_status
        self.text = text
