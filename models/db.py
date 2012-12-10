# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite')
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db = db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################
from datetime import datetime
from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
db.define_table(
    auth.settings.table_user_name,
    Field('username', length=128, default=''),
    Field('email', length=128, default='', unique=True), # required
    Field('password', 'password', length=512,            # required
          readable=False, label='Password'),
    Field('date_joined', 'datetime', writable=False, 
          readable=False, default=datetime.utcnow()),
    Field('last_access', 'datetime', writable=True, 
          readable=False, default=datetime.utcnow()),
    Field('registration_key', length=512,                # required
          writable=False, readable=False, default=''),
    Field('reset_password_key', length=512,              # required
          writable=False, readable=False, default=''),
    Field('registration_id', length=512,                 # required
          writable=False, readable=False, default=''))

## do not forget validators
custom_auth_table = db[auth.settings.table_user_name] # get the custom_auth_table
custom_auth_table.username.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
custom_auth_table.username.requires = IS_NOT_IN_DB(db, custom_auth_table.username)
custom_auth_table.password.requires = [IS_STRONG(), CRYPT()]
custom_auth_table.email.requires = [
  IS_EMAIL(error_message=auth.messages.invalid_email),
  IS_NOT_IN_DB(db, custom_auth_table.email)]
custom_auth_table.last_access.readable=custom_auth_table.last_access.writable = False

auth.settings.table_user = custom_auth_table # tell auth to use custom_auth_table

auth.define_tables(username=False, signature=False)

## configure email
mail=auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth,filename='private/janrain.key')

#########################################################################

db.define_table('category',
    Field('name', 'string'),
    format = '%(name)s'
)

db.category.name.requires = IS_NOT_IN_DB(db, db.category.name)

db.define_table('algorithm',
    Field('name', 'string'),
    Field('category', 'reference category'),
    Field('author', db.auth_user, default=auth.user_id),
    Field('date_created', 'datetime', default=datetime.utcnow()),
    Field('code', 'text'),
    Field('rating_total', 'double', default=0),
    Field('times_rated', 'integer', default=0),
    format = '%(name)s'
)

db.algorithm.name.requires = IS_NOT_EMPTY()
db.algorithm.author.readable = db.algorithm.author.writable = False
db.algorithm.date_created.readable = db.algorithm.date_created.writable = False
db.algorithm.rating_total.readable=db.algorithm.rating_total.writable=False
db.algorithm.times_rated.readable=db.algorithm.times_rated.writable=False
db.algorithm.code.requires = IS_NOT_EMPTY()

db.define_table('comment',
    Field('author', db.auth_user, default=auth.user_id),
    Field('algorithm', 'reference algorithm'),
    Field('date_written', 'datetime', default=datetime.utcnow()),
    Field('body', 'text')
)

db.comment.author.readable = db.comment.author.writable = False
db.comment.algorithm.readable = db.comment.algorithm.writable = False
db.comment.date_written.readable = db.comment.date_written.writable = False
db.comment.body.requires = IS_NOT_EMPTY()

#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
