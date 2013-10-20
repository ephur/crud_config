from sqlalchemy import *
from sqlalchemy.orm import *
from crudconfig import Base

class Value(Base):
    __tablename__ = "values"

    id = Column(Integer, Sequence('value_id_seq'), primary_key=True)
    key_id = Column(Integer, ForeignKey('keys.id'), nullable=False, index=True)
    value = Column(UnicodeText, nullable=False)
    added = DateTime()
    updated = DateTime()

    __table_args__ = (UniqueConstraint('key_id', 'value', name="key_id_value_uc"),
                     )

    def __init__(self, key, value, container_id, tag=None):
        self.key = unicode(key)
        self.value = unicode(value) 
        self.container_id = int(container_id)
        self.tag = unicode(tag.upper())

    def __repr__(self):
        return "<Value('%d', '%s')>" % ( int(self.key_id), unicode(self.value) )