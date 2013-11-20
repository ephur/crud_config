import flask
from crud_config import app
import simplejson as json


def error(code, *args, **kwargs):
    if code == 400:
        return(four_oh_oh(*(args), **(kwargs)))
    if code == 403:
        return(four_oh_three(*(args), **(kwargs)))
    if code == 404:
        return(four_oh_four(*(args), **(kwargs)))
    if code == 500:
        return(five_oh_oh(*(args), **(kwargs)))
    return(error_on_error())


# Error Handler for 400's, REQUEST errors.
def four_oh_oh(*args, **kwargs):
    app.logger.debug("CAUGHT 400: %s, %s" % (str(args), str(kwargs)))
    error = {"code": 400,
             "type": "client request error",
             "message": args,
             "details": kwargs}
    return json.dumps(error), 400


# 403's Unauthorized
def four_oh_three(*args, **kwargs):
    app.logger.debug("CAUGHT 403: %s, %s" % (str(args), str(kwargs)))
    error = {"code": 403,
             "type": "unauthorized",
             "message": args,
             "details": kwargs}
    return json.dumps(error), 403


# 404's Resources Not Found
def four_oh_four(*args, **kwargs):
    app.logger.debug("CAUGHT 404: %s, %s" % (str(args), str(kwargs)))
    error = {"code": 404,
             "type": "resource not found",
             "message": args,
             "details": kwargs}
    return json.dumps(error), 404


# 500 Internal Server error
def five_oh_oh(*args, **kwargs):
    app.logger.error("CAUGHT 500: %s, %s" % (str(args), str(kwargs)))
    error = {"code": 500,
             "type": "internal server error",
             "message": args,
             "details": kwargs}
    return json.dumps(error), 500


# If a generic 500 is called, return a 500 with as little processing as
# possible since it shouldn'tever come to this
# @app.errorhandler(500)
# def error_on_error():
#     raise
#     return "{\"code\": 500, \"message\": [ \"INTERNAL SERVER ERROR\" ]}", 500


# When the framework throws a 404 this will handle it, different than the
# custom 404 handler because it doesn't take arguments, and relies on access
# to the flask request object
@app.errorhandler(404)
def not_found(e):
    error = {"code": 404,
             "type": "resource not found",
             "message": "unknown location '%s'" % (flask.request.full_path)}
    return json.dumps(error), 404
