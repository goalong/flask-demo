# encoding: utf-8
from flask import render_template, flash, redirect, url_for, abort,\
    request, current_app, g, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import  Message
from . import message


@message.route('/message')
@login_required
def message_list():

    messages = current_user.messages.order_by(
            Message.timestamp.desc()).all()
    return render_template('messages/message.html', messages=messages)  #Todo, 分页



