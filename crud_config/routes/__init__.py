import flask
from crud_config import app

import crud_config.util as util
from crud_config.error_handlers import error
import gets
import puts
import posts
import deletes
import purge


# Need to do an auth lookup on any and all requests
@app.before_request
def before_request():
    try:
        auth = ("APIKEY", flask.request.headers['X-API-Auth'])
    except KeyError as e:
        try:
            auth = ("LDAP", flask.request.headers['X-SSO-Auth'])
        except KeyError as e:
            return(error(
                   403,
                   "authentication headers not provided",
                   validheaders=['X-API-Auth', 'X-SSO-Auth']))
    if util.checkAuth(auth) is not True:
        return(error(403, "invalid authentication informationed provided"))


# The catch all for GET requests. This will cover the majority of
# gets that come through this API.
@app.route("/", methods=['GET'], defaults={'path': ''})
@app.route('/<path:path>', methods=['GET'])
def get_index(path):
    return gets.get_main(path)


# Catch all for put methods, these update existing keys/values
@app.route("/", methods=['PUT'], defaults={'path': ''})
@app.route('/<path:path>', methods=['PUT'])
def put_index(path):
    return puts.put_main(path)


# Catch all for post methods, these add new containers/keys/values
@app.route("/", methods=['POST'], defaults={'path': ''})
@app.route('/<path:path>', methods=['POST'])
def post_index(path):
    return posts.post_main(path)


# Catch all for deletes, these remove containers/keys/values
@app.route("/", methods=['DELETE'], defaults={'path': ''})
@app.route('/<path:path>', methods=['DELETE'])
def delete_index(path):
    return deletes.delete_main(path)

################################
# All of the operations routes #
################################
@app.route("/operations/container/list/", methods=['GET'], defaults={'path': ''})
@app.route("/operations/container/list/<path:path>", methods=['GET'])
def get_list(path):
    return gets.get_list(path)

# Copy a TAG
@app.route("/operations/tag/copy", methods=['PUT'])
def put_copytag():
    return puts.copytag()


# When running in debug mode, allow a caller to GET /clear
# in order to empty the cache.
@app.route("/operations/cache/clear", methods=['GET'])
def clear_cache():
    return gets.get_clear()

@app.route("/operations/container/content/", methods=['GET'], defaults={'path': ''})
@app.route("/operations/container/content/<path:path>", methods=['GET'])
def get_content(path):
    return gets.get_content(path)



