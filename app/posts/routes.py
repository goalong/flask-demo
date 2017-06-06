# encoding: utf-8
from flask import render_template, flash, redirect, url_for, abort,\
    request, current_app, g
from flask_login import login_required, current_user
from .. import db
from ..models import User, Post, Comment, post_tag, Message
# from ..emails import send_author_notification, send_comment_notification
from . import posts
from .forms import ProfileForm, PostForm, CommentForm, PresenterCommentForm


@posts.route('/')
# @login_required
def index():
    page = request.args.get('page', 1, type=int)
    if current_user.is_authenticated:
        pagination = current_user.followed_posts().paginate(
            page, per_page=current_app.config['TALKS_PER_PAGE'],
            error_out=False)
    else:
        pagination = Post.query.order_by(Post.date.desc()).paginate(
        page, per_page=current_app.config['TALKS_PER_PAGE'],
        error_out=False)
    post_list = pagination.items
    return render_template('posts/index.html', posts=post_list, read_only=True,
                           pagination=pagination)

@posts.route('/explore')
# @login_required
def explore():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.date.desc()).paginate(
        page, per_page=current_app.config['TALKS_PER_PAGE'],
        error_out=False)
    post_list = pagination.items
    return render_template('posts/index.html', posts=post_list, read_only=True,
                           pagination=pagination)


@posts.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.date.desc()).paginate(
        page, per_page=current_app.config['TALKS_PER_PAGE'],
        error_out=False)
    post_list = pagination.items
    if user == current_user:

        return render_template('posts/user.html', user=user, posts=post_list,
                           followed=len(list(user.followee))-1, followers=len(list(user.fans))-1,
                           pagination=pagination)
    return render_template('posts/user.html', user=user, posts=post_list,
                           pagination=pagination)


@posts.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.bio = form.bio.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash(u'您的信息已更新')
        return redirect(url_for('posts.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.bio.data = current_user.bio
    return render_template('posts/profile.html', form=form)


@posts.route('/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        print("post_tag count: {}".format(db.session.query(post_tag).all()))
        post = Post(author=current_user)
        form.to_model(post)
        db.session.add(post)
        db.session.commit()
        flash(u'发布成功')
        print("post_tag count: {}".format(db.session.query(post_tag).all()))
        return redirect(url_for('.index'))
    return render_template('posts/edit_post.html', form=form)


@posts.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get(id)
    comment = None
    if current_user.is_authenticated:
        form = PresenterCommentForm()
        if form.validate_on_submit():   # form post请求valid
            comment = Comment(body=form.body.data,
                              post=post, reply_id = int(form.data.get("reply_id")) if form.data.get("reply_id") else None,
                              author=current_user,
                              approved=True)
            # if comment.reply_id:
            #     message = Message(sender=current_user.id, receiver=comment.reply_user.id, action='reply comment',
            #                       target_id=comment.reply_id, target_type="comment")  # 给原评论作者的消息
            #     if comment.reply_user.id != post.user_id:
            #         msg = Message(sender=current_user.id, receiver=post.user_id, action='add comment',
            #                       target_id=post.id, target_type="post")  # 给原主题作者的消息
            #         db.session.add(msg)
            # else:
            #     message = Message(sender=current_user.id, receiver=post.user_id, action='add comment',
            #                       target_id=post.id, target_type="post")
            # db.session.add(comment)
            # db.session.add(message)
            # db.session.commit()
            # if comment.approved:
            #     # send_comment_notification(comment)
            #     flash('Your comment has been published.')
            # else:
            #     # send_author_notification(post)
            #     flash('Your comment will be published after it is reviewed by '
            #           'the presenter.')
            # return redirect(url_for('.post', id=post.id) + '#top')
    else:    # 未登录用户的发表评论
        form = CommentForm()
        if form.validate_on_submit():
            comment = Comment(body=form.body.data,
                              post=post,
                              author_name=form.name.data,
                              author_email=form.email.data,
                              approved=True)    # 之前站外用户的评论需要审查通过才会显示
    if comment:    #post请求则comment有数据，get请求则comment为None
        # if current_user.is_authenticated:
        sender = current_user.id if current_user.is_authenticated else None
        sender_email = None
        if not sender:
            sender_email = comment.author_email
        if comment.reply_id:
            message = Message(sender=sender, receiver=comment.reply_user.id, action='reply comment',
                              target_id=comment.reply_id, target_type="comment", sender_email=sender_email)   #给原评论作者的消息
            if comment.reply_user.id != post.user_id:
                msg = Message(sender=sender, receiver=post.user_id, action='add comment',
                                  target_id=post.id, target_type="post", sender_email=sender_email)           #给原主题作者的消息
                db.session.add(msg)
        else:
            message = Message(sender=sender, receiver=post.user_id, action='add comment',
                          target_id=post.id, target_type="post", sender_email=sender_email)

        # else:
        #     message = Message(sender=current_user.id, receiver=post.user_id, action='add comment',
        #                       target_id=post.id, target_type="post")

        db.session.add(message)
        db.session.add(comment)
        db.session.commit()
        if comment.approved:
            # send_comment_notification(comment)
            flash('Your comment has been published.')
        else:
            # send_author_notification(post)
            flash('Your comment will be published after it is reviewed by '
                  'the presenter.')
        return redirect(url_for('.post', id=post.id) + '#top')
    if post.author == current_user or \
            (current_user.is_authenticated and current_user.is_admin):
        comments_query = post.comments
    else:
        comments_query = post.approved_comments()  #Todo, fix
    page = request.args.get('page', 1, type=int)
    pagination = comments_query.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    headers = {}
    if current_user.is_authenticated:
        headers['X-XSS-Protection'] = '0'
    return render_template('posts/post.html', post=post, form=form, read_only=True, show_full_content=True,
                           comments=comments, pagination=pagination),\
           200, headers


@posts.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if not current_user.is_admin and post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        form.to_model(post)
        db.session.add(post)
        db.session.commit()
        flash(u'修改成功')
        return redirect(url_for('.post', id=post.id))
    form.from_model(post)
    return render_template('posts/edit_post.html', form=form)


@posts.route('/moderate')
@login_required
def moderate():
    comments = current_user.for_moderation().order_by(Comment.timestamp.asc())
    return render_template('posts/moderate.html', comments=comments)


@posts.route('/moderate-admin')
@login_required
def moderate_admin():
    if not current_user.is_admin:
        abort(403)
    comments = Comment.for_moderation().order_by(Comment.timestamp.asc())
    return render_template('posts/moderate.html', comments=comments)


@posts.route('/unsubscribe/<token>')
def unsubscribe(token):
    post, email = Post.unsubscribe_user(token)
    if not post or not email:
        flash('Invalid unsubscribe token.')
        return redirect(url_for('posts.index'))
    # PendingEmail.remove(email)
    flash('You will not receive any more email notifications about this post.')
    return redirect(url_for('posts.post', id=post.id))


@posts.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    if user == current_user:
        flash('You can\'t follow yourself.')
        return redirect(url_for('posts.user', username=username))
    u = current_user.follow(user)
    if u is None:
        flash('Cannot follow ' + username + '.')
        return redirect(url_for('posts.user', username=username))
    message = Message(sender=current_user.id, receiver=user.id, action='follow',
                      target_id=user.id, target_type="user")
    db.session.add(u)
    db.session.add(message)
    db.session.commit()
    flash('You are now following ' + username + '!')
    return redirect(url_for('posts.user', username=username))

@posts.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    if user == current_user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('posts.user', username=username))
    u = current_user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + username + '.')
        return redirect(url_for('posts.user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + username + '.')
    return redirect(url_for('posts.user', username=username))
    
