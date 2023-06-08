import os

GITLAB_HOST = os.environ.get("GITLAB_HOST")
GITLAB_ACCESS_TOKEN = os.environ.get("GITLAB_ACCESS_TOKEN")
GITLAB_ACCESS_TOKEN_HEADER_KEY = os.environ.get("GITLAB_ACCESS_TOKEN_HEADER_KEY")
GITLAB_DEBUG = os.environ.get("GITLAB_DEBUG", default=False)
GITLAB_TIMEOUT = os.environ.get("GITLAB_TIMEOUT", default=2.)

# ключи для словаря атрибутов заметки, которые получаем из ее url
NOTE_ATTR_REPO_ID = 'repo_id'
NOTE_ATTR_BRANCH_NAME = 'branch_name'
NOTE_ATTR_FILE_PATH = 'file_path'
NOTE_ATTR_NOTE_TYPE = 'note_type'
NOTE_ATTR_FILE_FORMAT = 'file_format'

FILE_FORMAT_TEX = 'tex'
