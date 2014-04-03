from crud_config import app
from crud_config import db
from crud_config.models.cachereference import CacheReference
from crud_config.models.cachecontainers import CacheContainers
from crud_config.models.cachekeys import CacheKeys
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
        if item in ["SEARCHKEY"]:
            cache_params[item].append({"name": value})
            simple = False
        if item in ["TAG","KEY"]:
            cache_params[item].append({"name": value})
            simple = True

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
    try:
        for keyval in params['keyvals']:
            try:
                purge_keys.append(hashlib.sha512(path + "?TAG=" + keyval['tag'].upper()).hexdigest())
                purge_keys_plain.append(path + "?TAG=" + keyval['tag'].upper())
            except KeyError:
                pass
    except KeyError:
        pass

    # Purge all the return options for the given container
    for an_option in return_param_options:
        purge_keys.append(hashlib.sha512(path + "?RETURN=" + an_option).hexdigest())
        purge_keys_plain.append(path + "?" + "RETURN=" + an_option)
        try:
            for keyval in params['keyvals']:
                try:
                    purge_keys.append(hashlib.sha512(path + "?RETURN=" + an_option + "&TAG=" + keyval['tag'].upper()).hexdigest())
                    purge_keys_plain.append(path + "?RETURN=" + an_option + "&TAG=" + keyval['tag'].upper())
                except KeyError:
                    pass
        except KeyError:
            pass
    # Purge all the containers that were part of the put/post as well as container values
    try:
        for container in params['containers']:
            foo = db.session.query(CacheContainers).filter(CacheContainers.container_name==unicode(container["name"]))
            app.logger.debug(foo)
            app.logger.debug(dir(foo))
            purge_keys.append(hashlib.sha512(path + "/" + container['name'] + "?").hexdigest())
            purge_keys_plain.append(path + "/" + container['name'] + "?")
            for an_option in return_param_options:
                purge_keys.append(hashlib.sha512(path + "RETURN=" + an_option).hexdigest())
                purge_keys_plain.append(path + "/" + container['name'] + "?" + "RETURN=" + an_option)
    except KeyError as e:
        pass

    # Purge the keys that were updated in the container
    try:
        for keyval in params['keyvals']:
            try:
                tag = keyval['tag'].upper()
            except KeyError:
                tag=app.config['DEFAULT_TAG'].upper()

            app.logger.debug(unicode(keyval["key"]))
            cachedkeys = db.session.query(CacheKeys).filter(CacheKeys.key_name==unicode(keyval["key"].lower())).all()
            app.logger.debug(cachedkeys)
            try:
                for cachedkey in cachedkeys:
                    if cachedkey.parent.uri.split("?")[0].startswith(path):
                        app.logger.debug(cachedkey.parent.child_tags)
                        for child_tag in cachedkey.parent.child_tags:
                            app.logger.debug(child_tag.tag_name)
                            app.logger.debug("%s:%s" % (child_tag.tag_name, tag))
                            if child_tag.tag_name == tag:
                                app.logger.debug("MATCHED DATABASE CACHE ITEM: %s" % cachedkey.parent.cache_id)
                                purge_keys.append(cachedkey.parent.cache_id)
                                purge_keys_plain.append(cachedkey.parent.uri)
                                app.logger.debug(cachedkey.parent)
                                db.session.delete(cachedkey.parent)
                                db.session.commit()
                                break
            except TypeError as e:
                app.logger.debug("May be normal, but.... in case not! %s" % e.message)
                pass

            purge_keys.append(hashlib.sha512(path + "?KEY=" + keyval['key'] + "&TAG=" + tag).hexdigest())
            purge_keys_plain.append(path + "?KEY=" + keyval['key'] + "&TAG=" + tag)
            for an_option in return_param_options:
                purge_keys.append(hashlib.sha512(path + "?KEY=" + keyval['key'] +
                                                 "&RETURN=" + an_option +
                                                 "&TAG=" + tag).hexdigest())
                purge_keys_plain.append(path + "?KEY=" + keyval['key'] +
                                        "&RETURN=" + an_option +
                                        "&TAG=" + tag)
    except KeyError as e:
        app.logger.debug("May be normal, but.... in case not! %s" % e.message)
        pass

    app.logger.debug("PURGING KEYS: %s" % ("|".join(purge_keys)))
    app.logger.debug("PURGING KEYS: %s" % ("|".join(purge_keys_plain)))
    cache.delete_many(*purge_keys)
    return True