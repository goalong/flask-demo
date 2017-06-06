# encoding: utf8
from datetime import datetime
import hashlib

from flask import url_for
from markdown import markdown
import bleach
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import request, current_app
from flask_login import UserMixin
from . import db, login_manager


user_relationship = db.Table(
    'user_follow',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followee_id', db.Integer, db.ForeignKey('user.id'))
)

post_tag = db.Table('post_tag',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)


user_tag = db.Table('user_tag',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)



class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),
                      nullable=False, unique=True, index=True)
    username = db.Column(db.String(64),
                         nullable=False, unique=True, index=True)
    is_admin = db.Column(db.Boolean)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    bio = db.Column(db.String(256))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(64))
    posts = db.relationship('Post', lazy='dynamic', backref='author')
    comments = db.relationship('Comment', lazy='dynamic', backref='author')
    messages = db.relationship('Message', foreign_keys="Message.receiver", lazy='dynamic')
    followee = db.relationship('User',       #对于一个user, user.followee代表当前用户在关注的人, user.fans代表当前用户的粉丝
                               secondary=user_relationship,
                               primaryjoin=(user_relationship.c.follower_id == id),
                               secondaryjoin=(user_relationship.c.followee_id == id),
                               backref=db.backref('fans', lazy='dynamic'),
                               lazy='dynamic')
    tags = db.relationship(
        "Tag", lazy='dynamic',
        secondary=user_tag,
        back_populates="users")

    def follow(self, obj):
        if not self.is_following(obj):
            if isinstance(obj, User):
                self.followee.append(obj)
            elif isinstance(obj, Tag):
                self.tags.append(obj)
            return self

    def unfollow(self, obj):
        if self.is_following(obj):
            if isinstance(obj, User):
                self.followee.remove(obj)
            elif isinstance(obj, Tag):
                self.tags.remove(obj)
            return self

    def is_following(self, obj):
        if isinstance(obj, User):
            return self.followee.filter(
            user_relationship.c.followee_id == obj.id).count() > 0
        elif isinstance(obj, Tag):
            return db.session.query(user_tag).filter(user_tag.c.user_id == self.id, user_tag.c.tag_id==obj.id).count() > 0
    # def follow_tag(self, tag):
    #     if not self.is_following(tag):
    #         self.tags.append(tag)
    #         return self

    def followed_posts(self):     #Todo, need union follow tag's posts
        return Post.query.join(
            user_relationship, (user_relationship.c.followee_id == Post.user_id)).filter(
            user_relationship.c.follower_id == self.id).order_by(
            Post.date.desc())

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'https://www.gravatar.com/avatar'
        hash = self.avatar_hash or \
               hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def for_moderation(self, admin=False):
        if admin and self.is_admin:
            return Comment.for_moderation()
        return Comment.query.join(Post, Comment.post_id == Post.id).\
            filter(Post.author == self).filter(Comment.approved == False)

    def get_api_token(self, expiration=300):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'user': self.id}).decode('utf-8')

    @staticmethod
    def validate_api_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        id = data.get('user')
        if id:
            return User.query.get(id)
        return None




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # venue = db.Column(db.String(128))
    # venue_url = db.Column(db.String(128))
    date = db.Column(db.DateTime(), default=datetime.utcnow)
    comments = db.relationship('Comment', lazy='dynamic', backref='post', uselist=True)
    tags = db.relationship(
        "Tag", lazy='dynamic',
        secondary=post_tag,
        back_populates="posts")

    def approved_comments(self):
        return self.comments.filter_by(approved=True)

    @property
    def approve_count(self):
        return User_Approve.query.filter(User_Approve.target_type == "post",
                                         User_Approve.target_id == self.id).count()

    def get_unsubscribe_token(self, email, expiration=604800):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'talk': self.id, 'email': email}).decode('utf-8')

    def add_tag(self, tag):
        is_existed = self.tags.filter(post_tag.c.post_id == self.id, post_tag.c.tag_id == tag.id).count() > 0
        if is_existed:
            pass
        else:
            self.tags.append(tag)
            return self

    @staticmethod
    def unsubscribe_user(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None, None
        id = data.get('talk')
        email = data.get('email')
        if not id or not email:
            return None, None
        post = Post.query.get(id)
        if not post:
            return None, None
        Comment.query\
            .filter_by(post=post).filter_by(author_email=email)\
            .update({'notify': False})
        db.session.commit()
        return post, email

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    created_time = db.Column(db.DateTime(), default=datetime.utcnow)
    is_valid = db.Column(db.Boolean, default=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))   #在标签的详情页会有展示，以鼓励活跃的内容贡献者
    posts = db.relationship(
        "Post", lazy='dynamic',
        secondary=post_tag,
        back_populates="tags")
    users = db.relationship(
        "User", lazy='dynamic',
        secondary=user_tag,
        back_populates="tags")


class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    unread = db.Column(db.Boolean, default=True, nullable=False)
    sender = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender_email = db.Column(db.String(64))
    receiver = db.Column(db.Integer, db.ForeignKey('user.id'))
    target_id = db.Column(db.Integer)
    target_type = db.Column(db.String(64))

    @property
    def sender_name(self):
        if self.sender:
            return User.query.get(self.sender).username
        return None

    @property
    def target(self):
        if self.target_type == "post":
            target = Post.query.get(self.target_id)
            target.info = {"url": url_for('posts.post', id=self.target_id), "repr": target.title}
        elif self.target_type == "comment":
            target = Comment.query.get(self.target_id)
            target.info = {"url": url_for('posts.post', id=target.post_id), "repr": target.body}
        elif self.target_type == "user":
            target = User.query.get(self.target_id)
            target.info = {"url": url_for('posts.user', username=target.username), "repr": target.username}
        return target

    @property
    def target_url(self):
        pass

    @property
    def target_repr(self):
        pass






class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author_name = db.Column(db.String(64))
    author_email = db.Column(db.String(64))     #允许未注册用户评论
    notify = db.Column(db.Boolean, default=True)
    approved = db.Column(db.Boolean, default=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    reply_id = db.Column(db.Integer, db.ForeignKey('comments.id'))    #本条评论所要回复的评论的ID
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    children = db.relationship('Comment', backref=db.backref("parent", remote_side=[id]),  uselist=True,
                                     foreign_keys="Comment.parent_id")

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    @property
    def approve_count(self):
        return User_Approve.query.filter(User_Approve.target_type=="comment", User_Approve.target_id==self.id).count()

    @property
    def reply_user(self):  # 所要回复的评论的作者
        if not self.reply_id:
            return None
        author_id = Comment.query.get(self.reply_id).author_id
        if not author_id:
            return None
        return User.query.get(author_id)



    @property
    def reply_name(self):   #所要回复的评论的作者名字
        # if not self.reply_id:
        #     return None
        # author_id = Comment.query.get(self.reply_id).author_id
        # if not author_id:
        #     return None
        # return User.query.get(author_id).username
        if self.reply_user:
            return self.reply_user.username
        else:
            return None

    @staticmethod
    def for_moderation():
        return Comment.query.filter(Comment.approved == False)

    # def notification_list(self):
    #     list = {}
    #     for comment in self.talk.comments:
    #         # include all commenters that have notifications enabled except
    #         # the author of the talk and the author of this comment
    #         if comment.notify and comment.author != comment.talk.author:
    #             if comment.author:
    #                 # registered user
    #                 if self.author != comment.author:
    #                     list[comment.author.email] = comment.author.name or \
    #                                                  comment.author.username
    #             else:
    #                 # regular user
    #                 if self.author_email != comment.author_email:
    #                     list[comment.author_email] = comment.author_name
    #     return list.items()


db.event.listen(Comment.body, 'set', Comment.on_changed_body)


class User_Approve(db.Model):
    __tablename__ = 'user_approve'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved = db.Column(db.Boolean, default=False)
    target_type = db.Column(db.String(32))
    target_id = db.Column(db.Integer)



# class PendingEmail(db.Model):
#     __tablename__ = 'pending_emails'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64))
#     email = db.Column(db.String(64), index=True)
#     subject = db.Column(db.String(128))
#     body_text = db.Column(db.Text())
#     body_html = db.Column(db.Text())
#     talk_id = db.Column(db.Integer, db.ForeignKey('talks.id'))
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#
#     @staticmethod
#     def already_in_queue(email, talk):
#         return PendingEmail.query\
#             .filter(PendingEmail.talk_id == talk.id)\
#             .filter(PendingEmail.email == email).count() > 0
#
#     @staticmethod
#     def remove(email):
#         PendingEmail.query.filter_by(email=email).delete()
