from crud_config import db
from crud_config.models import *

class CacheTags(db.Model):
    """
    Contains tags that belong to a cache reference
    """

    __tablename__ = "cachetags"


    id = db.Column(db.Integer, primary_key=True)
    cache_id = db.Column(db.String(128),
                         db.ForeignKey("cachereference.cache_id", ondelete='CASCADE'),
                         nullable=False, index=True)
    tag_id = db.Column(db.Integer(), nullable=True, index=True)
    tag_name = db.Column(db.Unicode(128), nullable=True, index=True)

    def __init__(self, cache_id, tag_id=None, tag_name=None):
        self.cache_id = cache_id
        self.tag_id = tag_id
        self.tag_name = tag_name

    def __repr__(self):
        return "<Cachetags('{0:s}', '{1:s}')>".format(str(self.cache_id),
                                                             unicode(self.tag_name))