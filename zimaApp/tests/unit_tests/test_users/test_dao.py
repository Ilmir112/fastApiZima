import pytest

from zimaApp.users.dao import UsersDAO


@pytest.mark.parametrize(
    "user_id,login_user,is_present", [(1, "Ilmir112", True), (2, "string2", True)]
)
async def test_find_user_by_id(user_id, login_user, is_present):
    user = await UsersDAO.find_by_id(user_id)

    if is_present:
        assert user is not None
        assert user.login_user == login_user
    else:
        assert user is None
