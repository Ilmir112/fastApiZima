from sqladmin import ModelView

from zimaApp.users.models import Users
from zimaApp.well_classifier.models import WellClassifier
from zimaApp.well_silencing.models import WellSilencing
from zimaApp.wells_repair_data.models import WellsRepair


class UserAdmin(ModelView, model=Users):
    column_list = [Users.id, Users.login_user, Users.surname_user, Users.name_user, Users.second_name,
                   Users.position_id, Users.contractor]
    column_details_exclude_list = [Users.password]
    can_delete = False
    name = 'Пользователь'
    name_plural = 'Пользователи'
    icon = 'fa-sold fa-user'


class SilencingAdmin(ModelView, model=WellSilencing):
    column_list = [c.name for c in WellSilencing.__table__.c]
    name = 'Перечень без глушения'
    name_plural = 'Перечень без глушения'

    # Добавляем фильтры по нужным колонкам
    column_filters = [
        'well_number',
        'deposit_area'
    ]


class ClassifierAdmin(ModelView, model=WellClassifier):
    column_list = [c.name for c in WellClassifier.__table__.c]
    name = 'Классификатор скважин'
    name_plural = 'Классификатор скважин'

    # Добавляем фильтры по нужным колонкам
    column_filters = [
        'well_number',
        'deposit_area'
    ]


class RepairDataAdmin(ModelView, model=WellsRepair):
    column_list = [c.name for c in WellsRepair.__table__.c]
    name = 'план работ'
    name_plural = 'Планы работ'
