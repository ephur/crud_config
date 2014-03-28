from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

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
