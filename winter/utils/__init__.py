import re
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

SLUG_REGEX = re.compile(r'[\w\d_]+')

def slugify(title, dt):
    """ Slugs a search index result object for better SSO via URL parsing.

    Args:
        title:
        dt:

    Returns:
        str, str
    """
    slug_title = '-'.join(map(lambda x: x.lower(), SLUG_REGEX.findall(title)))
    slug_date = dt.strftime('%h-%d-%Y').lower()
    return slug_title, slug_date