import flask
from crud_config import app
from crud_config import db
from crud_config.models import *
import sqlalchemy.orm.exc as sqlormerrors
import crud_config.exceptions as ce
import retrieve as ccget
import delete as ccdelete

def update_key(container, name, new_name, tag=None):
    """ Change the name of a key

    :param container: container to change key in (required)
    :param name: name of key to change (required)
    :param new_name: what to rename key to (required)
    :param tag: match key with this tag
                (optional: default __class__.default_key)
    """
    pass

def update_keyval(container_path, key, value, tag=None):
    """ Set the value of a key

    :param container_path: path to container to change key in (required)
    :param key: the name of the key to set value for (required)
    :param value: the value to set the key equal to (required)
    :param tag: the tag for the key to update (optional)
    """
    # container = ccget.get_container(container_path)
    key = ccget.get_key(container_path, key, tag)
    if type(value) is not list:
        v = [str(value).encode('utf-8')]
    else:
        v = [x.encode('utf-8') for x in value]

    for item in key.values:
        db.session.delete(item)
    db.session.commit()

    for item in v:
        v=Value(key.id, item)
        db.session.add(v)
    db.session.commit()

def update_container(container, new_name, description=None):
    """
    Rename a container

    :param container: The container to rename (required)
    :param new_name: The new name of the container (required)
    :param description: The new description of the container
                        (optional: default None)
    """
    pass