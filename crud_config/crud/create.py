import flask
from crud_config import app
from crud_config import db
from crud_config.models import *
import retrieve as ccget
import crud_config.exceptions as ce

import sqlalchemy.orm.exc as sqlormerrors
import sqlalchemy.exc as sqlerrors

def add_container(parent_id, name, description=None):
    """
    Add a new container

    :param parent_id: The ID of the parent container (required)
    :param name: The name of the new container (required)
    :param description: The description of the new container
                        (optional: default None)

    """
    if parent_id < 1:
        raise ce.DBError("Parent ID must be greater than ZERO")
    c = Container(name, description, int(parent_id))
    try:
        db.session.add(c)
        db.session.commit()
    except sqlerrors.IntegrityError as e:
        db.session.rollback()
        raise ce.notUnique()
    return c

def add_keyval(container, key, value, tag=None):
    """
    Add a key:value pair to the database

    This method just simplifies the operations of adding a key and then
    attaching a value to that key.

    :param container: ID or full path to container
                      holding new keyvalue (required)
    :param key: The key to associate value with, can be an existing
                or new key. (required)
    :param value: The value to store. If a value already exists for key
                  the new value is appended to the list. (required)
    :param tag: tag to associated with key (only if key is NEW),
                (optional: default '__class__.default_tag')
    """
    # Set the default tag
    if tag is None:
        tag = app.config['DEFAULT_TAG']

    # Try and add the Key
    try:
        k = add_key(container, key, tag=tag)
    except ce.notUnique as e:
        # The key already exists, rollback the session and get existing key
        db.session.rollback()
        k = ccget.get_key(container, key, tag)
    # Add the value
    v = add_value(k.id, value)
    return (k, v)

def add_value(key_id, raw_value):
    """
    Add a value

    :param key_id: ID of Key to associate value with (required)
    :param raw_value: The value to add to the key (required)
    """

    raw_value = raw_value.encode('utf-8')
    try:
        # Get a list of all the values, iterate through the list to check
        # for duplicates, this is an expensive operation but the only way
        # to check for dupes when values are stored encrypted
        vs = ccget.get_value(key_id)
        for v in vs:
            if v.value == raw_value:
                return v
    except ce.noResult:
        pass

    v = Value(key_id, unicode(raw_value))
    db.session.add(v)
    db.session.commit()
    # Transform the ORM Object to a dict
    value = {"id": v.id, "key_id": v.key_id, "value": raw_value}

    return v


def add_key(container, name, tag=None):
    """
    Add a key to the specified container

    :param container: The path or ID of the container to
                      create key in (required)
    :param name: The name of the key to create (required)
    :param tag: Tag to associate with newly created key
                (optional: default __class__.default_tag)
    """

    if tag is None:
        tag = app.config['DEFAULT_TAG']

    try:
        container_id = int(container)
    except ValueError as e:
        container_id = ccget.get_container(container).id

    k = Key(name, container_id, tag)
    try:
        db.session.add(k)
        db.session.commit()
    except sqlerrors.IntegrityError as e:
        raise ce.notUnique()
    return k