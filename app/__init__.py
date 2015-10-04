#!/bin/python
from redis import Redis

from flask import Flask

app = Flask(__name__)

redis = Redis()

from . import (
        routes
)
