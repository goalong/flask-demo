from flask import Blueprint

comment = Blueprint('comment', __name__)

from . import routes

