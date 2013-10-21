class CrudException(Exception):
    def __call__(self, *args):
        return self.__class__(*(self.args + args))

class CryptoError(CrudException): pass

class DBError(CrudException): pass

class NotUnique(DBError): pass

class NoResult(DBError): pass
