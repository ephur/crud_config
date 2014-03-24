#!/usr/bin/env python
import sys
from crud_config import app
from crud_config import db
from crud_config.models import *

from alembic.config import Config
from alembic import command

print "Using DATABASE URI: %s" % (app.config['SQLALCHEMY_DATABASE_URI'])

db.create_all()
container = Container.query.filter_by(name=unicode('root')).first()
if container is None:
    row = Container(unicode('root'), unicode('The GLOBAL/ROOT container'), None);
    db.session.add(row)
    result = db.session.commit()
    print "Added root container."
else:
    print "Root container already exists."

from alembic.config import Config
from alembic import command
alembic_cfg = Config("alembic.ini")
command.stamp(alembic_cfg, "head")