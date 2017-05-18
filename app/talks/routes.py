# encoding: utf-8
from flask import render_template, flash, redirect, url_for, abort,\
    request, current_app, g
from flask_login import login_required, current_user
from .. import db
from ..models import User, Post, Comment, post_tag
# from ..emails import send_author_notification, send_comment_notification
from . import talks
from .forms import ProfileForm, TalkForm, CommentForm, PresenterCommentForm


@talks.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.followed_posts().paginate(
        page, per_page=current_app.config['TALKS_PER_PAGE'],
        error_out=False)
    talk_list = pagination.items
    return render_template('talks/index.html', talks=talk_list, read_only=True,
                           pagination=pagination)

@talks.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.date.desc()).paginate(
        page, per_page=current_app.config['TALKS_PER_PAGE'],
        error_out=False)
    talk_list = pagination.items
    return render_template('talks/index.html', talks=talk_list, read_only=True,
                           pagination=pagination)


@talks.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.date.desc()).paginate(
        page, per_page=current_app.config['TALKS_PER_PAGE'],
        error_out=False)
    talk_list = pagination.items
    if user == current_user:

        return render_template('talks/user.html', user=user, talks=talk_list,
                           followed=len(list(user.followee))-1, followers=len(list(user.fans))-1,
                           pagination=pagination)
    return render_template('talks/user.html', user=user, talks=talk_list,
                           pagination=pagination)


@talks.route('/profile', methods=['GET', 'POST'])
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
        return redirect(url_for('talks.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.bio.data = current_user.bio
    return render_template('talks/profile.html', form=form)


@talks.route('/new', methods=['GET', 'POST'])
@login_required
def new_talk():
    form = TalkForm()
    if form.validate_on_submit():
        print("post_tag count: {}".format(db.session.query(post_tag).all()))
        talk = Post(author=current_user)
        form.to_model(talk)
        db.session.add(talk)
        db.session.commit()
        flash(u'发布成功')
        print("post_tag count: {}".format(db.session.query(post_tag).all()))
        return redirect(url_for('.index'))
    return render_template('talks/edit_talk.html', form=form)


@talks.route('/post/<int:id>', methods=['GET', 'POST'])
def talk(id):
    post = Post.query.get_or_404(id)
    comment = None
    if current_user.is_authenticated:
        form = PresenterCommentForm()
        if form.validate_on_submit():
            comment = Comment(body=form.body.data,
                              post=post, reply_id = int(form.data.get("reply_id")) if form.data.get("reply_id") else None,
                              author=current_user,
                              approved=True)
    else:
        form = CommentForm()
        if form.validate_on_submit():
            comment = Comment(body=form.body.data,
                              post=post,
                              author_name=form.name.data,
                              author_email=form.email.data,
                              approved=False)
    if comment:
        db.session.add(comment)
        db.session.commit()
        if comment.approved:
            # send_comment_notification(comment)
            flash('Your comment has been published.')
        else:
            # send_author_notification(talk)
            flash('Your comment will be published after it is reviewed by '
                  'the presenter.')
        return redirect(url_for('.talk', id=post.id) + '#top')
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
    return render_template('talks/talk.html', talk=post, form=form,
                           comments=comments, pagination=pagination),\
           200, headers


@talks.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_talk(id):
    talk = Post.query.get_or_404(id)
    if not current_user.is_admin and talk.author != current_user:
        abort(403)
    form = TalkForm()
    if form.validate_on_submit():
        form.to_model(talk)
        db.session.add(talk)
        db.session.commit()
        flash(u'修改成功')
        return redirect(url_for('.talk', id=talk.id))
    form.from_model(talk)
    return render_template('talks/edit_talk.html', form=form)


@talks.route('/moderate')
@login_required
def moderate():
    comments = current_user.for_moderation().order_by(Comment.timestamp.asc())
    return render_template('talks/moderate.html', comments=comments)


@talks.route('/moderate-admin')
@login_required
def moderate_admin():
    if not current_user.is_admin:
        abort(403)
    comments = Comment.for_moderation().order_by(Comment.timestamp.asc())
    return render_template('talks/moderate.html', comments=comments)


@talks.route('/unsubscribe/<token>')
def unsubscribe(token):
    talk, email = Post.unsubscribe_user(token)
    if not talk or not email:
        flash('Invalid unsubscribe token.')
        return redirect(url_for('talks.index'))
    # PendingEmail.remove(email)
    flash('You will not receive any more email notifications about this talk.')
    return redirect(url_for('talks.talk', id=talk.id))


@talks.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    if user == current_user:
        flash('You can\'t follow yourself.')
        return redirect(url_for('talks.user', username=username))
    u = current_user.follow(user)
    if u is None:
        flash('Cannot follow ' + username + '.')
        return redirect(url_for('talks.user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + username + '!')
    return redirect(url_for('talks.user', username=username))

@talks.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    if user == current_user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('talks.user', username=username))
    u = current_user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + username + '.')
        return redirect(url_for('talks.user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + username + '.')
    return redirect(url_for('talks.user', username=username))
    
