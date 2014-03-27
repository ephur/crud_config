from crud_config import db
from crud_config.models import *
from datetime import datetime
import simplejson as json

class CacheKey(db.Model):
    """
    API Keys can be used to authenticate a client before giving them
    decrypted/private data
    """
    __tablename__ = "cachekeys"

    id = db.Column(db.Integer, db.Sequence('cachekeys_id_seq'), primary_key=True)
    cache_key = db.Column(db.UnicodeText, nullable=False)
    containers = db.Column(db.Unicode(1024), index=True)
    keys = db.Column(db.unicode(1024), index=True)
    created = db.Column(db.DateTime, default=datetime.utcnow())

    def __init__(self, cache_key, containers, keys):
        self.cache_key = unicode(cache_key)
        self.containers = unicode(json.dumps(containers))
        self.keys = unicode(json.dumps(keys))

    def __repr__(self):
        return "<CacheKey('%s','%s', '%s')>" % (
            self.cache_key,
            self.containers,
            self.keys
        )