from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from models import RootFactory
from security import groupFinder

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    session_factory = UnencryptedCookieSessionFactoryConfig('alternativeCookie')
    authn_policy = AuthTktAuthenticationPolicy(
        'Alternativebit', callback=groupFinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings,
                          session_factory = session_factory,
                          root_factory = RootFactory)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('homeValued', '/blog/{page}')
    config.add_route('homeValuedCategorized', '/blog/{page}/{category}')
    config.add_route('home','/')
    config.add_route('article','/article/{articleId}')
    config.add_route('atom','/atom')
    config.add_route('login','/login')
    config.add_route('logout','/logout')
    
    config.add_view('blog.views.blog_list_view', route_name='homeValued',\
                    renderer="blog:templates/blogArticleList.pt",
                    permission='view')
    config.add_view('blog.views.blog_list_view', route_name='home',\
                    renderer="blog:templates/blogArticleList.pt",
                    permission='view')
    config.add_view('blog.views.blog_article_view', route_name="article",\
                    renderer="blog:templates/blogArticle.pt",
                    permission='view')
    config.add_view('blog.views.blog_list_view', \
                    route_name='homeValuedCategorized',\
                    renderer='blog:templates/blogArticleCategoryList.pt',
                    permission='view')
    config.add_view('blog.views.atom', route_name='atom',
                    permission='view')
    config.add_view('blog.views.login', route_name='login')
    config.add_view('blog.views.logout', route_name='logout')
    
    return config.make_wsgi_app()
