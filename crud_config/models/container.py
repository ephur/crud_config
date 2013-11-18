from crud_config import db
from crud_config.models import *
from sqlalchemy.orm.collections import attribute_mapped_collection


class Container(db.Model):
    """
    Containers contain keys, and can be organized pointing to each other
    """
    __tablename__ = "containers"
    __table_args__ = (db.UniqueConstraint('name',
                                       'parent_id',
                                       name="containers_idx_parent_name_uc"),)

    id = db.Column(db.Integer, db.Sequence('container_id_seq'), primary_key=True)
    name = db.Column(db.Unicode(64), nullable=False, index=True)
    description = db.Column(db.UnicodeText, nullable=True)
    parent_id = db.Column(db.Integer,
                       db.ForeignKey('containers.id',
                                     ondelete='CASCADE'),
                       index=True)
    keys = db.relationship("Key",
                           backref='container',
                           passive_deletes=True)
    children = db.relationship("Container",
                            passive_deletes=True,
                            backref=db.backref('parent', remote_side=[id]),
                            collection_class=attribute_mapped_collection('name'))


    def __init__(self, name, description, parent_id):
        self.name = unicode(name)
        self.description = unicode(description)
        self.parent_id = parent_id

    def __repr__(self):
        return "<Container(%s', '%s', %s)>" % (
            unicode(self.name),
            unicode(self.description),
            int(self.parent_id))

    def dumptree(self, max_recursion=10, recursed=0):
        """
        dump tree provides a recursive dictionary starting at the container which
        this method is called on. inner should never be called by an external caller,
        it's merely used to support recursion on this method
        """
        values = { self.name: { } }
        if recursed >= max_recursion:
            return { }

        if len(self.children.values()) > 0:
            for c in self.children.values():
                values[self.name][c.name] = c.dumptree(recursed=recursed + 1,max_recursion=max_recursion)

        if recursed == 0:
            return values
        return values[self.name]