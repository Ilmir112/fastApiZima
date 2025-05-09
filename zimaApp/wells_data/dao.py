from zimaApp.dao.base import BaseDAO
from zimaApp.wells_data.models import WellsData


class WellsDatasDAO(BaseDAO):
    model = WellsData
