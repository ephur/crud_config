from crud_config import db
from crud_config.models import *

class CacheKeys(db.Model):
    """
    Contains keys that belong to a cache reference
    """

    __tablename__ = "cachekeys"

    cache_id = db.Column(db.String(128),
                         db.ForeignKey("cachereference.cache_id", ondelete='CASCADE'),
                         nullable=False, index=True, primary_key=True)
    key_id = db.Column(db.Integer(), nullable=True, index=True)
    key_name = db.Column(db.Unicode(128), nullable=True, index=True)

    def __init__(self, cache_id, key_id=None, key_name=None):
        self.cache_id = cache_id
        self.key_id = key_id
        self.key_name = key_name

    def __repr__(self):
        return "<Cachekeys('{0:s}', '{1:s}', {2:d})>".format(str(self.cache_id),
                                                             unicode(self.key_name),
                                                             int(self.key_id))