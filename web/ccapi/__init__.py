import flask
from logging import Formatter

# Define the initial APP Object 
app = flask.Flask(__name__)
app.config.from_object('config')

# Import the other modules, must happen after the app object is declared
import ccapi.routes
import ccapi.error_handlers
import ccapi.util

# Setup better (parsable...) logging format
for item in app.logger.handlers:
    item.setFormatter(Formatter(
                      '%(asctime)s:%(levelname)s:%(message)s:'
                      '%(pathname)s[Line: %(lineno)d]'))