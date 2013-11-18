#!/usr/bin/env bpython -i
import sys
from crud_config import app
from crud_config import db
from crud_config.models import *
import crud_config.crud.retrieve as ccget
import crud_config.crud.update as ccput
import crud_config.crud.delete as ccdelete
import crud_config.crud.create as ccpost
