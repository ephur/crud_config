from crud_config import db
from crud_config.models import *
import crud_config

class CacheReference(db.Model):
    """
    The cache reference is for looking up items that are cached, to lighten database load
    """

    __tablename__ = "cachereference"

    cache_id = db.Column(db.String(128), unique=True, nullable=False, index=True, primary_key=True)
    type = db.Column(db.String(16), nullable=False, index=True)
    uri = db.Column(db.UnicodeText(8332), nullable=True)
    added = db.DateTime(timezone="true")

    child_containers = db.relationship("CacheContainers",
                                       cascade='all, delete-orphan',
                                       passive_deletes=True,
                                       backref=db.backref('parent', remote_side=[cache_id]))
    child_tags = db.relationship("CacheTags",
                                 cascade='all, delete-orphan',
                                 passive_deletes=True,
                                 backref=db.backref('parent', remote_side=[cache_id]))
    child_keys = db.relationship("CacheKeys",
                                 cascade='all, delete-orphan',
                                 passive_deletes=True,
                                 backref=db.backref('parent', remote_side=[cache_id]))
    child_values = db.relationship("CacheValues",
                                 cascade='all, delete-orphan',
                                 passive_deletes=True,
                                 backref=db.backref('parent', remote_side=[cache_id]))

    def __init__(self, cache_id, type, **kwargs):
        self.cache_id = cache_id
        try:
            if type.upper() == "PAGE":
                self.type = "PAGE"
            elif type.upper() == "TREE":
                self.type = 'TREE'
            else:
                raise ValueError('value must be page or tree')
        except (TypeError, AttributeError) as e:
            raise TypeError('value must be string type')

        db.session.add(self)
        for item in kwargs:
            print item,"=",kwargs[item]
            try:
                if item.upper() == 'CONTAINERS':
                    print item.upper()
                    for container in kwargs[item]:
                        db.session.add(crud_config.models.cachecontainers.CacheContainers(
                                           self.cache_id,
                                           container['id'],
                                           unicode(container['name'])))
            except AttributeError as e:
                raise

        db.session.commit()

    def __repr__(self):
        return "<CacheReference('%s', '%s', '%s')>" % (
            str(self.cache_id),
            str(self.uri),
            str(self.type))