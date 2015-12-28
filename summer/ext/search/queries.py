from tornado import gen
from whoosh.query import Every
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.sorting import MultiFacet

from summer.ext.search import clean_results
from summer.utils import DotDict

@gen.coroutine
def get_all_documents(idx, limit=None):
    with idx.searcher() as search:
        results = search.search(Every(), limit=limit)
        return clean_results(idx, results)


@gen.coroutine
def get_one_document(idx, by_id=None):
    with idx.searcher() as search:
        results = search.documents(uuid=by_id)
        results = clean_results(idx, results)
        return results[0] if results else None


@gen.coroutine
def get_related(idx, by_id=None):
    pass


@gen.coroutine
def generic(idx, qs=None, q=None, page=1, limit=10):
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

        results = search.search_page(query, page, sortedby=facet, limit=limit)

        metadata.search_time = results.runtime
        metadata.qs = qs
        metadata.query = str(query)
        metadata.count = len(results)
        metadata.results = clean_results(idx, results)

    return metadata