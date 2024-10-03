class SentRecommendationModel:
    def __init__(self, rec_id: int, rec_status: str, text: str):
        self.rec_id = rec_id
        self.rec_status = rec_status
        self.text = text


    def to_dict(self):
        return {
            'rec_id': self.rec_id,
            'rec_status': self.rec_status,
            'text': self.text,
        }
