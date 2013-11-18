#!/usr/bin/env python
import sys
from crud_config import app
from crud_config import db
from crud_config.models import *

print app.config['SQLALCHEMY_DATABASE_URI']

print "hi"
db.create_all()
print "yo"
container = Container.query.filter_by(name=unicode('root')).first()
print container
if container is None:
  row = Container(unicode('root'), unicode('The GLOBAL/ROOT container'), None);
  db.session.add(row)
  result = db.session.commit()
  print result
