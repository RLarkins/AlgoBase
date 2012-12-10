# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
from datetime import timedelta

def logLastAccess():
    if auth.is_logged_in() == True:
        db(db.auth_user.id == auth.user_id).update(last_access = datetime.utcnow())
        db.commit
        
def makeActiveUserList():
    activeusers = []
    if db().select(db.auth_user.ALL) != None:
        authlist = db().select(db.auth_user.ALL)
        for user in authlist:
            if((datetime.utcnow() - user.last_access) < timedelta(minutes = 5)):
                activeusers.append(user)
    return activeusers

def index():
    logLastAccess()
    onlineusers = makeActiveUserList()
    algos = db().select(db.algorithm.ALL)
    categories = db().select(db.category.name)
    lastComment = db().select(db.comment.ALL, orderby = db.comment.date_written).first();
    form = SQLFORM.factory(
        Field('term', 'string')
    );
    if form.process().accepted:
        redirect(URL('search', args=form.vars.term))
    return dict(algos=algos,categories=categories,form=form,lastcomment=lastComment,onlineusers=onlineusers)

def rating_user_logged(form):
    if auth.is_logged_in():
        return
    else:
        form.errors.rating = 'You need to be logged in to do this!'

def comment_user_logged(form):
    if auth.is_logged_in():
        return
    else:
        form.errors.body = 'You need to be logged in to do this!'

def view():
    logLastAccess()
    algo = db.algorithm(request.args[0]) or redirect(URL('index'))
    rate = SQLFORM.factory(
        Field('rating', 'integer', requires=IS_INT_IN_RANGE(1, 6))
    )
    if rate.process(onvalidation=rating_user_logged).accepted:
        curr_total = algo.rating_total
        curr_times = algo.times_rated
        curr_total += rate.vars.rating
        curr_times += 1
        db(db.algorithm.id == request.args[0]).update(rating_total=curr_total)
        db(db.algorithm.id == request.args[0]).update(times_rated=curr_times)
        db.commit
        session.flash = T('Rated successfully!')
        redirect(URL('view', args=algo.id))
    comments = db(db.comment.algorithm==algo.id).select()
    db.comment.algorithm.default = algo.id
    form = SQLFORM(db.comment)
    if form.process(onvalidation=comment_user_logged).accepted:
        session.flash = T('Comment added')
        redirect(URL('view', args=algo.id))
    return dict(algo=algo, form=form, comments=comments, rate=rate)

@auth.requires_login()
def add():
    logLastAccess()
    form = SQLFORM(db.algorithm)
    if form.process().accepted:
        session.flash = T('Algorithm added')
        redirect(URL('index'))
    return dict(form=form)

def search():
    logLastAccess()
    results = db(db.algorithm.name.contains(request.args[0])).select()
    return dict(results=results)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
