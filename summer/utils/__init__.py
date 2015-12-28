import datetime

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    def __getattr__(self, attr):
        return self.get(attr)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__


def encode_datetime(o):
    if isinstance(o, datetime.datetime) or isinstance(o, datetime.date):
        return o.isoformat()
    return None
