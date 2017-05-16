# encoding: utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import Optional, Length, URL, Email, DataRequired
from flask_pagedown.fields import PageDownField


class ProfileForm(FlaskForm):
    name = StringField(u'昵称', validators=[Optional(), Length(1, 64)])
    location = StringField(u'位置', validators=[Optional(), Length(1, 64)])
    bio = TextAreaField(u'简介')
    submit = SubmitField(u'提交')


class TalkForm(FlaskForm):
    title = StringField(u'标题', validators=[DataRequired(), Length(1, 128)])
    description = TextAreaField(u'描述')
    # slides = StringField('Slides Embed Code (450 pixels wide)')
    # video = StringField('Video Embed Code (450 pixels wide)')
    venue = StringField(u'地点',
                        validators=[Length(1, 128)])
    venue_url = StringField(u'地点链接',
                            validators=[Optional(), Length(1, 128), URL()])
    # date = DateField(u'日期')
    submit = SubmitField(u'提交')

    def from_model(self, talk):
        self.title.data = talk.title
        self.description.data = talk.description
        # self.slides.data = talk.slides
        # self.video.data = talk.video
        self.venue.data = talk.venue
        self.venue_url.data = talk.venue_url
        # self.date.data = talk.date

    def to_model(self, talk):
        talk.title = self.title.data
        talk.description = self.description.data
        # talk.slides = self.slides.data
        # talk.video = self.video.data
        talk.venue = self.venue.data
        talk.venue_url = self.venue_url.data
        # talk.date =


class PresenterCommentForm(FlaskForm):
    body = PageDownField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 64)])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    body = PageDownField('Comment', validators=[DataRequired()])
    notify = BooleanField('Notify when new comments are posted', default=True)
    submit = SubmitField(u'提交')
