from crud_config import db
from crud_config.models import *
import datetime

class Key(db.Model):
    """
    A key is tagged, and lives inside of a container. A key is a container
    for values, a key lives in a single container, and is unique combined
    with a tag.
    """
    __tablename__ = "keys"

    id = db.Column(db.Integer, db.Sequence('key_id_seq'), primary_key=True)
    name = db.Column(db.Unicode(128), nullable=False, index=True)
    container_id = db.Column(db.Integer,
                          db.ForeignKey("containers.id", ondelete='CASCADE'),
                          nullable=False,
                          index=True)
    tag = db.Column(db.Unicode(128), nullable=False, index=True)
    values = db.relationship("Value",
                             cascade='all, delete-orphan',
                             passive_deletes=True,
                             backref=db.backref('key', remote_side=[id]))
    added = db.DateTime(timezone=True)
    updated = db.DateTime(timezone=True)

    __table_args__ = (db.UniqueConstraint('name',
                      'container_id',
                      'tag',
                      name="keyval_idx_name_container_tag_uc"),)

    def __init__(self, name, container_id, tag=None):
        self.name = unicode(name)
        self.container_id = int(container_id)
        self.tag = unicode(tag.upper())
        self.added = datetime.datetime.utcnow()
        self.updated = datetime.datetime.utcnow()

    def __repr__(self):
        return "<Key('%s', %d, '%s')>" % (
            unicode(self.name),
            int(self.container_id),
            unicode(self.tag))