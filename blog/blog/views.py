from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPInternalServerError

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Article

def blog_list_view(request):
    """Homepage view.
    Displays recent blog post list"""

    engine = create_engine('sqlite:///:blog:')
    Session = sessionmaker(bind=engine)
    session = Session()
    articlesByPage = 5
    renderDictList = []
    nbArticles = session.query(Article).count()
    try:
        page = request.matchdict['page']
    except KeyError:
        page=0
    if (page > nbArticles/articlesByPage):
        page=0
    query = session.query(Article).order_by('id')\
         [page : (page + articlesByPage)]
    for article in query:
        renderDictList.append({'title' : article.title,\
                               'date' : article.date.strftime("%d/%m/%y %H:%M"),\
                               'author' : article.author,\
                               'content' : article.content})
    return {'renderDictList' : renderDictList}

def blog_article_view(request):
    """Display a blog article.
    """
    engine = create_engine('sqlite:///:blog:')
    Session = sessionmaker(bind=engine)
    session = Session()
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
    return {'article' : renderDict}

        
    
