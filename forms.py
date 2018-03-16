from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, BooleanField
from wtforms.validators import Email, DataRequired, EqualTo
from flask_security import RegisterForm, ConfirmRegisterForm

class ExtendedLoginForm(FlaskForm):
    somefield = StringField('test', validators=[DataRequired()])

class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Login")

"""class SignupForm(RegisterForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    #email = StringField('E-mail', validators=[DataRequired(), Email()])
    #password = PasswordField('Password', validators=[DataRequired()])
    #conf_password = PasswordField('Repeat Password', validators=[DataRequired(),EqualTo('password', message='Passwords must match')])
    org = StringField('Organisation')
    #submit = SubmitField("Sign up")"""

class SignupForm(ConfirmRegisterForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    #email = StringField('E-mail', validators=[DataRequired(), Email()])
    #password = PasswordField('Password', validators=[DataRequired()])
    #conf_password = PasswordField('Repeat Password', validators=[DataRequired(),EqualTo('password', message='Passwords must match')])
    org = StringField('Organisation')
    #submit = SubmitField("Sign up")

class NewIssueForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    desc = TextAreaField('Description', validators=[DataRequired()])
    sev = SelectField('Severity', choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])
    impact_doc = SelectField('Document Impacted', choices=[('networkcpp', 'Network cPP'),('networksd', 'Network SD'), ('firewallcpp', 'Firewall cPP'), ('firewallsd', 'Firewall SD')])
    #impact_doc = BooleanField('Document Impacted', choices=[('networkcpp', 'Network cPP'),('networksd', 'Network SD'), ('firewallcpp', 'Firewall cPP'), ('firewallsd', 'Firewall SD')])
    #impact_doctype = SelectField('', choices=[('cpp', 'cPP'), ('sd', 'SD')])
    impact_ver = SelectField('Impacted Version', validators=[DataRequired()])
    area = StringField('Paragraph, Section or Page', validators=[DataRequired()])
    prop_res = TextAreaField('Proposed Resolution', validators=[DataRequired()])
    submit = SubmitField('Create')

class EditIssueForm(FlaskForm):
    id = StringField('Issue ID')
    title = StringField('Title', validators=[DataRequired()])
    desc = TextAreaField('Description', validators=[DataRequired()])
    sev = SelectField('Severity', choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])
    impact_doc = SelectField('Document Impacted', choices=[('networkcpp', 'Network cPP'), ('networksd', 'Network SD'),
                                                           ('firewallcpp', 'Firewall cPP'),
                                                           ('firewallsd', 'Firewall SD')])
    state = SelectField('State', choices=[('open','Open'), ('resolved','Resolved')])
    raised_by = StringField('Submitted by')
    # ToDo Use a dynamic selection field for allocated_to based on the users in the user_DB
    allocated_to = SelectField('Allocated to')
    impact_ver = SelectField('Impacted Version', choices = [('1.0','v1.0'),('2.0','v2.0'),('2.1','v2.1')], validators=[DataRequired()])
    # ToDo do I also need an additional field to identify who resolved the issue as well as how it was resolved (accepted etc.)
    # ToDo may also need an 'owner' field to identify who is handling the issue. As well as a resolution field
    res_state = SelectField('Resolution State', choices=[('no_change', 'No Change'), ('accept', 'Accept'), ('accept_w_mods', 'Accept with Modification'), ('roadmap','Roadmap')])
    resolution = TextAreaField('Resolution', validators=[DataRequired()])
    resolved_in = SelectField('Resolved in Version', choices=[('2.1','v2.1'), ('2.2','v2.2'),('3.0','v3.0')])
    area = StringField('Paragraph, Section or Page', validators=[DataRequired()])
    prop_res = TextAreaField('Proposed Resolution', validators=[DataRequired()])
    comment = TextAreaField('Comment')
    submit = SubmitField('Create')

class NewRequirement(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    desc = StringField('Description', validators=[DataRequired()])

class NewReleaseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    version = StringField('Version', validators=[DataRequired()])
    kind = SelectField('Kind', choices=[('cPP','cPP'), ('SD','SD')])
    release = SelectField('Release Type', choices=[('major','Major'), ('minor','Minor')])
    submit = SubmitField('Create')

