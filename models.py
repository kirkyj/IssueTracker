from tracker import app
from flask_mongoengine import MongoEngine

db = MongoEngine(app)

class User(db.Document):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    firstname = db.StringField(max_length=255)
    active = db.BooleanField()
    lastname = db.StringField(max_length=255)
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