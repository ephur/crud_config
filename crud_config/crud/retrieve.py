import flask
from crud_config import app
from crud_config import db
from crud_config.models import *
import sqlalchemy.orm.exc as sqlormerrors
import crud_config.exceptions as ce


def get_container(container):
    """
    Get the container referenced by ID or by Tree

    Tree generally maps to a URI path:  /region/datacenter/machine

    :param container: The ID or Tree of a container to get (required)
    """

    # Create the list to go through to find the requested container
    try:
        containers = [int(container)]
    except ValueError:
        containers = container.lstrip("/").rstrip("/").split("/")

    # Start at the top, and recurse to get the final container
    top_record = db.session.query(Container).filter(
        Container.parent_id == None, Container.name == unicode('root')).one()
    # The top record was the one requested, an empty string (or /)
    if len(containers) == 1 and containers[0] == '':
        return top_record

    # Iterate through containers, and get the next one down
    for item in containers:
        try:
            if type(item) is int:
                top_record = db.session.query(Container).\
                    filter(Container.id == item).one()
            else:
                top_record = db.session.query(Container).filter(
                    Container.name == unicode(item),
                    Container.parent_id == top_record.id).one()
        except sqlormerrors.MultipleResultsFound as e:
            db.session.rollback()
            raise ce.NotUnique("To many rows found matching."
                               "This is a serious DB integrity issue")
        except sqlormerrors.NoResultFound as e:
            db.session.rollback()
            raise ce.noResult("There's no match!")

    # After iterating, top_record was the final container requested
    return top_record

def get_key(container, name, tag=None):
    """
    Get key inside of a container

    This will return an ORM mapped key object with reference to the parent
    and values. The values returned will be encrypted since they are not
    transformed from the database. If accessing values through this
    relationship the client must handle decrypting the values.

    :param container: The path or ID of the container holding
                      the key (rquired)
    :param name: The name of the key to retreive (required)
    :param tag: Tag of key to return
                (optional: default __class__.default_tag)
    """

    if tag is None:
        tag = app.config['DEFAULT_TAG']
    try:
        c = get_container(container)
        k = db.session.query(Key).filter(Key.tag == unicode(tag),
                                           Key.container_id == c.id,
                                           Key.name == unicode(name)).one()
    except sqlormerrors.NoResultFound:
        db.session.rollback()
        raise ce.noResult("There's no match!")
    return k

def get_value(key_id):
    """
    Get value(s) for a key

    :param key_id: Key ID to get value(s) for (required)
    """

    # Get all the values from the DB and iterate through decrypting them
    vs = db.session.query(Value).filter(Value.key_id == key_id).all()
    if len(vs) == 0:
        raise ce.noResult

    return vs