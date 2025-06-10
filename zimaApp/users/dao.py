from zimaApp.dao.base import BaseDAO
from zimaApp.users.models import Users



class UsersDAO(BaseDAO):
    model = Users
