from zimaApp.dao.base import BaseDAO
from zimaApp.well_classifier.models import WellClassifier


class WellClassifierDAO(BaseDAO):
    model = WellClassifier
