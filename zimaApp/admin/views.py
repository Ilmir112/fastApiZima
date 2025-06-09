from sqladmin import ModelView
from sqlalchemy.orm import joinedload

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

    column_list = [WellsRepair.well_data] + \
                  [c.name for c in WellsRepair.__table__.c]
    name = 'план работ'
    name_plural = 'Планы работ'

    def get_query(self):
        return super().get_query().options(joinedload(WellsRepair.well_data))