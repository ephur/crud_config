import flask
from flask import Flask, render_template, request, g
from werkzeug.contrib.cache import MemcachedCache
from time import sleep
from random import random
import crudconfig

app = Flask(__name__)
app.config.from_object('config')
cache_servers=app.config['MEMCACHE_SERVERS'].split(",")
cache = MemcachedCache(cache_servers)


@app.route("/", methods=['GET'], defaults={'path': ''})
@app.route('/<path:path>', methods=['GET'])
def api_get(path):
    key = path + "?" + "&".join(["%s=%s" % (k, v) for k, v in request.args.iteritems()])
    loadkey = "loading-" + key
    cache_result = cache.get(key)
    loops = 0
    while cache_result is None:
        loops += 1
        app.logger.debug("%s is not cached, checked %d times" % (key, loops))
        sleeptime = random() / 10
        sleep(sleeptime)
        if cache.get("loading-" + key) is None and cache.get(key) is None:
            cache.set("loading-" + key, "True")
            app.logger.debug("I'm doing the loading after a sleep of %f seconds" % (sleeptime))
            cconfig = crudconfig.CrudConfig(keypath=app.config['KEYPATH'], 
                                            db_name=app.config['DATABASE_DB'],
                                            db_username=app.config['DATABASE_USER'],
                                            db_password=app.config['DATABASE_PASS'],
                                            db_host=app.config['DATABASE_HOST'])
            containers = cconfig



    return "\n".join(cache_result)


@app.route("/clear", methods=['GET'])
def clear_cache():
    if app.config['DEBUG'] is True:
        cache.clear()
        app.logger.debug("cleared the cache")
        return "cleared\n"
    else:
        flask.abort(404)