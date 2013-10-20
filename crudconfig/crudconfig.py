import exceptions as ce

try:
    from keyczar import keyczar
    from keyczar import errors as kcerrors
except ImportError as e:
    raise ce.CryptoError("cloud not import Key Czar, can't use CrudConfig")

try: 
    import sqlalchemy
    from sqlalchemy.ext.declarative import declarative_base
    import sqlalchemy.exc as sqlerrors
    import sqlalchemy.orm.exc as sqlormerrors
    from sqlalchemy.orm import sessionmaker, scoped_session
    import MySQLdb
except ImportError as e:
    raise ce.DBError("could not import SQL Alchemy or MySQLdb, can't use CrudConfig")

# Declare the Base object which all other items in the ORM will inherit from
Base = declarative_base()
# Import the tables/objects used in the ORM
from models import *

class CrudConfig(object):
    def __init__(self, **kwargs):
        try: 
            self.default_tag = unicode(kwargs['default_tag'].upper())
        except KeyError as e:
            self.default_tag = unicode('GLOBAL')

        # Initialize The Crypto Object
        try:
            keypath = kwargs['keypath']
            self.crypter = keyczar.Crypter.Read(keypath)
        except KeyError as e:
            raise ce.CryptoError("Cannot init %s, need to pass keypath argument" % (self.__class__))
        except kcerrors.KeyczarError as e:
            raise ce.CryptoError("Keycar error: %s " % (e.message))

        # Initialize the DB Object
        self.db = self.__db_init(**(kwargs))
        self._Session = scoped_session(sessionmaker(bind=self.db))
        self.session = self._Session()
        # Make sure the tables & seed data are proper
        self.__check_first_run()

    def new_session(self):
        self.session = None
        self.session = self._Session()

    def copy_tag(self, container_id, tag=None):
        pass 

    def copy_container(self, source_container, target_container):
        pass

    def add_keyval(self, container, key, value, tag=None):
        try:
            # Try to add the key
            k = self.add_key(container, key)
        except ce.NotUnique as e:
            # Need a new session because the last one is dirty now
            self.session.rollback()
            # The key already exists, so instead get it
            k = self.get_key(container, key, tag)


        v = self.add_value(k.id, value)
        return (k, v)

    def add_value(self, key_id, value):
        # Need to try and get the value first, to avoid dupes
        # can't index this in the DB since we allow text. Adding is a somewhat
        # slow operation because of this duplicate check
        try:
            v = self.get_value(key_id, value)
        except ce.NoResult as e:
            self.session.rollback()
            v = Value(key_id, value)
            self.session.add(v)
            self.session.commit()
        return v

    def get_value(self, key_id, value=None):
        if value is None:
            v = self.session.query(Value).filter(Value.key_id == key_id).all()
            print len(v)
            if len(v) == 0:
                raise ce.NoResult
        else:
            v = self.session.query(Value).filter(Value.key_id == key_id, Value.value == unicode(value)).all()
            if len(v) == 0:
                raise ce.NoResult

        return v

    def get_key(self, tree, name, tag=None):
        if tag is None:
            tag = self.default_tag
        c = self.get_container(tree)
        k = self.session.query(Key).filter(Key.tag == unicode(tag), Key.container_id == c.id, Key.name == unicode(name)).one()
        return k

    def add_key(self, container, name, tag=None):
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


    def delete_key(self, container_id, name, value, tag=None):
        pass

    def update_key(self, container_id, name, value, tag=None):
        pass

    def delete_container(self, parent_id, name):
        pass 

    def update_container(self, parent_id, name): 
        pass

    def get_config(self, tree, tag=None):
        pass

    def add_container(self, parent_id, name, description=None):
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

    def list_containers(self, tree):
        pass

    def get_container(self, tree): 
        containers = tree.lstrip("/").rstrip("/").split("/")
        top_record = self.session.query(Container).filter(Container.parent_id == 0).one()
        if len(containers) == 1 and containers[0] == '':
            return top_record
        for item in containers:
            try:
                top_record = self.session.query(Container).filter(Container.name == unicode(item), Container.parent_id == top_record.id).one()
            except sqlormerrors.MultipleResultsFound as e:
                self.session.rollback()
                raise ce.NotUnique("To many rows found matching! This is a serious DB integrity issue")
            except sqlormerrors.NoResultFound as e:
                self.session.rollback()
                raise ce.NoResult("There's no match!")
        return top_record

    def __check_first_run(self):
        Base.metadata.create_all(self.db, checkfirst=True)
        q = self.session.query(Container).filter(Container.parent_id == 0).all()
        if len(q) == 0:
            # This is the first run, add the 'global' container
            c = Container(unicode('root'),unicode('The Global Container, everything belongs to this'),0)
            self.session.add(c)
            self.session.commit()
        return

    def __db_init(self,**kwargs):
        # Initialize the DB Engine Object
        try:
            dbinfo = dict()
            for item in ['db_host', 'db_name', 'db_username', 'db_password']: 
                dbinfo[item] = kwargs[item]
        except KeyError as e:
            raise ce.DBError('Cannot init DB, must provide keyword argument: %s' % (item))

        try:
            dbinfo['db_port'] = int(kwargs['db_port'])
        except KeyError:
            dbinfo['db_port'] = 3306
        except (TypeError, ValueError) as e:
            raise ce.DBError('Cannot init DB, keyword db_port must be an integer not %s' % str(type(kwargs['db_port'])))

        # Build a connection string 
        base_conn_string = 'mysql+mysqldb://%s:%s@%s:%s/%s?' % (dbinfo['db_username'], dbinfo['db_password'], dbinfo['db_host'], str(dbinfo['db_port']), dbinfo['db_name'])

        dbopts=dict()
        dbopts['charset'] = 'utf8'
        dbopts['use_unicode'] = '1'

        try:
            for key, val in kwargs['sqlalchemy_params'].iteritems():
                dbopts[key] = val 
        except KeyError:
            pass

        dbinfo['connstring'] = base_conn_string + "&".join(["%s=%s" % (k, v) for k, v in dbopts.iteritems()])

        try: 
            engine = sqlalchemy.create_engine(dbinfo['connstring'])
        except Exception as e:
            raise

        return engine