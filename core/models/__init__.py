from .graph import Graph
from .research import Research
from .note import Note
from .nnr import NodesNotesRelation
from .user import User

# Прим: ограничение max_length в типе models.TextField используется только тогда,
# когда поле отображается в формах и сериализаторах (оно не применяется на уровне базы данных)
