from pymongo import MongoClient
from flask import Flask, render_template, request, session
from flask_mongoengine import MongoEngine
import datetime
from forms import LoginForm, SignupForm, NewIssueForm, EditIssueForm
from flask_bootstrap import Bootstrap
from passlib.hash import pbkdf2_sha256
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import datetime
from mailer import activate_mail
#from models import db
#from models import User, DocKind, DocVersion, Versions

# DB Connector routine

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

db = MongoEngine(app)

# Flask-Bootstrap Setup

Bootstrap(app)

app.config['MONGODB_SETTINGS'] = {
    'db': 'tracker',
    'host': 'localhost',
    'port': 27017
}

class User(db.Document):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    firstname = db.StringField(max_length=255)
    lastname = db.StringField(max_length=255)
    active = db.BooleanField()
    org = db.StringField(max_length=255)
    reg_date = db.DateTimeField()

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.email)

class DocVersion(db.EmbeddedDocument):
    version = db.StringField(max_length=20)
    rel_kind = db.StringField(max_length=20)
    state = db.StringField(max_length=20)
    released = db.DateTimeField()

class DocKind(db.EmbeddedDocument):
    kind = db.StringField(max_length=20)
    versions = db.EmbeddedDocumentListField(DocVersion)

class Versions(db.Document):
    name = db.StringField(max_length=20)
    type = db.EmbeddedDocumentListField(DocKind)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#version1 = DocVersion(version = "1.0", rel_kind = "major", state = "active", released = datetime.datetime.now())
#version2 = DocVersion(version = "2.0", rel_kind = "major", state = "active", released = datetime.datetime.now())
#version21 = DocVersion(version = "2.1", rel_kind = "minor", state = "draft", released = datetime.datetime.now())
#version22 = DocVersion(version = "2.2", rel_kind = "minor", state = "draft", released = datetime.datetime.now())

#cpp_kind = DocKind(kind = "cPP", versions = [version1, version2, version21, version22])
#sd_kind = DocKind(kind = "SD", versions = [version1, version2, version21])

#fw_doc = Versions(name = "Firewall", type = [cpp_kind, sd_kind]).save()

@login_manager.user_loader
def load_user(email):
    for user in User.objects:
        if user.email == email:
            return user

def db_connect(collection):

    myClient = MongoClient('localhost', 27017)
    db = myClient.tracker
    db_collection = db[collection]

    return db_collection

@app.route("/login", methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    elif request.method == 'POST':
        for user in User.objects:
            if user.email == form.email.data:
                if user.is_active() == False:
                    return "User not activated"
                elif pbkdf2_sha256.verify(form.password.data, user.password):
                    # Password must be correct
                    login_user(user)
                    session['user'] = current_user.firstname+' '+current_user.lastname
                    print (session['user'])
                    return render_template("home.html")
                else:
                    return "Incorrect username or password"
        # If we get here, we didn't find the user email in the DB so fail login
        return "Incorrect username or password"

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    login_form = LoginForm()
    if request.method == 'GET':
        return render_template('signup.html', form = form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            for user in User.objects:
                if user.email == form.email.data:
                    return "Email address already exists"
            User(email=form.email.data, password=pbkdf2_sha256.hash(form.password.data), firstname=form.first.data, \
                 lastname=form.last.data, org=form.org.data, reg_date=datetime.datetime.now(), active=False).save()
            activate_mail(form.email.data)
            return render_template("login.html", form=login_form)
        else:
            return "Form didn't validate"

@app.route("/")
@login_required
def show_home():

    # Main App routine which displays the main home page
    # Use datatables to display the currently open issues

   return render_template('home.html')

@app.route("/myissues")
@login_required
def my_issues():
    collection = 'issues'
    db = db_connect(collection)

    result = []

    for document in db.find():
        if document['raised_by'] == current_user.get_id():
            result.append(document)

    return render_template("myissues.html", issues=result)

@app.route("/newissue", methods=['GET','POST'])
@login_required
def new_issue():

    form = NewIssueForm()
    issue = {}

    issue_db = db_connect('issues')
    #doc_db = db_connect('doc')

    #for document in doc_db.find():

    form.impact_ver.choices = [('1.0','v1.0'),('2.0','v2.0'),('2.1','v2.1')]
    if request.method == 'GET':
        #form.impact.choices =
        return render_template("addissue.html", form = form)
    elif request.method == 'POST':

        issue['title'] = form.title.data
        issue['description'] = form.desc.data
        issue['severity'] = form.sev.data
        issue['impact_doc'] = form.impact_doc.data
        issue['impact_ver'] = form.impact_ver.data
        issue['impact_area'] = form.area.data
        issue['id'] = issue_db.count()
        issue['raised_by'] = current_user.get_id()
        issue['date'] = datetime.datetime.utcnow()
        issue['state'] = 'open'
        issue['prop_resolution'] = form.prop_res.data
        issue['comments'] = []

        issue_db.insert_one(issue)
        return render_template("issueadded.html")


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

    return  render_template("openissues.html", issues=result)

@app.route("/allissues")
@login_required
def all_issues():

    collection = 'issues'
    db = db_connect(collection)

    result = []

    for document in db.find():
        document['date'] = document['date'].strftime("%A, %d. %B %Y %I:%M%p")
        result.append(document)

    return  render_template("allissues.html", issues=result)

@app.route("/resissues")
@login_required
def res_issues():

    collection = 'issues'
    db = db_connect(collection)

    result = []

    for document in db.find():
        if document['state'] == 'resolved':
            #firstseen = datetime.datetime.strptime(document['date'], "%Y-%m-%dT%H:%M:%S.%fZ")
            document['date'] = document['date'].strftime("%a, %d. %b %Y %I:%M%p")
            result.append(document)

    return  render_template("resissues.html", issues=result)

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

    form = EditIssueForm()

    db = db_connect(collection)

    document = db.find_one({"id": int(issue_id)})

    form.id.data = str(document['id'])
    form.title.data = document['title']
    form.desc.data = document['description']
    form.sev.data = document['severity']
    form.raised_by.data = document['raised_by']
    form.impact_doc.data = document['impact_doc']
    form.state.data = document['state']
    form.impact_ver.data = document['impact_ver']
    form.area.data = document['impact_area']
    form.prop_res.data = document['prop_resolution']

    comments = document['comments']
    for comment in comments:
        comment['date'] = comment['date'].strftime("%a, %d. %b %Y %I:%M%p")

    # Now we have a handle to the issue we're interested in
    # just need to pass this back via the render engine

    return render_template("viewissue.html", issue=document, form = form, id = issue_id, comments = comments)

@app.route("/updateissue", methods=['GET','POST'])
@login_required
def update():

    form = EditIssueForm()
    issue_id = request.args.get("id")
    db = db_connect('issues')
    new_comment = {}

    document = db.find_one({"id": int(issue_id)})
    db.delete_one({'_id': document['_id']})
    document.pop('_id')

    document['title'] = form.title.data
    document['description'] = form.desc.data
    document['severity'] = form.sev.data
    document['impact_doc'] = form.impact_doc.data
    document['impact_area'] = form.area.data
    document['state'] = form.state.data
    document['impact_ver'] = form.impact_ver.data
    document['prop_resolution'] = form.prop_res.data

    document['last_update'] = datetime.datetime.utcnow()
    document['last_update_by'] = current_user.get_id()

    comments = document['comments']

    #print (comments)

    if form.comment.data != '':
        new_comment['comment'] = form.comment.data
        new_comment['user_id'] = current_user.get_id()
        new_comment['date'] = datetime.datetime.utcnow()
        comments.append(new_comment)

    print(document)
    document['comments'] = comments
    print (document)
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

@app.route("/logout")
@login_required
def logout():
    logout_user()
    form = LoginForm()
    return render_template("login.html", form = form)

@app.route("/roadmap")
@login_required
def roadmap():
    return "Roadmap"

if __name__ == '__main__':
    app.run(port=5000, host='localhost')