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

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
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
from datetime import datetime

db.define_table('user',
    Field('name', 'string'),
    Field('date_joined', 'datetime', default=datetime.utcnow()),
    Field('email', 'string'),
    Field('algorithms', 'list:reference algorithm'),
    Field('comments', 'list:reference comment'),
    format='%(name)s'
)

db.user.name.requires = IS_NOT_EMPTY()
db.user.email.requires = IS_EMAIL()

db.define_table('algorithm',
    Field('name', 'string'),
    Field('author', 'reference user'),
    Field('date_created', 'datetime', default=datetime.utcnow()),
    Field('code', 'text'),
    format = '%(name)s'
)

db.algorithm.name.requires = IS_NOT_EMPTY()
db.algorithm.author.requires = IS_IN_DB(db, db.user.id, '%(name)s')
db.algorithm.date_created.readable = db.algorithm.date_created.writable = False
db.algorithm.code.requires = IS_NOT_EMPTY()

db.define_table('comment',
    Field('author', 'reference user'),
    Field('algorithm', 'reference algorithm'),
    Field('date_written', 'datetime', default=datetime.utcnow()),
    Field('body', 'text')
)

db.comment.algorithm.readable = db.comment.algorithm.writable = False
db.comment.date_written.readable = db.comment.date_written.writable = False
db.comment.body.requires = IS_NOT_EMPTY()
db.comment.author.requires = IS_IN_DB(db, db.user.id, '%(name)s')

#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
