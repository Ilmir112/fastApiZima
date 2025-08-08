from sqlalchemy import select
from sqlalchemy.orm import selectinload

from zimaApp.dao.base import BaseDAO
from zimaApp.database import async_session_maker
from zimaApp.logger import logger
from zimaApp.repairtime.models import StatusSummary, RepairTime
from zimaApp.summary.models import BrigadeSummary


class BrigadeSummaryDAO(BaseDAO):
    model = BrigadeSummary


