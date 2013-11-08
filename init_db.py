#!/usr/bin/env python
from crud_config import db
from crud_config.models import *
import sys

db.create_all()
container = Container.query.filter_by(name=unicode('root')).first()
if container is None:
  row = Container(unicode('root'), unicode('The GLOBAL/ROOT container'), None);
  db.session.add(row)
  db.session.commit()
