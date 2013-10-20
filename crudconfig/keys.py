from sqlalchemy import *
from sqlalchemy.orm import *
from crudconfig import Base

class Key(Base):
    __tablename__ = "keys"

    id = Column(Integer, Sequence('key_id_seq'), primary_key=True)
    key = Column(Unicode(128), nullable=False, index=True)
    container_id = Column(Integer, ForeignKey("container.id"), nullable=False, index=True)
    tag = Column(Unicode(128), nullable=False, index=True)
    values = relationship("Value", backref="key")
    added = DateTime()
    updated = DateTime()

    __table_args__ = (UniqueConstraint('key', 'container_id', 'tag', name="keyval_idx_key_container_tag_uc"),
                     )

    def __init__(self, key, value, container_id, tag=None):
        self.key = unicode(key)
        self.value = unicode(value) 
        self.container_id = int(container_id)
        self.tag = unicode(tag.upper())

    def __repr__(self):
        return "<Key('%s','%s', '%s')>" % ( unicode(self.key), self.container_id, unicode(self.tag))