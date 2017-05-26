# encoding: utf-8
from flask import render_template, flash, redirect, url_for, abort,\
    request, current_app, g, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import  Message, Comment, User_Approve, Post
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


@comment.route('/post/<int:post_id>/approve_comment', methods=['POST'])
@login_required
def approve(post_id):
    target_id = request.form.get('target_id', 0, type=int)
    target_type = request.form.get('target_type', '', type=str)
    is_approved = User_Approve.query.filter_by(target_id=target_id, target_type=target_type,
                              user_id=current_user.id,
                              approved=True).count()
    if is_approved < 1:
        new_approve = User_Approve(target_id=target_id, target_type=target_type,
                              user_id=current_user.id,
                              approved=True)
        comment = Comment.query.get(target_id)
        message = Message(sender=current_user.id, receiver=comment.author_id, action='approve comment',
                          target_id=comment.id, target_type="comment")

        db.session.add(new_approve)
        db.session.add(message)
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



@comment.route('/post/<int:post_id>/approve', methods=['POST'])
@login_required
def approve_post(post_id):
    target_id = request.form.get('target_id', 0, type=int)
    target_type = request.form.get('target_type', '', type=str)
    is_approved = User_Approve.query.filter_by(target_id=target_id, target_type=target_type,
                              user_id=current_user.id,
                              approved=True).count()
    if is_approved < 1:
        new_approve = User_Approve(target_id=target_id, target_type=target_type,
                              user_id=current_user.id,
                              approved=True)
        post = Post.query.get(target_id)
        message = Message(sender=current_user.id, receiver=post.user_id, action='approve post',
                          target_id=post.id, target_type="post")

        db.session.add(new_approve)
        db.session.add(message)
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



