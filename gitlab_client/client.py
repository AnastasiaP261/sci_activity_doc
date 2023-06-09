import requests
from requests import Response
from rest_framework.exceptions import AuthenticationFailed

from gitlab_client.consts import NOTE_ATTR_REPO_ID, NOTE_ATTR_BRANCH_NAME, NOTE_ATTR_FILE_PATH, NOTE_ATTR_FILE_FORMAT
from gitlab_client.parse_url import _get_note_attributes
from sci_activity_doc.settings import GITLAB_API_ADDRESS, GITLAB_ACCESS_TOKEN, GITLAB_ACCESS_TOKEN_HEADER_KEY, \
    GITLAB_TIMEOUT


class GitlabError(Exception):
    """
    Гитлаб вернул ошибку
    """

    def __init__(self, content: str, code: int):
        self.content = content
        self.code = code
        self.message = f"Response content: {self.content} with code: {self.code}"
        super().__init__(self.message)


class GLClient:
    def __init__(self, ):
        self._auth()

    def _auth(self):
        resp = self._get_projects()
        if resp.status_code != 200:
            raise AuthenticationFailed

    def _get(self, url: str, params: dict = None, headers: dict = None) -> Response:
        resp = requests.get(
            url=url,
            params=params,
            headers=headers,
            timeout=GITLAB_TIMEOUT,
        )

        return resp

    def _get_projects(self):
        return self._get(
            url=f'{GITLAB_API_ADDRESS}/projects/',
            headers={
                GITLAB_ACCESS_TOKEN_HEADER_KEY: GITLAB_ACCESS_TOKEN,
            },
        )

    def _get_note_by_url(self, note_attrs: dict):
        resp = self._get(
            url=f'{GITLAB_API_ADDRESS}/projects/{note_attrs[NOTE_ATTR_REPO_ID]}/repository/files/{note_attrs[NOTE_ATTR_FILE_PATH]}/raw',
            headers={
                GITLAB_ACCESS_TOKEN_HEADER_KEY: GITLAB_ACCESS_TOKEN,
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

        else:
            raise GitlabError(str(resp.content), resp.status_code)
