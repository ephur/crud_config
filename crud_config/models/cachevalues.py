from crud_config import db
from crud_config.models import *

class CacheValues(db.Model):
    """
    Contains values that belong to a cache reference
    """

    __tablename__ = "cachevalues"

    cache_id = db.Column(db.String(128),
                         db.ForeignKey("cachereference.cache_id", ondelete='CASCADE'),
                         nullable=False, index=True, primary_key=True)
    value_id = db.Column(db.Integer(), nullable=True, index=True)
    value_name = db.Column(db.Unicode(128), nullable=True, index=True)

    def __init__(self, cache_id, value_id=None, value_name=None):
        self.cache_id = cache_id
        self.value_id = value_id
        self.value_name = value_name

    def __repr__(self):
        return "<Cachevalues('{0:s}', '{1:s}', {2:d})>".format(str(self.cache_id),
                                                             unicode(self.value_name),
                                                             int(self.value_id))