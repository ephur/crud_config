import flask
import simplejson as json
import crudconfig

from ccapi import app
from ccapi.error_handlers import error
from keyczar import keyczar
from werkzeug.contrib.cache import MemcachedCache
from time import sleep
from random import random


cache_servers=app.config['MEMCACHE_SERVERS'].split(",")
cache = MemcachedCache(cache_servers)

def get_main(path):
    # This will handle all gets that are not otherwise defined.
    cache_key = path + "?" + "&".join(["%s=%s" % (k.upper(), v.upper()) for k, v in flask.request.args.iteritems()])
    loadkey = "loading-" + cache_key
    cache_result = cache.get(cache_key)
    loops = 0
    # All get's are served up from the cache. If it's not in the cache, it should be.
    while cache_result is None:
        # Keep track of loops, abort if it get's to be excessive, this may need tuned 
        # later depending on how long DB operations take, right now the number of wait 
        # loops is excessive
        loops += 1
        if loops > 50:
            return(error(500, message="item never became available in cache", debug="%d: %s" %(loops, cache_key)))
        app.logger.debug("%s is not cached, checked %d times" % (cache_key, loops))
        sleeptime = random() / 10
        sleep(sleeptime)
        # For other threads that might be requesting the same thing, announce to the cache
        # that we're processing this page, help to eliminate overloading during bursts for
        # the same key.
        if cache.get("loading-" + cache_key) is None and cache.get(cache_key) is None:
            # Announce we're loading to the cache, be sure to expire in case we never delete
            cache.set("loading-" + cache_key, "True", timeout=app.config['CACHE_LOCKING_SECONDS'])
            # Set values for the request
            request_tag = app.config['DEFAULT_TAG']
            request_key = None
            for (k, v) in flask.request.args.iteritems():
                if k.upper() == "TAG":
                    request_tag = v.upper()
                elif k.upper() == "KEY":
                    request_key = v.upper()
                else:
                    # only handle query params we know about
                    # helps a little against attack, and ensuring people aren't 
                    # submitting stuff they think does something when it does not
                    # Oh yeah... In the words of Jesse Pinkman: "No Cache Busting Bitches"
                    return(error(400,"invalid query string parameters", key=k, value=v, path=cache_key))

            app.logger.debug("I'm doing the loading after a sleep of %f seconds" % (sleeptime))
            cconfig = crudconfig.CrudConfig(keypath=app.config['KEYPATH'], 
                                            db_name=app.config['DATABASE_DB'],
                                            db_username=app.config['DATABASE_USER'],
                                            db_password=app.config['DATABASE_PASS'],
                                            db_host=app.config['DATABASE_HOST'])
            # The CrudConfig library handles encrpytion of values, but not decryption
            # This is because of the data model, would be nice to fix and offload this
            # to the crud config library as well :( Or perhaps move the encrpytion to
            # this app, but I'd prefer it in the crud config library, but all in once place is best...
            crypter = keyczar.Crypter.Read(app.config['KEYPATH'])

            if request_key is not None:
                # A single Key is requested
                try:
                    key = cconfig.get_key(path, request_key, tag=request_tag)
                except crudconfig.exceptions.NoResult:
                    flask.abort(404)

                return_key = { key.name: {"values": list() } }
                return_key[key.name]['tag'] = key.tag
                # @TODO: Fix date added/date updated
                # return_key['added'] = key.added
                # return_key['updated'] = key.updated

                for v in key.values:
                    try:
                        return_key[key.name]['values'].append({'id': v.id, 'value': crypter.Decrypt(v.value)})
                    except (keyczar.errors.ShortCiphertextError, 
                            keyczar.errors.Base64DecodingError) as e:
                        return_key[key.name]['values'].append({'id': v.id, 'value': v.value})

                cache.set(cache_key, json.dumps(return_key), timeout=app.config['CACHE_DEFAULT_AGE_SECONDS'])

            else:
                try:
                    container = cconfig.get_container(path)
                except crudconfig.exceptions.NoResult:
                    flask.abort(404)
                all_containers = [container.id]
                all_values = dict()
                while container.parent is not None:
                    container = container.parent
                    if container is not None:
                        all_containers.append(container.id)
                for container in reversed(all_containers):
                    c = cconfig.get_container(container)
                    for key in c.keys:
                        if key.tag != request_tag and key.tag != app.config['DEFAULT_TAG']: continue
                        try:
                            if all_values[key.name]['tag'] != app.config['DEFAULT_TAG']: continue
                        except KeyError:
                            pass
                        all_values[key.name] = {'values': list(),
                                           'tag': key.tag, 
                                           'id': key.id }
                        for value in key.values:
                            try:
                                all_values[key.name]['values'].append({'id': value.id, 'value': crypter.Decrypt(value.value)})
                            except (keyczar.errors.ShortCiphertextError, 
                                    keyczar.errors.Base64DecodingError) as e:
                                all_values[key.name]['values'].append({'id': value.id, 'value': value.value})


                cache.set(cache_key, json.dumps(all_values), timeout=app.config['CACHE_DEFAULT_AGE_SECONDS'])

        cache.delete("loading-" + cache_key)
        cache_result = cache.get(cache_key)
    return cache_result

def get_clear():
    if app.config['DEBUG'] is True:
        cache.clear()
        app.logger.debug("cleared the cache")
        return "cleared\n"
    else:
        flask.abort(404)