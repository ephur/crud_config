import flask
from ccapi import app

import gets

# The catch all for GET requests. This will cover the majority of 
# gets that come through this API. 
@app.route("/", methods=['GET'], defaults={'path': ''})
@app.route('/<path:path>', methods=['GET'])
def get_index(path):
    return gets.get_main(path)

# When running in debug mode, allow a caller to GET /clear
# in order to empty the cache.
@app.route("/clear", methods=['GET'])
def clear_cache():
    return gets.get_clear()