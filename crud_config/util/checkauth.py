from crud_config import app, db
from crud_config.models import *
from tobool import toBool
from werkzeug.contrib.cache import MemcachedCache

def checkAuth(auth):
    (auth_type, auth_value) = auth
    cache = MemcachedCache(app.config['MEMCACHE_SERVERS'].split(","))
    cache_key = "AUTH-%s+%s" % (auth_type, auth_value)

    # Auth is in the cache, go ahead sir
    if toBool(cache.get(cache_key)) is True:
        return True

    # Auth is not cached
    if auth_type.upper() == "APIKEY":
        valid = ApiKey.query.filter_by(api_key=auth_value).first()
        if valid is None:
            return False
        else:
            cache.set(cache_key, True, timeout=app.config['CACHE_AUTH'])
            return True
        return False

    elif auth_type.upper() == "LDAP":
        return False

    else:
        return False