from re import search
from urllib.parse import urlparse, quote

from rest_framework.exceptions import ParseError

from gitlab_client.consts import NOTE_ATTR_REPO_ID, NOTE_ATTR_BRANCH_NAME, NOTE_ATTR_FILE_PATH, NOTE_ATTR_NOTE_TYPE, \
    NOTE_ATTR_FILE_FORMAT


def _get_note_attributes(note_url: str) -> dict:
    """
    Достает из url заметки все необходимые атрибуты (все атрибуты, которые должны быть закодированы - будут закодированы).
    :param note_url: url заметки
    :return: словарь, содержащий атрибуты
    """
    note_url = urlparse(note_url)
    try:
        f = search(r'/(.+?)/blob/(.+?)/(.*)', note_url.path)
        repo_id = f.group(1)
        branch = f.group(2)
        file_path = f.group(3)

        f = search(rf'(.*/)*(.*)\.(.*)', file_path)
        file_name = f.group(2)
        file_format = f.group(3)
        try:
            note_type = file_name.split('_', 3)[2]
        except IndexError:
            note_type = ''

    except AttributeError:
        raise ParseError()

    attrs = {
        NOTE_ATTR_REPO_ID: quote(repo_id, safe=''),
        NOTE_ATTR_BRANCH_NAME: branch,
        NOTE_ATTR_FILE_PATH: quote(file_path, safe=''),
        NOTE_ATTR_NOTE_TYPE: note_type,
        NOTE_ATTR_FILE_FORMAT: file_format,
    }

    return attrs


def parse_note_type_from_url(note_url: str) -> str:
    """
    Достает тип заметки из ее url
    """
    attrs = _get_note_attributes(note_url)
    return attrs[NOTE_ATTR_NOTE_TYPE]
