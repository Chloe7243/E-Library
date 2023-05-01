from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, PasswordField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = StringField('Name', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Submit')

class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    author = StringField('Author', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    category_id = IntegerField('Category ID', validators=[DataRequired()])
    cover_image = FileField('Cover Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    file = FileField('Book File', validators=[FileRequired(), FileAllowed(['pdf'], 'PDFs only!')])
    submit = SubmitField('Submit')

class VideoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    category_id = IntegerField('Category ID', validators=[DataRequired()])
    cover_image = FileField('Cover Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    file = FileField('Video File', validators=[FileRequired(), FileAllowed(['mp4'], 'MP4s only!')])
    submit = SubmitField('Submit')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Change Password')

class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')
