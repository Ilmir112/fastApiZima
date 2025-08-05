from pydantic import BaseModel


class SUsersRegister(BaseModel):
    login_user: str
    name_user: str
    surname_user: str
    second_name: str
    position_id: str
    costumer: str
    contractor: str
    ctcrs: str
    password: str


class SUserUpdate(BaseModel):
    login_user: str
    name_user: str
    surname_user: str
    second_name: str
    position_id: str
    costumer: str
    contractor: str
    ctcrs: str
    password: str

class SUsersAuth(BaseModel):
    login_user: str
    password: str
