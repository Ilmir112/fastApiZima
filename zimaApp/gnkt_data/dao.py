from sqlalchemy import event

from zimaApp.dao.base import BaseDAO

from zimaApp.gnkt_data.models import GnktData


class GnktDatasDAO(BaseDAO):
    model = GnktData

