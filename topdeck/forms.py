# TopDeck is provided under the Mozilla Public License Version 2.0
# All other included code and work is provided under their respective License
# 
# TopDeck written by jmp_xien:
# github.com/jmp_xien

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, \
     RadioField, SelectMultipleField, FileField, TextAreaField, HiddenField, validators
from wtforms.validators import ValidationError, InputRequired, DataRequired, \
    Email, EqualTo, Length
from topdeck.process import get_ethernet


kwph='placeholder'
kw0={kwph: 'Enter Info'}
kw1={kwph: 'Username'}
kw2={kwph: 'Password'}
kw3={kwph: 'Email'}
kw4={kwph: 'Host Name'}
kw5={kwph: 'IP Address'}
kw6={kwph: 'Service'}


class ServerConf(FlaskForm):
    sid = HiddenField('uid', validators=[DataRequired()])    
    hostname = StringField(u'Server Hostname', validators=[DataRequired()],
        render_kw=kw0) 
    daship = StringField(u'Dashboard IP', validators=[DataRequired()],
        render_kw=kw0) 
    dashport = StringField(u'Dashboard Port', validators=[DataRequired()],
        render_kw=kw0)         
    basedir = StringField(u'Base Directory', validators=[DataRequired()],
        render_kw=kw0)
    logdir = StringField(u'Log Directory', validators=[DataRequired()],
        render_kw=kw0)
    contdir = StringField(u'Container Directory', validators=[DataRequired()],
        render_kw=kw0)
    dnsip = StringField(u'DNS Server IP Address', validators=[DataRequired()],
        render_kw=kw0)   
    domain = StringField(u'Container Domain', validators=[DataRequired()],
        render_kw=kw0)     
    submit = SubmitField(label=('Submit'))


class LoginForm(FlaskForm):
    username = StringField(u'User ID', validators=[DataRequired()],
        render_kw=kw1)
    password = PasswordField(u'Password', validators=[DataRequired()],
        render_kw=kw2)
    submit = SubmitField(label=('Log-In'))


class BaseUser(FlaskForm):
    username = StringField(u'User ID', validators=[DataRequired()],
        render_kw=kw1)
    email = StringField(u'Email', validators=[DataRequired()],
        render_kw=kw3)
    admin = RadioField('Admin User', validators=[DataRequired()],
        choices=[('No', 'No'), ('Yes', 'Yes')], default='No')        


class UserAdd(BaseUser):
    password = PasswordField(u'Password', validators=[
        validators.Length(min=6, max=24),
        validators.EqualTo('password_confirm', 
        message='Passwords do not match')], render_kw=kw2)
    password_confirm = PasswordField(u'Password confirm', validators=[
        validators.Length(min=6, max=24)], render_kw=kw2)
    submit = SubmitField(label=('Add User'))


class UserUpdate(BaseUser):
    uid = HiddenField('uid', validators=[DataRequired()])
    password = PasswordField(u'Password', render_kw=kw2)
    password_confirm = PasswordField(u'Confirm Password', render_kw=kw2)
    admin = SelectField('Admin User', choices=None,
        validators=[DataRequired()])
    submit = SubmitField(label=('Update User'))


class BaseContConf(FlaskForm):
    form_type = "Form"
    ethlist = get_ethernet(form_type)
    hostname = StringField(u'Container Name', validators=[DataRequired()],
        render_kw=kw4)
    ipaddress = StringField(u'IP Address', validators=[DataRequired()],
        render_kw=kw5)
    ethernet = SelectField('Net Interface', choices=ethlist,
        validators=[DataRequired()], render_kw=kw0)
    options = StringField(u'Container Options', render_kw=kw0)


class ContainerConf(BaseContConf):
    submit = SubmitField(label=('Add Container'))


class ContUpdateConf(BaseContConf):
    cid = HiddenField('cid', validators=[DataRequired()])
    submit = SubmitField(label=('Update Container'))


class ContServiceState(BaseContConf):
    cid = HiddenField('cid', validators=[DataRequired()])
    submit = SubmitField(label=("Run"))


class UpdateRCconf(BaseContConf):
    cid = HiddenField('cid')
    rccfdata = TextAreaField(u'Caution:', render_kw=kw0)
    submit = SubmitField(label=("Update File"))


class UpdatePeriConf(BaseContConf):
    cid = HiddenField('cid')
    peridata = TextAreaField(u'Caution:', render_kw=kw0)
    submit = SubmitField(label=("Update File"))


class ContServiceForm(FlaskForm):
    contservice = StringField(u'Service Name', validators=[DataRequired()],
        render_kw=kw6)
    contsvcstatus = HiddenField('Status')
    query = StringField(u'Search Packages', render_kw=kw0)
    submit = SubmitField(label=('Add Service'))


class ShellInstallForm(ContServiceForm):
    contservice = HiddenField(u'Service Name')
    submit = SubmitField(label=('Install'))


class ContUserForm(FlaskForm):
    cuid = HiddenField('contuid')
    contoption = HiddenField('Cont Option')    
    contusrstat = HiddenField('Cont Usr Status')
    contuser = StringField(u'User ID', validators=[DataRequired()],
        render_kw=kw1)
    contuserpwd = PasswordField(u'Password', render_kw=kw2)
    contuserpwd_conf = PasswordField(u'Confirm Password', render_kw=kw2)
    submit = SubmitField(label=('Submit'))
