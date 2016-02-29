# encoding: utf-8
from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import Optional, Length, Required, URL, Email
from flask.ext.pagedown.fields import PageDownField


class ProfileForm(Form):
    name = StringField(u'姓名', validators=[Optional(), Length(1, 64)])
    location = StringField(u'位置', validators=[Optional(), Length(1, 64)])
    bio = TextAreaField('Bio')
    submit = SubmitField(u'提交')


class TalkForm(Form):
    title = StringField(u'标题', validators=[Required(), Length(1, 128)])
    description = TextAreaField(u'描述')
    # slides = StringField('Slides Embed Code (450 pixels wide)')
    # video = StringField('Video Embed Code (450 pixels wide)')
    venue = StringField(u'地点',
                        validators=[Required(), Length(1, 128)])
    venue_url = StringField(u'地点链接',
                            validators=[Optional(), Length(1, 128), URL()])
    date = DateField(u'日期')
    submit = SubmitField(u'提交')

    def from_model(self, talk):
        self.title.data = talk.title
        self.description.data = talk.description
        # self.slides.data = talk.slides
        # self.video.data = talk.video
        self.venue.data = talk.venue
        self.venue_url.data = talk.venue_url
        self.date.data = talk.date

    def to_model(self, talk):
        talk.title = self.title.data
        talk.description = self.description.data
        # talk.slides = self.slides.data
        # talk.video = self.video.data
        talk.venue = self.venue.data
        talk.venue_url = self.venue_url.data
        talk.date = self.date.data


class PresenterCommentForm(Form):
    body = PageDownField('Comment', validators=[Required()])
    submit = SubmitField('Submit')


class CommentForm(Form):
    name = StringField('Name', validators=[Required(), Length(1, 64)])
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    body = PageDownField('Comment', validators=[Required()])
    notify = BooleanField('Notify when new comments are posted', default=True)
    submit = SubmitField(u'提交')
