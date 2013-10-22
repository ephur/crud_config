import flask
from ccapi import app

import simplejson as json


def error(code, *args, **kwargs):
    if code == 400: return(four_oh_oh(*(args), **(kwargs)))
    if code == 404: return(four_oh_four(*(args), **(kwargs)))
    if code == 500: return(five_oh_oh(*(args), **(kwargs)))

# Error Handler for 400's, REQUEST errors.
def four_oh_oh(*args, **kwargs):
    error = {"code": 400, "type": "client request error", "message": args, "details": kwargs}
    return json.dumps(error), 400

# 404's Resources Not Found
def four_oh_four(*args, **kwargs):
    error = {"code": 404, "type": "resource not found", "message": args, "details": kwargs}
    return json.dumps(error), 404

# 500 Internal Server error
def five_oh_oh(*args, **kwargs):
    app.logger.error("CAUGHT 500: %s, %s" % (str(args), str(kwargs)))
    error = {"code": 500, "type": "internal server error", "message": args, "details": kwargs}
    return json.dumps(error), 500
