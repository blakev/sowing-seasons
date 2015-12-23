import os

from whoosh.analysis import StemmingAnalyzer, StopFilter
from whoosh.fields import *
from whoosh.index import create_in, exists_in, open_dir

IGNORE_WORDS = []

class WinterSchema(SchemaClass):
    uuid = NUMERIC(
        unique=True, stored=True, numtype=int, bits=64, signed=False)

    statics = ID(stored=True)
    title = TEXT(stored=True, field_boost=1.4, sortable=True)
    keywords = KEYWORD(stored=True, lowercase=True, commas=True, field_boost=1.2)
    summary = TEXT(stored=True, spelling=True, phrase=True, field_boost=1.1)
    content = TEXT(
            stored=True, spelling=True, phrase=True, field_boost=0.9,
            analyzer=StemmingAnalyzer(
                minsize=5, stoplist=IGNORE_WORDS, cachesize=1024*64) | StopFilter())


def obtain_index(location, schema, index_name, force_new_index=False, read_only=False):
    """Returns, or creates a new, whoosh search index.

    Args:
        location (str):
        schema:
        index_name (str):
        force_new_index (bool) False:
        read_only (bool) False:

    Returns:

    """

    created_index = False

    if not os.path.exists(location):
        try:
            os.makedirs(location)
        except IOError as e:
            raise e
        else:
            created_index = True

    if created_index or force_new_index:
        index = create_in(location, schema, indexname=index_name)

    else:
        if exists_in(location, indexname=index_name):
            index = open_dir(location, index_name, readonly=read_only, schema=schema)

        else:
            raise EnvironmentError('no search index found at: ' + location)

    return index


async def read_index(index):
    return "read"


async def write_index(index):
    return "Write"


async def search_index(index):
    return "search"