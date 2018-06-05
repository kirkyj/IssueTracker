from secrets import gmailpass, secret_key

DEBUG = True
SECRET_KEY = secret_key

MONGODB_HOST = '127.0.0.1'
MONGODB_PORT = 27017
MONGODB_DB = 'tracker'


SECURITY_LOGIN_USER_TEMPLATE = 'security/login.html'
SECURITY_REGISTER_USER_TEMPLATE = 'security/signup.html'
SECURITY_REGISTER_URL = '/signup'
SECURITY_REGISTERABLE = True
SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
SECURITY_PASSWORD_SALT = 'somesalt'
SECURITY_SEND_REGISTER_EMAIL = True
SECURITY_POST_LOGIN_VIEW = '/myissues'
SECURITY_EMAIL_SENDER = 'ccnditc@gmail.com'
SECURITY_CONFIRMABLE = True
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'ccnditc@gmail.com'
MAIL_PASSWORD = gmailpass
MAIL_DEFAULT_SENDER = 'ccnditc@gmail.com'
SECURITY_TOKEN_MAX_AGE = 60