from markupsafe import Markup
from sqladmin import ModelView
from sqlalchemy.orm import joinedload

from zimaApp.gnkt_data.models import GnktData
from zimaApp.norms.models import NormsWork
from zimaApp.users.models import Users
from zimaApp.well_classifier.models import WellClassifier
from zimaApp.well_silencing.models import WellSilencing
from zimaApp.wells_data.models import WellsData
from zimaApp.wells_repair_data.models import WellsRepair


class UserAdmin(ModelView, model=Users):
    column_list = [Users.id, Users.login_user, Users.surname_user, Users.name_user, Users.second_name,
                   Users.position_id, Users.contractor]
    column_details_exclude_list = [Users.password]

    name = 'Пользователь'
    name_plural = 'Пользователи'
    # icon = 'fa-sold fa-user'
    # form_excluded_columns = ["login_user"]



class SilencingAdmin(ModelView, model=WellSilencing):
    column_list = [c.name for c in WellSilencing.__table__.c]
    # Добавляем фильтры по нужным колонкам
    column_searchable_list = ["well_number", "well_area"]
    column_sortable_list = ["region", "well_number", "cdng"]
    column_labels = {
        "well_number": "Номер скважины",
        "well_area": "Площадь скважины",
        "region": "регион"
    }
    column_filters = False
    can_delete = False

    name = 'Перечень без глушения'
    name_plural = 'Перечень без глушения'


class GnktAdmin(ModelView, model=GnktData):
    column_list = [c.name for c in GnktData.__table__.columns]
    name = 'ГНКТ'
    name_plural = 'ГНКТ'


class NormsAdmin(ModelView, model=NormsWork):
    # pk_columns = [NormsWork.__table__.c.id]  # замените 'id' на ваше имя первичного ключа

    column_list = ["well_repair.well_data.well_number", "well_repair.well_data.well_area"] +\
                  [c.name for c in NormsWork.__table__.columns]



    def format_summary_work(self, obj):
        from markupsafe import Markup
        return Markup(f'''
            <a href="/admin/norms/{obj.id}/view" target="_blank">Подробнее</a>
        ''')

    column_formatters = {
            'summary_work': format_summary_work,
        }
    #

    name = 'АВР'
    name_plural = 'АВР'


class WellsDataAdmin(ModelView, model=WellsData):
    column_list = [c.name for c in WellsData.__table__.c]
    name = 'Данные по скважине'
    name_plural = 'скважины'
    column_searchable_list = ["well_number", "well_area"]
    column_labels = {
        "well_number": "Номер скважины",
        "well_area": "Площадь",
        "oilfield": "Месторождение",
        "region": "регион"
    }
    column_filters = ["well_number", "well_area"]


class ClassifierAdmin(ModelView, model=WellClassifier):
    column_list = [c.name for c in WellClassifier.__table__.c]
    name = 'Классификатор скважин'
    name_plural = 'Классификатор скважин'
    column_searchable_list = ["well_number", "well_area"]
    column_labels = {
        "well_number": "Номер скважины",
        "well_area": "Площадь",
        "oilfield": "Месторождение",
        "region": "регион"
    }
    column_sortable_list = ["region", "well_number", "cdng"]
    column_filters = ["well_number", "well_area"]
    column_filters = False
    can_delete = False
    icon = 'fa fa-users'


class RepairDataAdmin(ModelView, model=WellsRepair):

    column_list = ["well_data.well_number", "well_data.well_area"] + [WellsRepair.well_data] + \
                  [c.name for c in WellsRepair.__table__.c]
    name = 'план работ'
    name_plural = 'Планы работ'

    def get_query(self):
        return super().get_query().options(joinedload(WellsRepair.well_data))