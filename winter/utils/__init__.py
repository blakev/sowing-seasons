import datetime

datetime_encode = lambda o: (
    o.isoformat()
    if isinstance(o, datetime.datetime)
    or isinstance(o, datetime.date)
    else None
)

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    def __getattr__(self, attr):
        return self.get(attr)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__
