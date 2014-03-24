from crud_config import app, db
from crud_config.models import *
from tobool import toBool
from werkzeug.contrib.cache import MemcachedCache
read_methods = ['GET', 'HEAD']
write_methods = ['PUT', 'DELETE', 'POST']

def checkAuth(auth):

    (auth_type, auth_value, request) = auth

    cache = MemcachedCache(app.config['MEMCACHE_SERVERS'].split(","))
    cache_key = "AUTH-%s+%s" % (auth_type, auth_value)
    # Auth is in the cache, go ahead sir
    if auth_type == 'APIKEY':
        return checkAuthAPI(cache, cache_key, auth_value, request)

    elif auth_type == 'LDAP':
        return checkAuthLDAP(cache, cache_key, auth_value, request)

    else:
        return False
    return False

def checkAuthAPI(cache, cache_key, auth_value, request):
    # Get the auth record from cache if possible, if not it comes from the DB
    authvalue = cache.get(cache_key)
    if authvalue is None:
        authvalue = ApiKey.query.filter_by(api_key=auth_value).first()
    if authvalue is None:
        # Not in cache or DB, so it's not valid
        return False
    else:
        cache.set(cache_key, authvalue, timeout=app.config['CACHE_AUTH'])

    # Check the methods to determine if reads/write required
    if request.method in read_methods:
        if authvalue.valid is True:
            return True
        else:
            return False
    if request.method in write_methods:
        if (authvalue.valid is True) and (authvalue.write is True):
            return True
        else:
            return False

    # Shouldn't make it here, if so return False if somehow it does
    return False

def checkAuthLDAP(cache, cache_key, auth_value, request):
    return False