from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from logging.handlers import TimedRotatingFileHandler

import logging
import config

app = Flask(__name__)
app.config.from_object(config)
app.debug = app.config['DEBUG']


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://%s:%s@%s:%s/%s?' % (
                                         app.config['DATABASE_USER'],
                                         app.config['DATABASE_PASS'],
                                         app.config['DATABASE_HOST'],
                                         str(app.config['DATABASE_PORT']),
                                         app.config['DATABASE_DB'])
db = SQLAlchemy(app)

"""
Setup Logging
"""
file_handler = TimedRotatingFileHandler(app.config['LOG_FILE'],
                                        when="midnight",
                                        backupCount=app.config['LOG_COUNT'])
loglevel = getattr(logging, app.config['LOG_LEVEL'])
file_handler.setLevel(loglevel)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[called by %(funcName)s in %(pathname)s:%(lineno)d]'
))

# Add the handler to the application
app.logger.addHandler(file_handler)

# Add the handler to any libraries that log
for alog in ['sqlalchemy']:
    app.logger.debug("setting up logging for: %s" % alog)
    logger = logging.getLogger(alog)
    logger.addHandler(file_handler)