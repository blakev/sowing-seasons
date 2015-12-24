from tornado import gen
from whoosh.query import Every
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.sorting import MultiFacet

from winter.search import get_default_schema
from winter.utils import DotDict, slugify

def clean_results(results):
    ret = []

    # get the default document structure
    default_doc = get_default_schema()

    for doc in results:
        # create a copy of the default structure
        # then replace the fields that exist in our
        # returned document; this will also add any
        # fields/columns that didn't exist in the original schema.
        result_doc = dict(default_doc)
        result_doc.update(doc.items())
        result_doc['slug'] = slugify(doc['title'], doc['modified'])
        ret.append(result_doc)

    return ret


@gen.coroutine
def get_all_documents(idx):
    with idx.searcher() as search:
        results = search.search(Every())
        return clean_results(results)


@gen.coroutine
def get_one_document(idx, by_id):
    with idx.searcher() as search:
        results = search.documents(uuid=by_id)
        return clean_results(results)

@gen.coroutine
def generic(idx, qs=None, q=None, limit=10):
    if qs is q is None:
        raise ValueError('cannot have a null querystring and query')

    parser = MultifieldParser(
            ['title', 'keywords', 'summary', 'content'], idx.schema, group=OrGroup)

    metadata = DotDict()

    with idx.searcher() as search:
        # generate the Query object

        if qs:
            query = parser.parse(qs)
        else:
            query = q

        facet = MultiFacet()

        facet.add_field('modified', reverse=True)
        facet.add_score()
        facet.add_field('title')

        results = search.search(query, sortedby=facet, limit=limit)

        metadata.search_time = results.runtime
        metadata.qs = qs
        metadata.query = str(query)
        metadata.count = len(results)
        metadata.results = clean_results(results)

    return metadata