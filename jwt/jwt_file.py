import jwt
from cryptography.hazmat.primitives import serialization

payload_data = {
    "sub": "4242",
    "name": "Andy",
    "nickname": "Sailor723"
}

token = jwt.encode(
    payload= payload_data,
    key = "my_suppert_secret"
)

token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MjQyIiwibmFtZSI6IkFuZHkiLCJuaWNrbmFtZSI6IlNhaWxvcjcyMyJ9.H4KPyjuE3MKVsHVOt9JK00mrM8ts-w2DVsHHVdRzZRQ'

jwt.decode(token, key='my_supper_secret', algorithms=['HS256',])

header_data = jwt.get_unverified_header(token)

jwt.decode(token, key="my_supper_secret", algorithms=[header_data['alg'],]) 