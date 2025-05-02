from zimaApp.dao.base import BaseDAO
from zimaApp.database import async_session_maker
from sqlalchemy import select

from zimaApp.well_classifier.models import WellClassifier
from zimaApp.wells_silencing.models import WellSilencing


class WellClassifierDAO(BaseDAO):
    model = WellClassifier


class WellSilencingDAO(BaseDAO):
    model = WellSilencing

