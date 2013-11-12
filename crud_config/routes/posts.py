import flask
import simplejson as json
import crud_config
import crud_config.crud.retrieve as ccget
import crud_config.crud.update as ccput
import crud_config.crud.delete as ccdelete
import crud_config.crud.create as ccpost
import crud_config.exceptions as ce

from crud_config.error_handlers import error
from crud_config import app
from werkzeug.contrib.cache import MemcachedCache


def post_main(path):
    # A function that matches post_process_{valid_key} must exist
    valid_keys = ['containers', 'keyvals']
    try:
        container = ccget.get_container(path)
    except ce.noResult:
        return(error(
               404,
               "Container you want to post to is not found",
               requested_container_tree=" -> ".join(path.split("/"))))

    # Check the validity of request
    if len(flask.request.args) > 0:
        return(error(
               400,
               "POST requests should not have querystring params",
               querystring_params=flask.request.args))

    # Load the JSON data, and validate it
    try:
        request_data = json.loads(flask.request.get_data())
    except json.JSONDecodeError as e:
        return(error(
               400,
               "JSON Data is invalid",
               escaped_data_submitted=flask.request.get_data(), 
               parsing_error=e.message))

    # Check for invalid keys
    for key in sorted(request_data.keys()):
        if key not in valid_keys:
            return(error(
                   400,
                   "JSON contained bad key",
                   errored_on_key=key))

    return_data = list()
    for key in valid_keys:
        try:
            local_data = request_data[key]
        except (KeyError) as e:
            continue
        return_data = globals()["post_process_" + key](
            local_data,
            container_id=container.id,
            processed_so_far=return_data)

        # Return data will become a TUPLE if there was a processing error, in
        # which case we need to return this back up the stack
        if type(return_data) is tuple:
            return return_data

    # Time to clean up the caches...
    #post_invalidate_cache(path, request_data)
    purge(path, request_data)
    return json.dumps({"results": return_data})


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
        base_path = base_path + "/" + path_parts.pop(0)
        purge_keys.append(base_path)

    # Generate the URI's to purge based on the keyvals updated
    try:
        keyvals = params['keyvals']
    except KeyError as e:
        keyvals = list()
        pass

    # Purge the container level items for the containers updated
    for item in containers:
        purge_keys.append(base_path + "/" + item['name'])
        purge_keys.append(base_path + "/OPERATIONS/LIST/" + base_path + "/" + item['name'])
        purge_keys.append(base_path + "/OPERATIONS/LIST/" + base_path + "/" + item['name'] + "?RECURSIVE=TRUE")

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

def post_process_containers(data, **kwargs):
    cid = kwargs['container_id']
    return_data = kwargs['processed_so_far']
    try:
        for container in data:
            try:
                name = container['name']
            except TypeError as e:
                return(error(
                       400,
                       "containers JSON should be a list of JSON"
                       " dictionaries, and yours is not",
                       processed_so_far=return_data))
            except KeyError as e:
                return(error(
                       400,
                       "unable to add container, forgot to specify name!",
                       processed_so_far=return_data))
            try:
                desc = container['description']
            except KeyError:
                desc = None

            try:
                return_data.append("Created:" +
                                   str(ccpost.add_container(
                                       cid,
                                       name,
                                       desc)))
            except ce.notUnique:
                return_data.append("Container Not Added, Already Exists: %s" %
                                   (name))

    except TypeError as e:
        return(error(
               400,
               "containers JSON should be a list of JSON dictionaries",
               processed_so_far=return_data),
               True)

    return return_data

def post_process_keyvals(data, **kwargs):
    cid = kwargs['container_id']
    return_data = kwargs['processed_so_far']
    try:
        for keyval in data:
            try:
                key = keyval['key']
            except TypeError as e:
                return(error(
                       400,
                       "containers JSON should be a list of JSON dictionaries",
                       processed_so_far=return_data))
            except KeyError as e:
                return(error(
                       400,
                       "must specify key name for all keyvals",
                       processed_so_far=return_data))

            try:
                value = keyval['value']
            except KeyError as e:
                return(error(
                       400,
                       "must specify value for all keyvals",
                       processed_so_far=return_data))

            try:
                tag = keyval['tag']
            except KeyError as e:
                tag = None

            return_data.append("Created:" + str(
                               ccpost.add_keyval(cid, key, value, tag)))

    except TypeError as e:
        return(error(
               400,
               "keyvals JSON should be a list of JSON dictionaries",
               processed_so_far=return_data))
    return return_data
