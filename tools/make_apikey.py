#!/usr/bin/env python
import sys
import uuid
from crud_config import db
from crud_config.models import *

apikey = str(uuid.uuid4())
key = ApiKey(apikey,'test-owner',valid=True, write=False)
print "The API Key is: %s" %(apikey)
db.session.add(key)
db.session.commit()
