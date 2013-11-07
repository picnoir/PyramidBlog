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
    
    add_generals_routes(config)
    add_admin_routes(config)
    
    return config.make_wsgi_app()


def add_generals_routes(config):
        """Add generals views (all the views except
        the administration related ones) to the
        configuration config"""

        config.add_static_view('static', 'static', cache_max_age=3600)
        config.add_route('homeValued', '/blog/{page}')
        config.add_route('homeValuedCategorized', '/blog/{page}/{category}')
        config.add_route('home','/')
        config.add_route('article','/article/{articleId}')
        config.add_route('projectList','/project')
        config.add_route('project','/project/{projectId}')
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
        config.add_view('blog.views.project_view',\
                        route_name='projectList',\
                        renderer='blog:templates/project.pt',\
                        permission='view')
        config.add_view('blog.views.project_view',\
                        route_name='project',\
                        renderer='blog:templates/project.pt',\
                        permission='view')               
        config.add_view('blog.views.atom', route_name='atom',
                        permission='view')
        config.add_view('blog.views.login', route_name='login')
        config.add_view('blog.views.logout', route_name='logout')

def add_admin_routes(config):
    """Add admin related views to the
    configuration config"""

    config.add_route('admin_article','/admin/article')
    config.add_route('admin_home','/admin')
    config.add_route('admin_user','/admin/user')
    config.add_route('admin_project','/admin/project')
    config.add_route('admin_view_user','/admin/user/{id}')
    config.add_route('admin_add_user','/admin/user/add/{id}')
    config.add_route('admin_del_user','/admin/user/del/{id}')
    config.add_route('admin_view_article','/admin/article/{id}')
    config.add_route('admin_add_article','/admin/article/add/{id}')
    config.add_route('admin_del_article','/admin/article/del/{id}')
    config.add_route('admin_view_project','/admin/project/{id}')
    config.add_route('admin_add_project','/admin/project/add/{id}')
    config.add_route('admin_del_project','/admin/project/del/{id}')

    config.add_view('blog.views.admin_article',
                    route_name='admin_article',
                    renderer='blog:templates/admin_list.pt',
                    permission='admin')
    config.add_view('blog.views.admin_article',
                    route_name='admin_home',
                    renderer='blog:templates/admin_list.pt',
                    permission='admin')
    config.add_view('blog.views.admin_user',
                    route_name='admin_user',
                    renderer='blog:templates/admin_list.pt',
                    permission='admin')
    config.add_view('blog.views.admin_project',
                    route_name='admin_project',
                    renderer='blog:templates/admin_list.pt',
                    permission='admin')
    config.add_view('blog.views.admin_view_user',
                    route_name='admin_view_user',
                    renderer='blog:templates/admin_user.pt',
                    permission='admin')
    config.add_view('blog.views.admin_add_user',
                    route_name='admin_add_user',
                    permission='admin')
    config.add_view('blog.views.admin_del_user',
                    route_name='admin_del_user',
                    permission='admin')
    config.add_view('blog.views.admin_view_article',
                    route_name='admin_view_article',
                    renderer='blog:templates/admin_article.pt',
                    permission='admin')
    config.add_view('blog.views.admin_add_article',
                    route_name='admin_add_article',
                    permission='admin')
    config.add_view('blog.views.admin_del_article',
                    route_name='admin_del_article',
                    permission='admin')
    config.add_view('blog.views.admin_view_project',
                    route_name='admin_view_project',
                    renderer='blog:templates/admin_project.pt',
                    permission='admin')
    config.add_view('blog.views.admin_add_project',
                    route_name='admin_add_project',
                    permission='admin')
    config.add_view('blog.views.admin_del_project',
                    route_name='admin_del_project',
                    permission='admin')
