# Import the crud config exceptions
import exceptions as ce

try:
    # Import SQL Alchemy Related Items
    import sqlalchemy
    import sqlalchemy.exc as sqlerrors
    import sqlalchemy.orm.exc as sqlormerrors
    import MySQLdb
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, scoped_session

    # Import KeyCzar/Encryption Related Items
    from keyczar import keyczar
    from keyczar import errors as kcerrors
    import base64

except ImportError as e:
    raise ce.RequirementsError("%s\nModule Required for CrudConfig" % (
                               e.message))

# Declare the Base for ORM models, and import all the models
Base = declarative_base()
from models import *


# The main class, here's where all the work happens
class CrudConfig(object):
    def __init__(self, **kwargs):
        """ Initialize a CrudConfig Object

        The CrudConfig object provides the interface to the CrudConfig
        database. It handles encryption of values, managing the relationships
        between containers, and managing tags/key:value pairs.

        :param keypath: path to KeyCzar keys (required)
        :param db_host: hostname of database server (required)
        :param db_username: username for DB server (required)
        :param db_password: password for DB server (required)
        :param db_name: database from DB server to use (required)
        :param default_tag: default tag for keys (optional: default 'GLOBAL')
        :param db_port: database port to use (optional: default 3306)
        :sqlalchemy_params: a list of SQL Alchemy paramaters (optional)
        """

        # Set the default TAG
        try:
            self.default_tag = unicode(kwargs['default_tag'].upper())
        except KeyError as e:
            self.default_tag = unicode('GLOBAL')

        # Ensure KeyPath is set
        try:
            self.keypath = kwargs['keypath']
        except KeyError as e:
            raise ce.CryptoError("Cannot init %s, keypath required"
                                 % (self.__class__))
        except kcerrors.KeyczarError as e:
            raise ce.CryptoError("Keycar error: %s " % (e.message))

        # Initialize the DB Object & Ensure Tables/Global Root is Present
        self.db = self.__db_init(**(kwargs))
        self._Session = scoped_session(sessionmaker(bind=self.db))
        self.session = self._Session()
        self.crypter = None
        self.__check_first_run()

    def add_keyval(self, container, key, value, tag=None):
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
            tag = self.default_tag

        # Try and add the Key
        try:
            k = self.add_key(container, key, tag=tag)
        except ce.NotUnique as e:
            # The key already exists, rollback the session and get existing key
            self.session.rollback()
            k = self.get_key(container, key, tag)
        # Add the value
        v = self.add_value(k.id, value)

        return (k, v)

    def add_value(self, key_id, raw_value):
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
            vs = self.get_value(key_id)
            for v in vs:
                if v['value'] == raw_value:
                    return v
        except ce.NoResult:
            pass

        # The value doesn't already exist so add it
        if self.crypter is None:
            self.crypter = keyczar.Crypter.Read(self.keypath)

        value = self.crypter.Encrypt(raw_value)
        v = Value(key_id, value)
        self.session.add(v)
        self.session.commit()
        # Transform the ORM Object to a dict
        value = {"id": v.id, "key_id": v.key_id, "value": raw_value}

        return value

    def get_value(self, key_id):
        """
        Get value(s) for a key

        :param key_id: Key ID to get value(s) for (required)
        """

        # Intialize a list to store all the decrypted values
        values = list()

        # Get all the values from the DB and iterate through decrypting them
        vs = self.session.query(Value).filter(Value.key_id == key_id).all()
        if len(vs) == 0:
            raise ce.NoResult

        # Decrypt all the values
        if self.crypter is None:
            self.crypter = keyczar.Crypter.Read(self.keypath)
        # Copy all the values to new objects so there's not a bunch of changes
        # to the values in the ORM Object
        for v in vs:
            value = {"key_id": v.key_id, "id": v.id}
            value['value'] = self.crypter.Decrypt(v.value)
            values.append(value)

        return values

    def get_key(self, container, name, tag=None):
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
            tag = self.default_tag
        try:
            c = self.get_container(container)
            k = self.session.query(Key).filter(Key.tag == unicode(tag),
                                               Key.container_id == c.id,
                                               Key.name == unicode(name)).one()
        except sqlormerrors.NoResultFound as e:
            self.session.rollback()
            raise ce.NoResult("There's no match!")
        return k

    def add_key(self, container, name, tag=None):
        """
        Add a key to the specified container

        :param container: The path or ID of the container to
                          create key in (required)
        :param name: The name of the key to create (required)
        :param tag: Tag to associate with newly created key
                    (optional: default __class__.default_tag)
        """

        if tag is None:
            tag = self.default_tag

        try:
            container_id = int(container)
        except ValueError as e:
            container_id = self.get_container(container).id

        k = Key(name, container_id, tag)
        try:
            self.session.add(k)
            self.session.commit()
        except sqlerrors.IntegrityError as e:
            raise ce.NotUnique()
        return k

    def delete_key(self, container, name, tag=None):
        """ Delete a key (and it's associated values)

        :param container: container to delete key from (required)
        :param name: name of key to delete (required)
        :param tag: match key with tag
                    (optional: default __class__.default_key)
        """
        pass

    def update_key(self, container, name, new_name, tag=None):
        """ Change the name of a key

        :param container: container to change key in (required)
        :param name: name of key to change (required)
        :param new_name: what to rename key to (required)
        :param tag: match key with this tag
                    (optional: default __class__.default_key)
        """

        pass

    def delete_container(self, container, noop=True, confirm=False):
        """ Delete a container and all of the keys and values inside of it

        This is a descructive operation. It defaults to noop, when noop is
        true it will return a dictionary of all the items to be deleted,
        in order to actually delete noop must be False & confirm must be True.

        :param container: The container to delete (required)
        :param noop: perform a dry run (optional: default True)
        :param confirm: if True allow delete to happen
                        (optional: default False)
        """
        pass

    def update_container(self, container, new_name, description=None):
        """
        Rename a container

        :param container: The container to rename (required)
        :param new_name: The new name of the container (required)
        :param description: The new description of the container
                            (optional: default None)
        """
        pass

    def add_container(self, parent_id, name, description=None):
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
            self.session.add(c)
            self.session.commit()
        except sqlerrors.IntegrityError as e:
            self.session.rollback()
            raise ce.NotUnique()
        return c

    def list_containers(self, container):
        """
        List the containers inside of a container

        :param container: The ID or Tree of the container to list
        """
        pass

    def get_container(self, container):
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
        top_record = self.session.query(Container).filter(
            Container.parent_id == 0).one()
        # The top record was the one requested, an empty string (or /)
        if len(containers) == 1 and containers[0] == '':
            return top_record

        # Iterate through containers, and get the next one down
        for item in containers:
            try:
                if type(item) is int:
                    top_record = self.session.query(Container).\
                        filter(Container.id == item).one()
                else:
                    top_record = self.session.query(Container).filter(
                        Container.name == unicode(item),
                        Container.parent_id == top_record.id).one()
            except sqlormerrors.MultipleResultsFound as e:
                self.session.rollback()
                raise ce.NotUnique("To many rows found matching."
                                   "This is a serious DB integrity issue")
            except sqlormerrors.NoResultFound as e:
                self.session.rollback()
                raise ce.NoResult("There's no match!")

        # After iterating, top_record was the final container requested
        return top_record

    def add_api_key(self, raw_apikey=None, owner=None, valid=True):
        """
        Add an API Key

        API Keys can be used to authenticate the validity of a requestor to
        data. API Keys are also stored encrypted to preserve the integrity of
        the secured data

        :param raw_apikey: API key to use. If this optional param is omitted
                           a UUID4 type api_key will be automatically returned.
        :param owner: The name of the owner (optional: default None)
        :param valid: Is the API key valid (optional: default True)
        """

        # If an api key is not provided, generate one
        if raw_apikey is None:
            import uuid
            raw_apikey = str(uuid.uuid4())
        if self.crypter is None:
            self.crypter = keyczar.Crypter.Read(self.keypath)
        apikey = unicode(base64.b64encode(
                         self.crypter.primary_key.Sign(raw_apikey)))

        try:
            key = self.session.query(ApiKey).filter(
                ApiKey.api_key == apikey).one()
        except sqlormerrors.MultipleResultsFound as e:
            self.session.rollback()
            raise ce.NotUnique("This API key already exists")
        except sqlormerrors.NoResultFound as e:
            self.session.rollback()
            key = ApiKey(apikey, owner, valid)
            self.session.add(key)
            self.session.commit()
        return (raw_apikey, key)

    def check_api_key(self, raw_apikey):
        """
        Check the validity of an API Key

        :param raw_apikey: the API key to validate (required)
        """

        if self.crypter is None:
            self.crypter = keyczar.Crypter.Read(self.keypath)
        apikey = unicode(base64.b64encode(
                         self.crypter.primary_key.Sign(raw_apikey)))

        try:
            key = self.session.query(ApiKey).filter(
                ApiKey.api_key == apikey).one()
            return True
        except sqlormerrors.MultipleResultsFound as e:
            self.session.rollback()
            return False
        except sqlormerrors.NoResultFound as e:
            self.session.rollback()
            return False

    def __check_first_run(self):
        """
        Make sure the tables are created, and global container exists
        """
        Base.metadata.create_all(self.db, checkfirst=True)
        q = self.session.query(Container).filter(
            Container.parent_id == 0).all()
        if len(q) == 0:
            # This is the first run, add the 'global' container
            c = Container(unicode('root'),
                          unicode('The Global Container,'
                                  'everything belongs to this'),
                          0)
            self.session.add(c)
            self.session.commit()
        return

    def __db_init(self, **kwargs):
        """
        Initialize the database object, checking params & creating engine

        :param db_host: hostname of database server (required)
        :param db_username: username for DB server (required)
        :param db_password: password for DB server (required)
        :param db_name: database from DB server to use (required)
        :param db_port: database port to use (optional: default 3306)
        :sqlalchemy_params: a list of SQL Alchemy paramaters (optional)
        """

        # Initialize the DB Engine Object
        try:
            dbinfo = dict()
            for item in ['db_host', 'db_name', 'db_username', 'db_password']:
                dbinfo[item] = kwargs[item]
        except KeyError as e:
            raise ce.DBError('Cannot init DB'
                             ', must provide keyword argument: %s' % (item))

        try:
            dbinfo['db_port'] = int(kwargs['db_port'])
        except KeyError:
            dbinfo['db_port'] = 3306
        except (TypeError, ValueError) as e:
            raise ce.DBError('Cannot init DB, keyword db_port must be an'
                             ' integer not %s' % str(type(kwargs['db_port'])))

        # Build a connection string
        base_conn_string = 'mysql+mysqldb://%s:%s@%s:%s/%s?' % (
            dbinfo['db_username'],
            dbinfo['db_password'],
            dbinfo['db_host'],
            str(dbinfo['db_port']),
            dbinfo['db_name'])

        dbopts = dict()
        dbopts['charset'] = 'utf8'
        dbopts['use_unicode'] = '1'

        try:
            for key, val in kwargs['sqlalchemy_params'].iteritems():
                dbopts[key] = val
        except KeyError:
            pass

        dbinfo['connstring'] = base_conn_string + "&".join(
            ["%s=%s" % (k, v) for k, v in dbopts.iteritems()])

        try:
            engine = sqlalchemy.create_engine(dbinfo['connstring'])
        except Exception as e:
            raise

        return engine
