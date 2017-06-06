# encoding: utf-8
from flask import render_template, current_app, request, redirect, url_for, \
    flash
from flask_login import login_user, logout_user, login_required

from app import db
from ..models import User
from . import auth
from .forms import LoginForm, RegisterForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if not current_app.config['DEBUG'] and not current_app.config['TESTING'] \
            and not request.is_secure:
        return redirect(url_for('.login', _external=True, _scheme='https'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash(u'邮箱或密码错误')
            return redirect(url_for('.login'))
        login_user(user, form.remember_me.data)
        return redirect(request.args.get('next') or url_for('posts.index'))
    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if not current_app.config['DEBUG'] and not current_app.config['TESTING'] \
            and not request.is_secure:
        return redirect(url_for('.login', _external=True, _scheme='https'))
    form = RegisterForm()
    if form.validate_on_submit() and form.password.data==form.password_confirm.data:
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        db.session.add(user.follow(user))
        db.session.commit()
        return redirect(request.args.get('next') or url_for('posts.index'))
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'您已退出登录')
    return redirect(url_for('posts.index'))
