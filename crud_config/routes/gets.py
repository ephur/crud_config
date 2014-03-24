import flask
import crud_config.crud.retrieve as ccget
import crud_config.crud.update as ccput
import crud_config.crud.delete as ccdelete
import crud_config.crud.create as ccpost
import crud_config.exceptions as ce
import crud_config.util
from crud_config.error_handlers import error

import simplejson as json

from crud_config import app
from werkzeug.contrib.cache import MemcachedCache
from time import sleep
from random import random

cache_servers = app.config['MEMCACHE_SERVERS'].split(",")
cache = MemcachedCache(cache_servers)

def get_main(path):
    # This will handle all gets that are not otherwise defined.
    cache_key = "/" + path + "?" + "&".join(
        ["%s=%s" % (k.upper(), v.upper()) for k, v in sorted(
         flask.request.args.iteritems())])
    app.logger.debug("Using Cache Key: %s" % (cache_key))
    loadkey = "loading-" + cache_key
    cache_result = cache.get(cache_key)
    loops = 0
    # All get's are served up from the cache.
    while cache_result is None:
        # Keep track of loops, abort if it get's to be excessive, this may
        # need tuned later depending on how long DB operations take, right now
        # the number of wait loops is excessive
        loops += 1
        if loops > 50:
            return(error(
                   500,
                   message="item never became available in cache",
                   debug="%d: %s" % (loops, cache_key)))
        app.logger.debug("%s is not cached, checked %d times" %
                         (cache_key, loops))
        sleeptime = random() / 100
        sleep(sleeptime)
        # For other threads that might be requesting the same thing, announce
        # to the cache that we're processing this page, help to eliminate
        # overloading during bursts for the same key.
        if ((cache.get("loading-" + cache_key) is None and
             cache.get(cache_key) is None)):

            # Announce we're loading to the cache
            cache.set("loading-" + cache_key, "True",
                      timeout=app.config['CACHE_LOCKING_SECONDS'])
            # Set values for the request
            request_tag = app.config['DEFAULT_TAG']
            request_return = "VALUES"
            request_key = None
            for (k, v) in flask.request.args.iteritems():
                if k.upper() == "TAG":
                    request_tag = v.upper()
                elif k.upper() == "KEY":
                    request_key = v.lower()
                elif k.upper() == "RETURN":
                    request_return = v.upper()
                else:
                    # Clean up known query string params, avoid cachebusting
                    # and make clearing the cache possible for posts/puts
                    return(error(
                           400,
                           "client error",
                           "invalid query string parameters",
                           key=k,
                           value=v,
                           path=cache_key))

            app.logger.debug(
                "I'm doing the loading after a sleep of %f seconds" %
                (sleeptime))

            # Can't request a key in conjuction with some request_return types
            if request_key is not None and request_return is not "VALUES":
                return(error(
                       400,
                       "client error",
                       "paramater conflict",
                       message="%s can't be return value when requesting a single key" %(request_return),
                       ))

            if request_key is not None:
                # A single Key is requested
                try:
                    key = ccget.get_key(path, request_key, tag=request_tag)
                except ce.noResult:
                    return error(404, "key not found", requested_key=request_key, requested_container=path, applied_tag=request_tag)

                return_key = {key.name: {"values": list()}}
                return_key[key.name]['tag'] = key.tag
                # @TODO: Fix date added/date updated
                # return_key['added'] = key.added
                # return_key['updated'] = key.updated

                for v in key.values:
                    return_key[key.name]['values'].append(
                            {'id': v.id, 'value': v.value } )

                cache.set(cache_key,
                          json.dumps(return_key),
                          timeout=app.config['CACHE_DEFAULT_AGE_SECONDS'])

            else:
                try:
                    container = ccget.get_container(path)
                except ce.noResult:
                    return error(404, "container not found", requested_container=path)

                # Process a container list
                if request_return == "ALL" or request_return == "CONTAINERS":
                    child_containers = list()
                    all_child_containers = dict()
                    app.logger.debug(request_return)
                    for child_container in container.children:
                        child_containers.append(path + "/" + child_container)
                        app.logger.debug(all_child_containers)
                    for child_container in child_containers:
                        c = ccget.get_container(child_container)
                        all_child_containers[c.name] = { "description": c.description,
                                                         "id": c.id }

                # Process a value list
                if request_return == "ALL" or request_return =="VALUES":
                    all_containers = [container.id]
                    all_values = dict()
                    while container.parent is not None:
                        container = container.parent
                        if container is not None:
                            all_containers.append(container.id)

                    for container in reversed(all_containers):
                        c = ccget.get_container(container)
                        for key in c.keys:
                            if ((key.tag != request_tag and
                                 key.tag != app.config['DEFAULT_TAG'])):
                                continue
                            try:
                                if ((all_values[key.name]['tag'] !=
                                     app.config['DEFAULT_TAG'])):
                                    continue
                            except KeyError:
                                pass
                            all_values[key.name] = {'values': list(),
                                                    'tag': key.tag,
                                                    'id': key.id}
                            for value in key.values:
                                all_values[key.name]['values'].append(
                                    {'id': value.id, 'value': value.value })
                if request_return == "ALL":
                    return_hash = { "containers": all_child_containers, 
                                    "key_values": all_values }

                elif request_return == "CONTAINERS":
                    return_hash = all_child_containers

                elif request_return == "VALUES":
                    return_hash = all_values

                else:
                    return(error(400,
                                 "client_error",
                                 "invalid paramater value",
                                 key=k,
                                 value=v,
                                 path=cache_key))


                cache.set(cache_key,
                          json.dumps(return_hash),
                          timeout=app.config['CACHE_DEFAULT_AGE_SECONDS'])

        cache.delete("loading-" + cache_key)
        cache_result = cache.get(cache_key)
    return cache_result

def get_list(path):
    """
    This will return a list of all containers inside of another 
    container

    Setting ?recursive=true will get all the child containers,
    until there are no more children and provide a full container
    tree
    """
    cache_key = "/operations/container/list/" + path + "?" + "&".join(
        ["%s=%s" % (k.upper(), v.upper()) for k, v in sorted(
         flask.request.args.iteritems())])
    app.logger.debug("Using Cache Key: %s" % (cache_key))
    loadkey = "loading-" + cache_key
    cache_result = cache.get(cache_key)
    loops = 0
    while cache_result is None:
        loops += 1
        if loops > 50:
            return error(500,
                         message="item never became available in cache",
                         debug="%d: %s" % (loops, cache_key))
        app.logger.debug("%s is not cached, checked %d times" %
                         (cache_key, loops))
        sleeptime = random() / 10
        sleep(sleeptime)
        if ((cache.get("loading-" + cache_key) is None and
            cache.get(cache_key) is None)):

            cache.set("loading-" + cache_key, "True",
                      timeout=app.config['CACHE_LOCKING_SECONDS'])
            request_recursive = False
            max_recursion = int(app.config['TREE_MAX_RECURSION'])

            request_key = None
            request_val = None
            for (k, v) in flask.request.args.iteritems():
                if k.upper() == "DEPTH":
                    try:
                        max_recursion = int(v)
                    except ValueError as e:
                        return error(400,
                                     "client_error",
                                     "invalid querystring",
                                     recursion_depth="%s does not appear to be" +
                                      " an integer" % (v))

                elif k.upper() == "RECURSIVE":
                    try:
                        request_recursive = crud_config.util.toBool(v)
                    except ValueError as e:
                        return error(400,
                                     "client error",
                                     "invalid querystring",
                                     recursion_request_value=v)

                elif k.upper() == "KEY":
                    request_key = v.lower()

                elif k.upper() == "VALUE":
                    request_val = v.lower()

                else:
                    return error(400,
                                 "client error",
                                 "invalid query string",
                                 key=k,
                                 value=v,
                                 path=cache_key
                                 )
            app.logger.debug("loading %s after %f seconds wait" % (cache_key, sleeptime))
            try:
                container = ccget.get_container(path)
            except ce.noResult as e:
                return error(404,
                             "container not found",
                             container=path)

            if request_recursive is True and request_key is None:
                #app.logger.debug("recursive with NO key")
                cache.set(cache_key,
                          json.dumps(container.dumptree(max_recursion=max_recursion)),
                          timeout=app.config['CACHE_DEFAULT_AGE_SECONDS'])

            elif request_recursive is True and request_key is not None and request_val is None:
                #app.logger.debug("recursive with key")
                cache.set(cache_key,
                          json.dumps(container.dumptree_with_key(max_recursion=max_recursion, key=request_key)),
                          timeout=app.config['CACHE_DEFAULT_AGE_SECONDS'])

            elif request_recursive is True and request_key is not None and request_val is not None:
                #app.logger.debug("recursive with key and val")
                cache.set(cache_key,
                         json.dumps(container.dumptree_with_key_val(max_recursion=max_recursion, key=request_key, r_val=request_val)),
                         timeout=app.config['CACHE_DEFAULT_AGE_SECONDS'])


            else:
                cache.set(cache_key,
                          json.dumps([x for x in container.children.keys()]),
                          timeout=app.config['CACHE_DEFAULT_AGE_SECONDS'])

        cache.delete("loading-" + cache_key)
        cache_result = cache.get(cache_key)
    return cache_result


def get_content(path):
    """
    This will return a dict of the content in containers matching key or key and value provided
    in arguments.

    """
    cache_key = "/operations/container/content/" + path + "?" + "&".join(
        ["%s=%s" % (k.upper(), v.upper()) for k, v in sorted(
         flask.request.args.iteritems())])
    app.logger.debug("Using Cache Key: %s" % (cache_key))
    loadkey = "loading-" + cache_key
    cache_result = cache.get(cache_key)
    loops = 0
    while cache_result is None:
        loops += 1
        if loops > 70:
            return error(500,
                         message="item never became available in cache",
                         debug="%d: %s" % (loops, cache_key))
        app.logger.debug("%s is not cached, checked %d times" %
                         (cache_key, loops))
        sleeptime = random() / 10
        sleep(sleeptime)
        if ((cache.get("loading-" + cache_key) is None and
            cache.get(cache_key) is None)):

            cache.set("loading-" + cache_key, "True",
                      timeout=app.config['CACHE_LOCKING_SECONDS'])
            request_recursive = False
            max_recursion = int(app.config['TREE_MAX_RECURSION'])

            request_key = None
            request_val = None
            for (k, v) in flask.request.args.iteritems():
                if k.upper() == "KEY":
                    request_key = v.lower()

                elif k.upper() == "VALUE":
                    request_val = v.lower()

                else:
                    return error(400,
                                 "client error",
                                 "invalid query string",
                                 key=k,
                                 value=v,
                                 path=cache_key
                                 )
            app.logger.debug("loading %s after %f seconds wait" % (cache_key, sleeptime))
            # Check that key is provided
            if request_key == None:
                return error(400,
                             "client error",
                             "No key provided"
                            )
            try:
                container = ccget.get_container(path)
            except ce.noResult as e:
                return error(404,
                             "container not found",
                             container=path)

            if request_key is not None and request_val is None:
                #app.logger.debug("No key")
                return_hash = dict()
                a = container.dumptree_with_key(max_recursion=max_recursion, key=request_key, container_id=True)
                for container in a:
                    c = ccget.get_container(container)
                    all_values = dict()
                    for key in c.keys:
                        all_values[key.name] = {'values': list()}

                        for value in key.values:
                            #all_values[key.name]['values'].append({'value': value.value})
                            all_values[key.name]['values'].append(value.value)

                    return_hash[c.name]= all_values

                cache.set(cache_key,
                          json.dumps(return_hash),
                          timeout=app.config['CACHE_DEFAULT_AGE_SECONDS'])

            elif request_key is not None and request_val is not None:
                #app.logger.debug("Given key")
                return_hash = dict()
                a = container.dumptree_with_key_val(max_recursion=max_recursion, key=request_key, r_val=request_val, container_id=True)
                for container in a:
                    c = ccget.get_container(container)
                    all_values = dict()
                    for key in c.keys:
                        all_values[key.name] = {'values': list()}

                        for value in key.values:
                            #app.logger.debug(key.values)
                            #all_values[key.name]['values'].append({'value': value.value})
                            all_values[key.name]['values'].append(value.value)

                    return_hash[c.name]=all_values

                cache.set(cache_key,
                          json.dumps(return_hash),
                          timeout=app.config['CACHE_DEFAULT_AGE_SECONDS'])

            ## Shouldn't get here fix or error
            else:
                app.logger.debug("Should not get here!")
                cache.set(cache_key,
                          json.dumps([x for x in container.children.keys()]),
                          timeout=app.config['CACHE_DEFAULT_AGE_SECONDS'])

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