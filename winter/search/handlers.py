import simplejson as json
from tornado import gen
from winter.search import get_default_schema, write_index
from winter.search.queries import generic
from winter.utils import datetime_encode
from winter.views import BaseHandler


class SearchHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        body = json.loads(self.request.body)
        fields = get_default_schema()
        fields.update(body)
        success = yield write_index(self.meta.search_index, **fields)
        self.write({'success': success})

    @gen.coroutine
    def get(self):
        # get the query strings
        qs = ' '.join(self.get_query_arguments('qs'))
        results = yield generic(self.meta.search_index, qs)
        self.write(json.dumps(results, default=datetime_encode))