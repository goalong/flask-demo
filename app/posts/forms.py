# encoding: utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, HiddenField
from wtforms.fields.html5 import DateField
from wtforms.validators import Optional, Length, URL, Email, DataRequired
from flask_pagedown.fields import PageDownField

from app.models import Tag


class ProfileForm(FlaskForm):
    name = StringField(u'昵称', validators=[Optional(), Length(1, 64)])
    location = StringField(u'位置', validators=[Optional(), Length(1, 64)])
    bio = TextAreaField(u'简介')
    submit = SubmitField(u'提交')


class PostForm(FlaskForm):
    title = StringField(u'标题', validators=[DataRequired(), Length(1, 128)])
    description = TextAreaField(u'内容')
    # slides = StringField('Slides Embed Code (450 pixels wide)')
    # video = StringField('Video Embed Code (450 pixels wide)')
    tags = StringField(u'标签',
                        validators=[Length(1, 128)], description=u"多个标签请用空格分开")
    # venue_url = StringField(u'地点链接',
    #                         validators=[Optional(), Length(1, 128), URL()])
    # date = DateField(u'日期')
    submit_button = SubmitField(u'提交', id='submit_post')


    def from_model(self, post):
        self.title.data = post.title
        self.description.data = post.description


    def to_model(self, post):
        post.title = self.title.data
        post.description = self.description.data
        tag_list = self.tags.data.split(" ")
        for t in tag_list:
            tag = Tag.query.filter_by(name=t).first()    #first方法在没有结果时返回None, 这一点需要注意
            if not tag:
                tag = Tag(name=t)
            post.add_tag(tag)
        # post.tags

        # post.venue_url = self.venue_url.data
        # post.date =


class PresenterCommentForm(FlaskForm):
    reply_id = HiddenField()
    body = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 64)])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    body = TextAreaField('Comment', validators=[DataRequired()])
    notify = BooleanField('Notify when new comments are posted', default=True)
    submit = SubmitField(u'提交')
