from collections import Counter
from datetime import datetime, timedelta

from tornado import gen
from whoosh.query import Every, DateRange
from whoosh.qparser import MultifieldParser, OrGroup, QueryParser
from whoosh.qparser.dateparse import DateParserPlugin
from whoosh.sorting import MultiFacet

from summer.ext.search import clean_results
from summer.utils import DotDict

@gen.coroutine
def get_all_topics_and_kw(idx):
    with idx.searcher() as search:
        # collections to return as the result
        keywords = Counter()
        topics = set()
        # search through every document
        results = search.search(Every(), limit=None)
        for document in results:
            # and extract the Topic and Keywords, how we want them
            topics.add(document['topic'])
            keywords.update([x.strip() for x in document.get('keywords', '').split(',')])
    return {'keywords': keywords.most_common(None), 'topics': topics}

@gen.coroutine
def get_all_documents(idx, limit=None):
    with idx.searcher() as search:
        results = search.search(Every(), limit=limit)
        return clean_results(idx, results)

@gen.coroutine
def get_one_document(idx, by_id=None):
    with idx.searcher() as search:
        q = QueryParser('uuid', idx.schema).parse(by_id)
        results = search.search(q)
        related = results[0].more_like_this('keywords', top=3, numterms=10)
        return clean_results(idx, results), clean_results(idx, related)

@gen.coroutine
def documents_last_year(idx):
    pass

@gen.coroutine
def documents_last_month(idx):
    posts = yield generic(idx, qs="modified:-30 days to now")
    return posts

@gen.coroutine
def generic(idx, qs=None, q=None, limit=10, parser=None, page=1):
    if qs is q is None:
        raise ValueError('cannot have a null querystring and query')

    if parser is None:
        parser = MultifieldParser(
                ['title', 'keywords', 'summary', 'content'], idx.schema, group=OrGroup)

    # add better date parsing support
    parser.add_plugin(DateParserPlugin())

    with idx.searcher() as search:
        # generate the Query object
        if qs:
            query = parser.parse(qs)
        else:
            query = q

        facet = MultiFacet()
        facet.add_score()
        facet.add_field('modified', reverse=True)
        facet.add_field('title')

        results = search.search_page(query, pagenum=page, sortedby=facet, pagelen=limit)
        res = clean_results(idx, results, query)

        # pagination attributes on `search_page` method
        res.page_number = results.pagenum   # current page number
        res.page_total = results.pagecount  # total pages in results
        res.offset = results.offset         # first result of current page
        res.pagelen = results.pagelen       # the number of max results per page

    return res