import coreapi
from .consts import GITLAB_HOST, GITLAB_ACCESS_TOKEN_KEY, GITLAB_ACCESS_TOKEN_VAL
from .auth import AuthenticationWithCustomHeader


client = coreapi.Client()
schema = client.get(GITLAB_HOST)

action = ['api-token-auth', 'create']
params = {"username": "example", "password": "secret"}
result = client.action(schema, action, params)

auth = AuthenticationWithCustomHeader(
    token=GITLAB_ACCESS_TOKEN_VAL,
    header_name=GITLAB_ACCESS_TOKEN_KEY,
)
client = coreapi.Client(auth=auth)