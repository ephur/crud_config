import flask

app = flask.Flask(__name__)
app.config.from_object('config')

import ccapi.routes
import ccapi.error_handlers
import ccapi.util