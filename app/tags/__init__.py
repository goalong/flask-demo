from flask import Blueprint

tag = Blueprint('tag', __name__)

from . import routes

