import requests
from requests import Response
from rest_framework.exceptions import AuthenticationFailed, NotFound

from gitlab_client.consts import NOTE_ATTR_REPO_ID, NOTE_ATTR_BRANCH_NAME, NOTE_ATTR_FILE_PATH, NOTE_ATTR_FILE_FORMAT
from gitlab_client.parse_url import _get_note_attributes
from sci_activity_doc.consts import GET_METHOD
from sci_activity_doc.settings import GITLAB_HOST, GITLAB_ACCESS_TOKEN, GITLAB_ACCESS_TOKEN_HEADER_KEY, GITLAB_TIMEOUT


class GLClient:
    token_header_key: str
    token_val: str
    address: str
    gitlab_timeout: float  # в секундах

    def __init__(
            self,
            host: str = GITLAB_HOST,
            token_header_key: str = GITLAB_ACCESS_TOKEN_HEADER_KEY,
            token_val: str = GITLAB_ACCESS_TOKEN,
            timeout: float = GITLAB_TIMEOUT,
    ):
        self.address = host
        self.token_val = token_val
        self.token_header_key = token_header_key
        self.gitlab_timeout = timeout

        self._auth()

    def _auth(self):
        resp = self._get_projects()
        if resp.status_code != 200:
            raise AuthenticationFailed

    def _get(self, url: str, params: dict = None, headers: dict = None) -> Response:
        resp = requests.request(
            method=GET_METHOD,
            url=url,
            params=params,
            headers=headers,
            timeout=self.gitlab_timeout,
        )

        return resp

    def _get_projects(self):
        return self._get(
            url=f'{self.address}/projects/',
            headers={
                self.token_header_key: self.token_val,
            },
        )

    def _get_note_by_url(self, note_attrs: dict):
        resp = self._get(
            url=f'{self.address}/projects/{note_attrs[NOTE_ATTR_REPO_ID]}/repository/files/{note_attrs[NOTE_ATTR_FILE_PATH]}/raw',
            headers={
                self.token_header_key: self.token_val,
            },
            params={
                'ref': note_attrs[NOTE_ATTR_BRANCH_NAME],
            },
        )
        return resp

    def get_note_raw_text_by_url(self, note_url: str) -> (str, str):
        """
        Получает из гитлаба текст файла по его url.
        Первый возвращаемый параметр - текст, а второй - формат файла заметки
        """

        note_attrs = _get_note_attributes(note_url)
        resp = self._get_note_by_url(note_attrs)

        if resp.ok:
            text = resp.text
            return text, note_attrs[NOTE_ATTR_FILE_FORMAT]

        elif resp.status_code == 404:
            raise NotFound()
