# -*- coding: utf-8 -*-
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import (HTTPNotFound,
                                    HTTPInternalServerError,
                                    HTTPFound)
from pyramid.security import remember, forget, authenticated_userid

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from pyatom import AtomFeed

from models import (Article,
                    dbSession,
                    User)

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
                               'date' : article.date.strftime("%d/%m/%y %H:%M"),\
                               'author' : article.author,\
                               'content' : article.content\
                                [:article.content.rfind('</p>',0,200)]+" ...",\
                               'id' : article.id})
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
        raise HTTPNotFound()
    article = session.query(Article).filter(Article.id == articleId).all()
    if len(article) > 1:
        raise HTTPInternalServerError()
    if len(article) == 0:
        raise HTTPNotFound()
    article = article[0]
    renderDict = {'title' : article.title,\
                           'date' : article.date.strftime("%d/%m/%y %H:%M"),\
                           'author' : article.author,\
                           'content' : article.content}
    session.close()
    return {'article' : renderDict}

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
