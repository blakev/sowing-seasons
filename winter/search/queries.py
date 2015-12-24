from tornado import gen
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.sorting import MultiFacet

from winter.search import get_default_schema
from winter.utils import DotDict

@gen.coroutine
def generic(idx, qs):
    if not qs:
        return []

    parser = MultifieldParser(
            ['title', 'keywords', 'summary', 'content'], idx.schema, group=OrGroup)

    metadata = DotDict()
    ret_results = []

    # get the default document structure
    default_doc = get_default_schema()

    with idx.searcher() as search:
        # generate the Query object
        query = parser.parse(qs)

        facet = MultiFacet()

        facet.add_field('modified', reverse=True)
        facet.add_score()
        facet.add_field('title')

        results = search.search(query, sortedby=facet)

        metadata.search_time = results.runtime
        metadata.qs = qs
        metadata.query = str(query)
        metadata.count = len(results)

        for doc in results:
            # create a copy of the default structure
            # then replace the fields that exist in our
            # returned document; this will also add any
            # fields/columns that didn't exist in the original schema.
            result_doc = dict(default_doc)
            result_doc.update(doc.items())
            ret_results.append(result_doc)

    metadata.results = ret_results

    return metadata