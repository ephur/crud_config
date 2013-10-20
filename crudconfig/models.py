from sqlalchemy import *
from sqlalchemy.orm import *
from crudconfig import Base

import datetime

''' Containers map to each level of the URI request, essentially a path in the URI ''' 
class Container(Base):
    __tablename__ = "containers"

    id = Column(Integer, Sequence('container_id_seq'), primary_key=True)
    name = Column(Unicode(64), nullable=False, index=True)
    description = Column(UnicodeText, nullable=True)
    parent_id = Column(Integer, nullable=False, index=True)
    keys = relationship("Key", backref='container')

    __table_args__ = (UniqueConstraint('name', 'parent_id', name="containers_idx_parent_name_uc"), 
                     )

    def __init__(self, name, description, parent_id):
        self.name = unicode(name)
        self.description = unicode(description)
        self.parent_id = parent_id

    def __repr__(self):
        return "<Container(%s', '%s', %d)>" % (unicode(self.name), unicode(self.description), self.parent_id)

''' A Key holds one or more values '''
class Key(Base):
    __tablename__ = "keys"

    id = Column(Integer, Sequence('key_id_seq'), primary_key=True)
    name = Column(Unicode(128), nullable=False, index=True)
    container_id = Column(Integer, ForeignKey("containers.id"), nullable=False, index=True)
    tag = Column(Unicode(128), nullable=False, index=True)
    values = relationship("Value", backref="key")
    added = DateTime(timezone=True)
    updated = DateTime(timezone=True)

    __table_args__ = (UniqueConstraint('name', 'container_id', 'tag', name="keyval_idx_name_container_tag_uc"),
                     )

    def __init__(self, name, container_id, tag=None):
        self.name = unicode(name)
        self.container_id = int(container_id)
        self.tag = unicode(tag.upper())
        self.added = datetime.datetime.utcnow()
        self.updated = datetime.datetime.utcnow()

    def __repr__(self):
        return "<Key('%s', %d, '%s')>" % (unicode(self.name), int(self.container_id), unicode(self.tag))

''' Values belong to keys ''' 
class Value(Base):
    __tablename__ = "values"

    id = Column(Integer, Sequence('value_id_seq'), primary_key=True)
    key_id = Column(Integer, ForeignKey('keys.id'), nullable=False, index=True)
    value = Column(UnicodeText, nullable=False)
    added = DateTime()
    updated = DateTime()

    def __init__(self, key, value):
        self.key_id = key
        self.value = unicode(value) 

    def __repr__(self):
        return "<Value(%d, '%s')>" % ( int(self.key_id), unicode(self.value) )