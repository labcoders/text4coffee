#!/bin/python
from redis import Redis

from flask import Flask

app = Flask(__name__)
app.config.from_object("secret_config")

redis = Redis()

from . import (
        routes
)
