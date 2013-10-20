from sqlalchemy import Table, Column, MetaData, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy import String, Integer, Unicode, UnicodeText, Sequence
from crudconfig import Base

class Key(Base):
    __tablename__ = "keys"

    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    key = Column(Unicode(128), nullable=False, index=True)
    container_id = Column(Integer, nullable=False, index=True)
    tag = Column(Unicode(128), nullable=False, index=True)
    added = DateTime()
    updated = DateTime()

    __table_args__ = (ForeignKeyConstraint(['container_id'],['containers.id']),
                      UniqueConstraint('key', 'container_id', 'tag', name="keyval_idx_key_container_tag_uc"))

    def __init__(self, key, value, container_id, tag=None):
        self.key = unicode(key)
        self.value = unicode(value) 
        self.container_id = int(container_id)
        self.tag = unicode(tag.upper())

    def __repr__(self):
        return "<Key('%s','%s', '%d', '%s')>" % ( unicode(self.key), self.container_id, unicode(self.tag))