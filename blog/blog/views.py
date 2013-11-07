# -*- coding: utf-8 -*-
from datetime import datetime

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import (HTTPNotFound,
                                    HTTPInternalServerError,
                                    HTTPFound,
                                    HTTPBadRequest)
from pyramid.security import remember, forget

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from pyatom import AtomFeed

from models import (Article,
                    dbSession,
                    User,
                    Project)

def blog_list_view(request):
        """Homepage view.
        Displays recent blog post list"""

        session = dbSession()
        articlesByPage = 5
        renderDictList = []
        category = None
        nbArticles = session.query(Article).count()
        nbPageList = range(1,nbArticles/articlesByPage + 1)
        if nbPageList == []:
                nbPageList.append(1)
        try:
                page = request.matchdict['page']
        except KeyError:
                page=0
        try:
                page = int(page)
        except ValueError:
                page=0
        if (page > nbArticles/articlesByPage - 1):
                page=0
        try:
                category = request.matchdict['category']
                query = session.query(Article).order_by(desc('id')).\
                        filter(Article.categories.any(name=category))\
                        [(articlesByPage * page) :\
                        (page * articlesByPage) + articlesByPage]
        except KeyError:
                query = session.query(Article).order_by(desc('id'))\
                        [(articlesByPage * page) :\
                        (page * articlesByPage) + articlesByPage]        
         
        for article in query:
                renderDictList.append({'title' : article.title,\
                                       'date' : article.date.\
                                       strftime("%d/%m/%y %H:%M"),\
                                       'author' : article.author,\
                                       'content' : article.content\
                                       [:article.content.rfind('</p>',0,200)]+\
                                       " ...",'id' : article.id})
        session.close()
        return {'renderDictList' : renderDictList,\
                'pageList' : nbPageList, 'category' : category}

def blog_article_view(request):
        """Display a blog article.
        """

        session = dbSession()
        try:
                articleId = request.matchdict['articleId']
        except KeyError:
                session.close()
                raise HTTPNotFound()
        article = session.query(Article).filter(Article.id == articleId).all()
        session.close()
        if len(article) > 1:
                raise HTTPInternalServerError()
        if len(article) == 0:
                raise HTTPNotFound()
        article = article[0]
        renderDict = {'title' : article.title,\
                      'date' : article.date.strftime("%d/%m/%y %H:%M"),\
                      'author' : article.author,\
                      'content' : article.content}
        return {'article' : renderDict}

def project_view(request):
	"""Displays a project"""

        try:
                projectId = int(request.matchdict['projectId'])
        except KeyError:
                projectId = 1
        except ValueError:
                raise HTTPNotFound
        projectList = Project.getProjectsList()
        selectedProject=None
        renderDictList = []
        for project in projectList:
	        renderDictList.append(project.toDict())
                if project.id == projectId:
                        selectedProject = project
        if selectedProject == None:
                raise HTTPNotFound()
        return {'project':selectedProject.toDict(),
                'renderDictList':renderDictList}



def atom(request):
        """Display atom feed
        """
    
        feed = AtomFeed(title="Alternativebit",
                        subtitle="Alternativebit",
                        feed_url="http://www.alternativebit.fr/atom",
                        url="http://alternativebit.fr",
                        author="Ninja Trappeur")
        session = dbSession()
        query = session.query(Article).order_by(desc('id'))[0:14]
        session.close()
        for article in query:
                feed.add(title=article.title,
                        content=article.content,
                        content_type="html",
                        author=article.author,
                        url="http://www.alternativebit.fr/article/{0}".format(article.id),
                        updated=article.date)
        return Response(feed.to_string())


def login(request):
        """Login view
        """

        previous_location = request.params.get('came_from',
                                            request.route_url('home'))
        post_data = request.POST
        if 'submit' in post_data:
                username = post_data['username']
                password = post_data['password']
                if User.check_user_password(username, password):
                        headers = remember(request, username)
                        request.session.flash('Log in.')
                        return HTTPFound(location=previous_location,\
                                         headers = headers)
        request.session.flash('Wrong username or password.')
        return HTTPFound(location=previous_location)
        
def logout(request):
        """Logout view
        """

        request.session.invalidate()
        request.session.flash('Log out.')
        headers = forget(request)
        return HTTPFound(location=request.route_url('home'),\
                         headers=headers)

def admin_article(request):
    """Displays a list of the articles
    in the admin section"""
    
    session = dbSession()
    articleList = session.query(Article).order_by(desc('id'))[0:50]
    session.close()
    renderDictList = []
    for article in articleList:
        renderDictList.append({'id':article.id,
             'name':article.title})
    return{'elementDictList':renderDictList, 'elementType':'article'}

    
def admin_user(request):
    """Displays a list of the users
    in the admin section"""
    
    session = dbSession()
    usersList = session.query(User).order_by(desc('id'))[0:50]
    session.close()
    renderDictList = []
    for user in usersList:
        renderDictList.append({'id':user.id,
             'name':user.name})
    return{'elementDictList':renderDictList, 'elementType':'user',
           'isUser':True}

def admin_project(request):
    """Displays a list of the projects
    in the admin section"""
    
    session = dbSession()
    projectsList = session.query(Project).order_by(desc('id'))[0:50]
    session.close()
    renderDictList = []
    for project in projectsList:
        renderDictList.append({'id':project.id,
             'name':project.title})
    return{'elementDictList':renderDictList, 'elementType':'project'}

def admin_view_user(request):
    """User formular.

    You can change any username or create one with this formular"""

    try:
        userId = request.matchdict['id']
    except:
        raise HTTPBadRequest()
    if userId!='-1':
        session = dbSession()
        try:
            user = session.query(User).\
                filter(User.id == userId).one()
        except:
            session.close()
            raise HTTPBadRequest()
        session.close()
        return{'username': user.name, 'id': userId,
            'group': user.group,
            'submitMessage':'Modify User'}
    else:
        return{'username':'', 'id': '-1',
            'group': '',
            'newUser':True,
            'submitMessage':'Create user'}
    
def admin_add_user(request):
    """Add a new user or modify
    a user already registered in the database

    If the request have an id variable, that means that
    we will do a modification. Otherwise, the user is new."""

    session = dbSession()
    postData = request.POST
    userId = request.matchdict['id']
    if userId != '-1' :
        if 'submit' in postData:
                username = postData['username']
                group = postData['group']
                try:
                        user=session.query(User)\
                        .filter(User.id == userId).one()
                        user.name = username
                        user.group = group
                except:
                        session.close()
                        raise HTTPBadRequest()

        else:
                session.close()
                raise HTTPBadRequest()
    else:
        if 'submit' in postData:
                username = postData['username']
                password = postData['password']
                group = postData['group']
                user = User(username, password, group)
        else:
            session.close()
            raise HTTPBadRequest()
    session.add(user)
    session.commit()
    session.close()
    return HTTPFound(location=request.route_url('admin_user'))

def admin_del_user(request):
    """Delete the user given in request
    matchdict"""

    session = dbSession()
    try:
        userId = request.matchdict['id']
        user = session.query(User).filter(User.id == userId).one()
    except:
        session.close()
        raise HTTPBadRequest
    session.delete(user)
    session.commit()
    session.close()
    return HTTPFound(location=request.route_url('admin_user'))

def admin_view_article(request):
    """This view allow you to modify or create a blog
    article"""

    session = dbSession()
    try:
        articleId = request.matchdict['id']
    except:
        session.close()
        raise HTTPBadRequest
    if articleId != '-1':
        try:
            article = session.query(Article).\
              filter(Article.id == articleId).one()
        except:
            session.close()
            raise HTTPBadRequest
        session.close()
        categoryNameList = []
        for category in article.categories:
            categoryNameList.append(category.name)
        return{'id':articleId, 'title':article.title,
               'date':article.date, 'author':article.author,
               'content':article.content,
               'categories':' ,'.join(categoryNameList),
               'submitMessage':'Modify article'}
    else:
        return{'id':'-1', 'title':'',
               'date':'', 'author':'',
               'content':'',
               'categories':'',
               'submitMessage':'Create article'}

        
def admin_add_article(request):
    """Add a new article or modify
    an article already registered in the database

    If the request have an id variable, that means that
    we will do a modification. Otherwise, the article is new."""

    session = dbSession()
    postData = request.POST
    articleId = request.matchdict['id']
    if 'submit' in postData:
        title = postData['title']
        date = datetime.now()
        categories = postData['categories'].split(', ')
        author = postData['author']
        content = postData['content']
    else:
        session.close()
        raise HTTPBadRequest()
    if articleId != '-1' :
        try:
            article=session.query(Article)\
                .filter(Article.id == articleId).one()
        except:
            session.close()
            raise HTTPBadRequest()
        article.title = title
        article.date = datetime.now()
        article.author = author
        article.content = content
        article.set_categories_by_name(session,categories)
    else:
        article = Article(None, title, date, author, content, categories)
    session.add(article)
    session.commit()
    session.close()
    return HTTPFound(location=request.route_url('admin_article'))


def admin_del_article(request):
    """Delete the article given in request
    matchdict"""

    session = dbSession()
    try:
        articleId = request.matchdict['id']
        article = session.query(Article).\
          filter(Article.id == articleId).one()
    except:
        session.close()
        raise HTTPBadRequest
    session.delete(article)
    session.commit()
    session.close()
    return HTTPFound(location=request.route_url('admin_article'))

def admin_view_project(request):
    """This view allow you to modify or create a project"""

    session = dbSession()
    try:
        projectId = request.matchdict['id']
    except:
        session.close()
        raise HTTPBadRequest
    if projectId != '-1':
        try:
            project = session.query(Project).\
              filter(Project.id == projectId).one()
        except:
            session.close()
            raise HTTPBadRequest
        session.close() 
        return{'id':projectId, 'title':project.title,
               'author':project.author,
               'content':project.getMdFileContent(),
               'submitMessage':'Modify project'}
    else:
        session.close()
        return{'id':'-1', 'title':'',
               'author':'',
               'content':'',
               'submitMessage':'Create project'}


def admin_add_project(request):
    """Add a new project or modify
    a project already registered in the database

    If the request have an id variable, that means that
    we will do a modification. Otherwise, the article is new."""

    session = dbSession()
    postData = request.POST
    projectId = request.matchdict['id']
    if 'submit' in postData:
        title = postData['title']
        date = datetime.now()
        author = postData['author']
        mdContent = postData['content']
    else:
        session.close()
        raise HTTPBadRequest()
    if projectId != '-1' :
        try:
            project=session.query(Project)\
                .filter(Project.id == projectId).one()
        except:
            session.close()
            raise HTTPBadRequest()
        project.title = title
        project.date = datetime.now()
        project.author = author
    else:
        project = Project(title, "", author, date)
    content = project.processMd(mdContent)
    project.content = content
    session.add(project)
    session.commit()
    session.close()
    return HTTPFound(location=request.route_url('admin_project'))


def admin_del_project(request):
    """Delete the project given in request
    matchdict"""

    session = dbSession()
    try:
        projectId = request.matchdict['id']
        project = session.query(Project).\
          filter(Project.id == projectId).one()
    except:
        session.close()
        raise HTTPBadRequest
    session.delete(project)
    session.commit()
    session.close()
    return HTTPFound(location=request.route_url('admin_project'))
