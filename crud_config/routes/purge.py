import flask
from crud_config import app
from werkzeug.contrib.cache import MemcachedCache

def purge(path, params):
    """
    This is to invalidate cache items that are submitted.
    """
    cache = MemcachedCache(app.config['MEMCACHE_SERVERS'].split(","))

    # Each of the containers so the top level containers can be purged
    path_parts = path.split("/")
    # The starting point for purge requests
    base_path = ""
    # Hold a list of the keys to purge
    purge_keys = []

    try:
        containers = params['containers']
    except KeyError as e:
        containers = list()
        pass

    # Purge keys for the items in the tree up to the final one submitted
    while len(path_parts) > 0:
        base_path = base_path + "/" + path_parts.pop(0).upper()
        purge_keys.append(base_path)

    # Generate the URI's to purge based on the keyvals updated
    try:
        keyvals = params['keyvals']
    except KeyError as e:
        keyvals = list()
        pass

    # Purge the container level items for the containers updated
    for item in containers:
        try:
            name = item['name']
        except TypeError:
            name = item
        purge_keys.append(base_path + "/" + name)
        purge_keys.append(base_path + "/operations/container/list" + base_path + "/" + name)
        purge_keys.append(base_path + "/operations/container/list" + base_path + "/" + name + "?RECURSIVE=TRUE")
        for i in range(app.config['TREE_MAX_RECURSION']):
            purge_keys.append(base_path + "/operations/container/list" + base_path + "/" +
                              name + "?DEPTH=%s" %(str(i)))
            purge_keys.append(base_path + "/operations/container/list" + base_path + "/" +
                              name + "?DEPTH=%s&RECURSIVE=TRUE" %(str(i)))


    # Purge all the keyvals in the container, with the proper tags (and for untagged items)
    for item in keyvals:
        param_path = base_path
        param_path = param_path + "?KEY=%s" % (item['key'].upper())
        purge_keys.append(param_path)
        try:
            purge_keys.append(param_path + "&TAG=" + item['tag'].upper())
        except KeyError as e:
            purge_keys.append(param_path + "&TAG=" + app.config['DEFAULT_TAG'])

    app.logger.debug("PURGING KEYS: %s" % ("|".join(purge_keys)))
    cache.delete_many(*purge_keys)
    return True