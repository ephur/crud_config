from ccapi import app 
import crudconfig

from werkzeug.contrib.cache import MemcachedCache

def toBool(string):
    if str(string).upper() in ['YES', 'Y', '1', 'TRUE', 'T', 'YE']: return True
    if str(string).upper() in ['N', 'NO', 'FALSE', 'F', '0', "0.0", "[]", "{}", "NONE", ""]: return False
    raise ValueError("Unknown Boolean Value %s" % (str(string).upper()))

def checkAuth(auth):
    (auth_type, auth_value) = auth
    cache = MemcachedCache(app.config['MEMCACHE_SERVERS'].split(","))
    cache_key = "AUTH-%s+%s" % (auth_type, auth_value)
    # Auth is in the cache, go ahead sir
    if toBool(cache.get(cache_key)) is True:
        return True

    # Auth is not cached
    if auth_type.upper() == "APIKEY":
        cconfig = crudconfig.CrudConfig(keypath=app.config['KEYPATH'], 
                                        db_name=app.config['DATABASE_DB'],
                                        db_username=app.config['DATABASE_USER'],
                                        db_password=app.config['DATABASE_PASS'],
                                        db_host=app.config['DATABASE_HOST'])
        if cconfig.check_api_key(auth_value) is True:
            cache.set(cache_key, True, timeout=app.config['CACHE_AUTH'])
            return True
        return False

    elif auth_type.upper() == "LDAP":
        return False

    else:
        return False