from crud_config import db
from crud_config.models import *


class ApiKey(db.Model):
    """
    API Keys can be used to authenticate a client before giving them
    decrypted/private data
    """
    __tablename__ = "apikeys"

    id = db.Column(db.Integer, db.Sequence('apikeys_id_seq'), primary_key=True)
    api_key = db.Column(db.UnicodeText, nullable=False)
    valid = db.Column(db.Boolean)
    owner = db.Column(db.Unicode(128), nullable=True)
    write = db.Column(db.Boolean, default=False, server_default='0')

    def __init__(self, api_key, owner, valid=True):
        self.api_key = unicode(api_key)
        self.owner = unicode(owner)
        self.valid = int(valid)
        self.write = int(write)

    def __repr__(self):
        return "<ApiKey('%s','%s', '%d', %d')>" % (
            self.api_key,
            self.owner,
            self.valid,
            self.write)