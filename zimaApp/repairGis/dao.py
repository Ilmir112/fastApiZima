from sqlalchemy import select
from sqlalchemy.orm import joinedload

from zimaApp.dao.base import BaseDAO
from zimaApp.repairGis.models import RepairsGis


class RepairsGisDAO(BaseDAO):
    model = RepairsGis
