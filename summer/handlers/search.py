from tornado import gen
from whoosh.qparser import QueryParser

from summer.ext.search import clean_results
from summer.ext.search.queries import generic
from summer.handlers import BaseHandler


class StaticSearchHandler(BaseHandler):
    @gen.coroutine
    def get(self, subject, value, is_atom=None):
        # pagination results
        try:
            page_number = int(self.get_argument('page', 1))
        except ValueError:
            page_number = 1

        # get the index from the application meta data
        idx = self.meta.search_index

        # clean up the subject and search value from the url bar
        subject, value = subject.split()[0], value.strip(' /')

        # build the query string we'll pass to the QueryParser
        q = '%s:%s' % (subject, value)

        # build the QueryParser instance from the index schema
        parser = QueryParser(subject, schema=idx.schema)

        # get our results, in a clean format for display
        results = yield generic(idx, qs=q, parser=parser, page=page_number)

        keywords = self.get_keywords(results)
        topics = self.get_topics(results)

        if is_atom:
            # render the results as an atom feed
            self.write(self.generate_feed(results, subtitle=q, url=self.this_url))

        else:
            # render the results to the page!
            self.render_html('pages/search_results.html',
                    keywords=keywords, topics=topics, results=results, term=value)


class DynamicSearchHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        self.render_html('pages/search.html')