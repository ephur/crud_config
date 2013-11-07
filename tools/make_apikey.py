#!/usr/bin/env python
import sys
import uuid
from crud_config import db
from crud_config.models import *

db.create_all()
apikey = str(uuid.uuid4())
key = ApiKey(apikey,'test-owner',valid=True)
print "The API Key is: %s" %(apikey)
db.session.add(key)
db.session.commit()
