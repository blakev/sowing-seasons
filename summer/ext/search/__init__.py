import re
import os
import datetime
import logging
from uuid import uuid4

from tornado import gen
from whoosh.analysis import StemmingAnalyzer, StopFilter
from whoosh.fields import *
from whoosh.index import create_in, exists_in, open_dir
from whoosh.writing import IndexingError

from summer.utils import DotDict

logger = logging.getLogger(__name__)

IGNORE_WORDS = []

class SowingSchema(SchemaClass):
    uuid = NUMERIC(
        unique=True, stored=True, numtype=int, bits=64, signed=False)
    modified = DATETIME(
        stored=True, sortable=True)
    statics = ID(
        stored=True)
    topic = TEXT(
        stored=True, field_boost=2.0, sortable=True)
    slug = TEXT(
        stored=True, sortable=True)
    title = TEXT(
        stored=True, field_boost=1.4, sortable=True)
    keywords = KEYWORD(
        stored=True, lowercase=True, commas=True, field_boost=1.2)
    summary = TEXT(
        stored=True, spelling=True, phrase=True, field_boost=1.1)
    content = TEXT(
        stored=True, spelling=True, phrase=True, field_boost=0.9,
        analyzer=StemmingAnalyzer(
            minsize=4, stoplist=IGNORE_WORDS, cachesize=1024*64) | StopFilter())


def obtain_index(location, schema, index_name, force_new_index=False, read_only=False):
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


# Helpers

def clean_results(idx, results, query=None):
    schema = idx.schema
    ret, default_document = list(), get_default_schema(schema)

    metadata = DotDict()
    metadata.search_time = round(results.runtime, 4)
    metadata.count = len(results)
    metadata.query = str(query)

    for doc in results:
        # create a copy of the default structure
        # then replace the fields that exist in our
        # returned document; this will also add any
        # fields/columns that didn't exist in the original schema.
        res = dict(default_document)
        res.update(doc.items())
        ret.append(res)

    metadata.results = ret
    return metadata


def get_default_schema(schema, uuid=None, modified_date=None):
    if uuid is None:
        uuid = int(str(uuid4().int)[:8])

    if modified_date is None:
        modified = datetime.datetime.utcnow()

    ret_schema = dict().fromkeys(schema._fields)

    ret_schema['uuid'] = uuid
    ret_schema['modified'] = modified

    return ret_schema


def slugify(title):
    SLUG_REGEX = re.compile(r'[\w\d_]+')
    slug_title = '-'.join(map(lambda x: x.lower(), SLUG_REGEX.findall(title)))
    return slug_title

def document_slug(document):
    # matches the BlogHandler pattern:
    # .. /blog/([a-z]+)/(\d+)/(\d+)/(.*)/(\d+)/
    # .. /blog/topic/year/month/_slug_/uuid/
    doc = DotDict(document)
    year = doc.modified.year
    month = str(doc.modified.month).zfill(2)    # 0-pad the month

    return r'/blog/{}/{}/{}/{}/{}'.format(
        doc.topic, year, month, slugify(doc.title), doc.uuid)

@gen.coroutine
def write_index(idx, **fields):
    try:
        writer = idx.writer()
        writer.add_document(**fields)
        writer.commit()
        success = True
    except (IndexError, IOError) as e:
        logger.error(e)
        success = False
    return success


@gen.coroutine
def update_index(idx, is_delete=False, **fields):
    try:
        writer = idx.writer()
        if is_delete:
            writer.delete_by_term('uuid', fields.get('uuid'))
        else:
            writer.update_document(**fields)
        writer.commit()
        success = True
    except (IndexError, IOError) as e:
        logger.error(e)
        success = False
    return success

