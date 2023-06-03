from .graph import Graph
from .nnr import NodesNotesRelation
from .note import Note
from .research import Research
from .user import User

# Прим: ограничение max_length в типе models.TextField используется только тогда,
# когда поле отображается в формах и сериализаторах (оно не применяется на уровне базы данных)
