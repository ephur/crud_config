import flask
from crud_config import app
from crud_config import db
from crud_config.models import *
import sqlalchemy.orm.exc as sqlormerrors
import crud_config.exceptions as ce
import retrieve as ccget

def delete_key(container, name, value=None, tag=None):
    """ Delete a key (and it's associated values)

    :param container: container to delete key from (required)
    :param name: name of key to delete (required)
    :param tag: match key with tag
                (optional: default __class__.default_key)
    """
    k = ccget.get_key(container, name, tag=tag)
    if value is None:
        db.session.delete(k)
        db.session.commit()
        return True
    check1 = len(k.values) == 1
    check2 = k.values[0].value == value
    if check1 and check2:
        db.session.delete(k)
        db.session.commit()
        return True
    else:
        for a_val in k.values:
            if a_val.value == value:
                db.session.delete(a_val)
                db.session.commit()
                return True
    return False


def delete_container(container, confirm=False):
    """ Delete a container and all of the keys and values inside of it

    This is a descructive operation. It defaults to noop, when noop is
    true it will return a dictionary of all the items to be deleted,
    in order to actually delete noop must be False & confirm must be True.

    :param container: The container to delete (required)
    :param noop: perform a dry run (optional: default True)
    :param confirm: if True allow delete to happen
                    (optional: default False)
    """
    c = ccget.get_container(container)
    db.session.delete(c)
    db.session.commit()
    return True