import jwt
from gtd.settings import SECRET_KEY


def user_token_to_data(token):
    payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
    return payload["user_id"]