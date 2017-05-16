# encoding: utf-8
from flask import render_template, flash, redirect, url_for, abort,\
    request, current_app, g, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import  Post, Comment, User_Approve
from . import comment


@comment.route('/post/<int:post_id>/reply_comment', methods=['POST'])
@login_required
def reply_comment(post_id):
    reply_id = request.form.get('reply_id', 0, type=int)
    content = request.form.get('content', '', type=str)
    parent_id = request.form.get('parent_id', '', type=int)
    parent_comment = Comment.query.get_or_404(parent_id)
    new_comment = Comment(body=content,
                              post_id=post_id, reply_id=reply_id,
                              author=current_user,
                              parent = parent_comment,
                              approved=True)
    # parent_comment.child_comments.append(new_comment)
    db.session.add(new_comment)
    # db.session.add(parent_comment)
    # db.session.add(parent_comment)
    db.session.commit()
    return jsonify(rs="olla")


@comment.route('/post/<int:post_id>/approve', methods=['POST'])
@login_required
def approve_comment(post_id):
    target_id = request.form.get('target_id', 0, type=int)
    target_type = request.form.get('target_type', '', type=str)
    is_approved = User_Approve.query.filter_by(target_id=target_id, target_type=target_type,
                              user_id=current_user.id,
                              approved=True).count()
    if is_approved < 1:
        new_approve = User_Approve(target_id=target_id, target_type=target_type,
                              user_id=current_user.id,
                              approved=True)
        db.session.add(new_approve)
        db.session.commit()
        rs = 1
    elif is_approved == 1:
        rs = 0
    else:
        db.session.query(User_Approve).filter_by(target_id=target_id, target_type=target_type,
                              user_id=current_user.id,
                              approved=True).delete()
        db.session.commit()
        rs = 0
    return jsonify(rs=rs)

@comment.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.date.desc()).paginate(
        page, per_page=current_app.config['TALKS_PER_PAGE'],
        error_out=False)
    talk_list = pagination.items
    return render_template('talks/index.html', talks=talk_list,
                           pagination=pagination)

