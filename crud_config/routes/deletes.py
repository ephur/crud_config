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
from cacheops import purge

def delete_main(path):
    valid_keys = ['containers', 'keyvals']
    try:
        container = ccget.get_container(path)
    except ce.noResult:
        return(error(
               404,
               "Container you want to delete from is not found",
               requested_container_tree=" -> ".join(path.split("/"))))

    # Check the validity of request
    if len(flask.request.args) > 0:
        return(error(
               400,
               "DELETE requests should not have querystring params",
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
        return_data = globals()["delete_process_" + key](
            local_data,
            container_id=container.id,
            processed_so_far=return_data,
            path=path)

        # Return data will become a TUPLE if there was a processing error, in
        # which case we need to return this back up the stack
        if type(return_data) is tuple:
            return return_data

    # Time to clean up the caches...
    # post_invalidate_cache(path, request_data)
    purge(path, request_data)
    return json.dumps({"results": return_data})

def delete_process_containers(data, **kwargs):
    path = kwargs['path']
    return_data = kwargs['processed_so_far']
    for container in data:
        killtainer = path + "/" + container['name']
        try:
            ccdelete.delete_container(killtainer)
            return_data.append("Deleted %s" % (killtainer) )
        except ce.noResult as e:
            return_data.append("Can't delete %s, it doesn't exist!" % (killtainer) )
    return return_data

def delete_process_keyvals(data, **kwargs):
    path = kwargs['path']
    return_data = kwargs['processed_so_far']
    for keyval in data:
        try:
            key = keyval['key']
        except KeyError:
            return_data.append("must provide a key to delete (got %s)" % str(keyval))
            continue

        try:
            tag = keyval['tag']
        except KeyError as e:
            tag = app.config['DEFAULT_TAG']

        try:
            val = keyval['value']
        except:
            val = None
        try:
            ccdelete.delete_key(path, key, value=val, tag=tag)
            return_data.append("Deleted %s in %s with tag %s" % (key, path, tag))
        except ce.noResult as e:
            return_data.append("Can't delete %s in %s with tag %s, can't find container or value"  %(key, path, tag))

    return return_data