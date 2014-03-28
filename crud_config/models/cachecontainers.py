from crud_config import db
from crud_config.models import *

class CacheContainers(db.Model):
    """
    Contains containers that belong to a cache reference
    """

    __tablename__ = "cachecontainers"

    cache_id = db.Column(db.String(128),
                         db.ForeignKey("cachereference.cache_id", ondelete='CASCADE'),
                         nullable=False, index=True, primary_key=True)
    container_id = db.Column(db.Integer(), nullable=True, index=True)
    container_name = db.Column(db.Unicode(128), nullable=True, index=True)
    order = db.Column(db.Integer(32), nullable=True)

    def __init__(self, cache_id, container_id=None, container_name=None, order=None):
        self.cache_id = cache_id
        self.container_id = container_id
        self.container_name = container_name
        self.order=order

    def __repr__(self):
        return "<CacheContainers('{0:s}', '{1:s}', {2:d}, {3:d})>".format(str(self.cache_id),
                                                                          unicode(self.container_name),
                                                                          int(self.container_id),
                                                                          int(self.order))