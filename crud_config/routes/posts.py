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
from purge import purge


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
        raise
        return(error(
               400,
               "keyvals JSON should be a list of JSON dictionaries",
               processed_so_far=return_data))
    return return_data
