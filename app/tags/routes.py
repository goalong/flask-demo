# encoding: utf-8
from flask import render_template, flash, redirect, url_for, abort,\
    request, current_app, g, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import Post, Tag, Message
from . import tag


@tag.route('/tag/<tag_name>/')
# @login_required
def tag_profile(tag_name):
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = tag.posts.order_by(Post.date.desc()).paginate(
        page, per_page=current_app.config['TALKS_PER_PAGE'],
        error_out=False)
    talk_list = pagination.items

    return render_template('tags/tag.html', posts=talk_list, tag=tag,
                           pagination=pagination)

@tag.route('/tags/')
# @login_required
def tag_list():
    page = request.args.get('page', 1, type=int)
    pagination = Tag.query.order_by(Tag.created_time.desc()).paginate(
        page, per_page=current_app.config['TALKS_PER_PAGE'],
        error_out=False)
    tag_list = pagination.items

    return render_template('tags/tag_list.html', tag_list=tag_list,
                           pagination=pagination)


@tag.route('/tag/<tag_name>/follow')
@login_required
def follow_tag(tag_name):
    tag = Tag.query.filter_by(name=tag_name).first()
    u = current_user.follow(tag)

    if u is None:
        flash('Cannot follow ' + tag_name + '.')
        return redirect(url_for('tag.tag_profile', tag_name=tag_name))
    # message = Message(sender=current_user.id, receiver=user.id, action='follow',
    #                   target_id=user.id, target_type="user")
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + tag_name + '!')
    return redirect(url_for('tag.tag_list'))

@tag.route('/tag/<tag_name>/unfollow')
@login_required
def unfollow_tag(tag_name):
    tag = Tag.query.filter_by(name=tag_name).first()
    u = current_user.unfollow(tag)
    if u is None:
        flash('Cannot unfollow ' + tag_name + '.')
        return redirect(url_for('tag.tag_profile', tag_name=tag_name))
    db.session.add(u)
    db.session.commit()
    flash('You are now unfollowing ' + tag_name + '!')
    return redirect(url_for('tag.tag_list'))




