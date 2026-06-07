from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AddCustomerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    address = TextAreaField('Address')
    notes = TextAreaField('Notes')
    submit = SubmitField('Save Customer')

class AddSupplierForm(FlaskForm):
    name = StringField('Supplier Name', validators=[DataRequired()])
    collection = StringField('Collection Mapping')
    submit = SubmitField('Save Supplier')

class AddInstallerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone')
    email = StringField('Email')
    notes = TextAreaField('Notes')
    submit = SubmitField('Save Installer')