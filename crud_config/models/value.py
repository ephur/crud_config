from crud_config import db
from crud_config.models import *


class Value(db.Model):
    """
    Values are associated with keys, and stored encrypted.
    """
    __tablename__ = "values"

    id = db.Column(db.Integer, db.Sequence('value_id_seq'), primary_key=True)
    key_id = db.Column(db.Integer, db.ForeignKey('keys.id'),
                    nullable=False,
                    index=True)
    value = db.Column(db.Text, nullable=False)
    added = db.DateTime()
    updated = db.DateTime()

    def __init__(self, key, value):
        self.key_id = key
        self.value = unicode(value)

    def __repr__(self):
        return "<Value(%d, '%s')>" % (
            int(self.key_id),
            unicode(self.value))