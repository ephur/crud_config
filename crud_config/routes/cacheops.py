from crud_config import app
from crud_config import db
from crud_config.models.cachereference import CacheReference
from werkzeug.contrib.cache import MemcachedCache
import hashlib


def getkey(path, params):
    """
    generate a cache key based on the arguments

    Understood keyword arguments:
        (boolean) tree; If True treated as a container tree cache
        (boolean) data; URI data
    """

    simple = True
    app.logger.debug("Generating cache key for path --- params Path: %s /// Params: %s" % (path, params))
    cache_params = dict()
    cache_params['KEY'] = list()
    cache_params['TAG'] = list()
    cache_params['CONTAINERS'] = list()

    for item, value in params.iteritems():
        app.logger.debug("%s:%s" % (item, value))
        if item in ["KEY", "SEARCHKEY"]:
            cache_params[item].append({"name": value})
            simple = False
        if item in ["TAG"]:
            cache_params[item].append({"name": value})
            simple = False

    sanitized_uri = "/" + path + "?" + "&".join(
        ["%s=%s" % (k.upper(), v.upper()) for k, v in sorted(
         params.iteritems())])

    hashkey = hashlib.sha512(sanitized_uri).hexdigest()

    if simple is True:
        app.logger.debug("Using SIMPLE cache")
    elif simple is False:
        for item in path.split("/"):
            cache_params['CONTAINERS'].append({"name": item})
        data = CacheReference.query.filter_by(cache_id=hashkey).first()
        if data is None:
            newitem = CacheReference(hashkey, 'page', sanitized_uri)
            db.session.add(newitem)
            db.session.commit()
            newitem.save_cache_entry(**cache_params)
        else:
            if data.uri != sanitized_uri:
                raise Exception("DATA Integrity error! cache key is returning nonmatching URI")
        app.logger.debug("Using DATABASE cache")

    app.logger.debug("returning key: %s for sanitized URL: %s" % (hashkey, sanitized_uri))
    return hashkey


def get_cached_container_tree(path):
    """
    Method to get a cached container tree
    """
    pass


def cache_container_tree(path):
    """
    Method to deal with storing a container tree in the hash
    """
    pass


def purge(path, params):
    """
    This is to invalidate cache items that are submitted.
    """
    app.logger.debug("Cache Purge Path: %s " % path)
    app.logger.debug("Cache Purge Params: %s" % params)
    cache = MemcachedCache(app.config['MEMCACHE_SERVERS'].split(","))

    # Setup the main container purge
    return_param_options = ['ALL', 'CONTAINERS', 'VALUES']
    if path[0] != "/":
        path = "/" + path
    purge_keys = [hashlib.sha512(path).hexdigest()]
    purge_keys_plain = [(path)]
    purge_keys.append(hashlib.sha512(path + "?").hexdigest())
    purge_keys_plain.append(path + "?")

    # Purge all the return options for the given container
    for an_option in return_param_options:
        purge_keys.append(hashlib.sha512(path + "RETURN=" + an_option).hexdigest())
        purge_keys_plain.append(path + "?" + "RETURN=" + an_option)

    # Purge all the containers that were part of the put/post as well as container values
    try:
        for container in params['containers']:
            purge_keys.append(hashlib.sha512(path + "/" + container['name'] + "?").hexdigest())
            purge_keys_plain.append(path + "/" + container['name'] + "?")
        for an_option in return_param_options:
            purge_keys.append(hashlib.sha512(path + "RETURN=" + an_option).hexdigest())
            purge_keys_plain.append(path + "/" + container['name'] + "?" + "RETURN=" + an_option)
    except KeyError as e:
        pass

    # Purge the keys

    # Setup the key purge
    for item in params:
        app.logger.debug(item)

    app.logger.debug("PURGING KEYS: %s" % ("|".join(purge_keys)))
    app.logger.debug("PURGING KEYS: %s" % ("|".join(purge_keys_plain)))
    cache.delete_many(*purge_keys)
    return True