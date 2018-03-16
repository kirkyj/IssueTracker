from flask import Flask, render_template, request, session, Response, current_app, flash, url_for
from pymongo import MongoClient
from flask_mongoengine import MongoEngine
from flask_security import MongoEngineUserDatastore, Security, url_for_security, user_registered, UserMixin, RoleMixin, login_required, current_user
from forms import SignupForm, NewIssueForm, EditIssueForm
from flask_bootstrap import Bootstrap
import datetime
from flask_principal import RoleNeed, Permission
import io
import csv
from flask_mail import Mail


# Flask Setup

app = Flask(__name__)
app.config.from_pyfile('config.py')

# MongoEngine Setup

db = MongoEngine(app)

# Flask-Bootstrap Setup

Bootstrap(app)

# Flask-Mail Setup

mail = Mail(app)

# User Class for Flask-Security

class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)

class User(db.Document, UserMixin):

    firstname = db.StringField(max_length=255)
    lastname = db.StringField(max_length=255)
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    org = db.StringField(max_length=255)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])
    active = db.BooleanField(default=True)

    def list_roles(self):
        entry = []
        for r in self.roles:
            entry.append(r.name)
        return entry

    #def get_id(self):
    #    return str(self.email)

    #Could Add some addition functions here to deal with listing the user roles etc.

# Flask-Security Setup and Configuration

user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore, confirm_register_form=SignupForm)

# Flask_Principal Role Setup

admin_role = user_datastore.find_or_create_role('admin')
editor_role = user_datastore.find_or_create_role('editor')
member_role = user_datastore.find_or_create_role('member')

admin_permission = Permission(RoleNeed('admin'))
editor_permission = Permission(RoleNeed('editor'))
member_permission = Permission(RoleNeed('member'))

# MongoDB Connection Function

def db_connect(collection):

    myClient = MongoClient('localhost', 27017)
    db = myClient.tracker
    db_collection = db[collection]

    return db_collection

# Flask Routing Defintions

@app.context_processor
def login_context():
    return {
        'url_for_security': url_for_security
    }

# Connect to the user_registered signal to add in
# some additional aspects to the user account during registration

@user_registered.connect_via(app)
def user_reg(sender, user, confirm_token):
    # Automatically add the member role to all users during registration
    user_datastore.add_role_to_user(user, member_role)
    # Should also de-activate all users until manual activation?


@app.route("/")
@login_required
def show_home():

    # ToDo Better home page with some summary information included.

   return render_template('home.html')

@app.route("/openissues")
@login_required
def open_issues():

    collection = 'issues'
    db = db_connect(collection)

    result = []

    for document in db.find():
        if document['state'] == 'open':
            document['date'] = document['date'].strftime("%A, %d. %B %Y %I:%M%p")
            result.append(document)

    return render_template("openissues.html", issues=result)

@app.route("/myissues")
@login_required
def my_issues():

    collection = 'issues'
    db = db_connect(collection)

    result = []

    for document in db.find():
        if document['raised_by'] == current_user.email:
            document['date'] = document['date'].strftime("%A, %d. %B %Y %I:%M%p")
            result.append(document)

    return render_template("myissues.html", issues=result)

@app.route("/allissues")
@login_required
def all_issues():

    collection = 'issues'
    db = db_connect(collection)

    result = []

    for document in db.find():
        document['date'] = document['date'].strftime("%A, %d. %B %Y %I:%M%p")
        result.append(document)

    return render_template("allissues.html", issues=result)

@app.route("/resissues")
@login_required
def res_issues():

    collection = 'issues'
    db = db_connect(collection)

    result = []

    for document in db.find():
        if document['state'] == 'resolved':
            document['date'] = document['date'].strftime("%a, %d. %b %Y %I:%M%p")
            result.append(document)

    return  render_template("resissues.html", issues=result)

@app.route("/newissue", methods=['GET','POST'])
@login_required
def new_issue():

    form = NewIssueForm()
    issue = {}

    # Todo Add in ability to tag an issue as a NIT issue with associated identifier

    issue_db = db_connect('issues')

    form.impact_ver.choices = [('1.0','v1.0'),('2.0','v2.0'),('2.1','v2.1')]

    if request.method == 'GET':
        return render_template("addissue.html", form = form)
    elif request.method == 'POST':

        issue['title'] = form.title.data
        issue['description'] = form.desc.data
        issue['severity'] = form.sev.data
        issue['impact_doc'] = form.impact_doc.data
        issue['impact_ver'] = form.impact_ver.data
        issue['impact_area'] = form.area.data
        issue['id'] = issue_db.count()
        issue['raised_by'] = current_user.email
        issue['allocated_to'] = ''
        issue['date'] = datetime.datetime.utcnow()
        issue['state'] = 'open'
        issue['prop_resolution'] = form.prop_res.data
        # This may not be needed, or the check in the 'viewissues route might not be needed since all issues
        # will have an empty comments array...Check on best way to handle
        issue['comments'] = []

        issue_db.insert_one(issue)

        # Todo need to find a better response template

        return render_template("issueadded.html")


@app.route("/newrelease", methods=['GET','POST'])
@login_required
def new_release():

    form = NewReleaseForm()

    if request.method == 'GET':
        return render_template('newrelease.html', form = form)
    elif request.method == 'POST':
        # Get the form data
        # Ensure it isn't already in the database
        # If not, add it to the database
        # Maybe use some JS and AJAX to dynamically change the page to simply state
        # that the data is already in the DB?
        # Use an AJAX call to post the form data and if not found then
        # actually add the data to the form.
        # Only allow a new version to be added as we know there is only ever going to be
        # FW and Network
        return "Do Stuff"


@app.route("/viewissue")
@login_required
def view_issue():

    issue_id = request.args.get("id")
    collection = 'issues'
    user_db = db_connect('user')
    users = []
    choices = []
    form = EditIssueForm()

    #if current_user.has_role('admin') or current_user.has_role('editor'):
    #    form.state.choices=[('open','Open'),('resolved','Resolved')]
    #else:
    #    form.state.choices = [('open', 'Open')]

    # Populate the 'Allocated To' form element using the current list of registered users

    for user in user_db.find():
        users.append(user_datastore.get_user(user['email']))

    choices.append(('',''))

    for entry in users:
        choice = (entry.email, entry.email)
        choices.append(choice)
        choice = ()

    form.allocated_to.choices = choices

    db = db_connect(collection)

    document = db.find_one({"id": int(issue_id)})

    form.id.data = str(document['id'])
    form.title.data = document['title']
    form.desc.data = document['description']
    form.sev.data = document['severity']
    form.raised_by.data = document['raised_by']
    form.allocated_to.data = document['allocated_to']
    form.impact_doc.data = document['impact_doc']
    form.state.data = document['state']
    form.impact_ver.data = document['impact_ver']
    form.area.data = document['impact_area']
    form.prop_res.data = document['prop_resolution']
    # Add a fixed-in drop down if the role is editor or admin

    if document['state'] == 'resolved':
        form.res_state.data = document['resolution_state']
        form.resolution.data = document['resolution']
        if form.res_state.data == 'accept' or form.res_state.data == 'accept_w_mods' or form.res_state.data == 'roadmap':
            form.resolved_in.data = document['resolved_in']

    try:
        comments = document['comments']
        for comment in comments:
            comment['date'] = comment['date'].strftime("%a, %d. %b %Y %I:%M%p")
        return render_template("viewissue.html", issue=document, form=form, id=issue_id, comments=comments)
    except:
        return render_template("viewissue.html", issue=document, form=form, id=issue_id)

    # Now we have a handle to the issue we're interested in
    # just need to pass this back via the render engine


@app.route("/updateissue", methods=['GET','POST'])
@login_required
def update():

    form = EditIssueForm()

    # Grab the Issue ID from the form POST

    issue_id = request.args.get("id")

    # Connect to the Issues DB

    db = db_connect('issues')
    new_comment = {}

    # Find the issue in the DB that we're about to update and store a copy of it in 'document'
    # After this, we delete it from the DB and then strip of the MongoDB _id identifier as we don't need this

    document = db.find_one({"id": int(issue_id)})
    db.delete_one({'_id': document['_id']})
    document.pop('_id')

    # Update all of the fields of the issue from the submitted form data

    document['title'] = form.title.data
    document['description'] = form.desc.data
    document['severity'] = form.sev.data
    document['impact_doc'] = form.impact_doc.data
    document['impact_area'] = form.area.data
    # Insert check to make sure the person that submitted the data was actually an admin/editor role, i.e. the data was just posted/injected!

    # Need to insert a check to avoid status being set to 'None' because of the field not being present in the form.
    if current_user.has_role('admin') or current_user.has_role('editor'):
        document['state'] = form.state.data
    if form.state.data == 'resolved':
        document['resolution_state'] = form.res_state.data
        document['resolution'] = form.resolution.data
        # Tag who resolved/closed the issue?
        if form.res_state.data == 'accept' or form.res_state.data == 'accept_w_mods' or form.res_state.data == 'roadmap':
            document['resolved_in'] = form.resolved_in.data
            document['resolved_by'] = current_user.email

    document['impact_ver'] = form.impact_ver.data
    document['prop_resolution'] = form.prop_res.data
    document['allocated_to'] = form.allocated_to.data

    document['last_update'] = datetime.datetime.utcnow()
    document['last_update_by'] = current_user.email

    document['resolution_state'] = form.res_state.data
    document['resolution'] = form.resolution.data
    document['resolved_in'] = form.resolved_in.data

    # Grab a copy of the current comments associated with the issue. After first checking if there
    # are comments already in the document

    if 'comments' in document.keys():
        comments = document['comments']

    if form.comment.data != '':
        new_comment['comment'] = form.comment.data
        new_comment['user_id'] = current_user.email
        new_comment['date'] = datetime.datetime.utcnow()
        comments.append(new_comment)

    document['comments'] = comments

    db.insert_one(document)

    #db.update_one({'_id': document['_id']},
     #             {"$set": {"title": form.title.data, "desc": form.desc.data, "sev": form.sev.data,
     #                       "impact_doc": form.impact_doc.data, "state": form.state.data,
      #                      "impact_ver": form.impact_ver.data, "impact_area": form.area.data,
       #                     "prop_resolution": form.prop_res.data}})

    # Remove the old document from the DB
    # Copy all of the mutable data from the form in to an updated document.
    # Keep the id, date and raised_by the same (these can't be updated by the form so shouldn't be a problem
    # ToDo need to check it status changed to resolved and if so, tag the ID of the user that changed the state
    # ToDo need to check the state and if resolved, don't allow editing of the issue, except adding comments

    #if form.comment.data != '':
     #   commentor = current_user.get_id()
     #   db.update_one({'_id': document['_id']},
     #                 {"$set": {"comments.})


    return render_template("issueadded.html")
    # Todo Need to grab the comment field and add this in to the DB tagged with the current userID
    # Todo Better response to the edited issue page

@app.route("/roadmap")
@login_required
def roadmap():

    """ Need to iterate over the DB and find all issues in a resolved state
        and then go through each one and allocate them to the view accordingly. AN alternative could be that when
        an issue is resolved, it gets copied to a new collection in the DB which then saves a load of
        querying. """

    issue_db = db_connect('issues')

    resolved_issues = []

    for issue in issue_db.find():
        if issue['state'] == 'resolved' and issue['state'] != 'no_change':
            resolved_issues.append(issue)

    # Now we have a list of resolved issues

    print (resolved_issues)

    #for item in resolved_issues:

    return render_template('roadmap.html', issues = resolved_issues)

@app.route("/admin")
@login_required
@admin_permission.require()
def admin():

    user_db = db_connect('user')

    users = []

    for user in user_db.find():
        users.append(user_datastore.get_user(user['email']))
    print (users)
    for entry in users:
        print (entry.email)
        print (entry.list_roles())
    return render_template("admin.html", users=users)

@app.route("/upload", methods=['POST'])
@login_required
def upload_issues():

    upload = []

    issue_db = db_connect('issues')

    severity = {'1' : 'Low', '2' : 'Medium', '3' : 'High'}

    if request.method == 'GET':
        return render_template('upload.html')
    elif request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)

        csv_input = csv.reader(stream)

        for row in csv_input:
            entry = {}

            if row[0] != '' and row[4] != 'Severity':
                entry['title'] = row[0]
                entry['impact_area'] = row[1]
                entry['description'] = row[2]
                entry['prop_resolution'] = row[3]
                entry['severity'] = severity[row[4]]
                entry['date'] = datetime.datetime.utcnow()
                entry['allocated_to'] = ''
                entry['state'] = 'open'
                entry['id'] = issue_db.count()
                entry['comments'] = []
                entry['raised_by'] = 'marjacks@cisco.com'

                entry['impact_doc'] = row[5]
                entry['impact_ver'] = row[6]

                issue_db.insert_one(entry)

        #print (upload[1])

        return "Uploaded"

if __name__ == '__main__':
    app.run(port=5000, host='localhost')




