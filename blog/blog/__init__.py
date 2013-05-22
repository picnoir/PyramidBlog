from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('homeValued', '/blog/{page}')
    config.add_route('home','/')
    config.add_view('blog.views.blog_list_view', route_name='homeValued',\
                    renderer="blog:templates/blogArticleList.pt")
    config.add_view('blog.views.blog_list_view', route_name='home',\
                    renderer="blog:templates/blogArticleList.pt")
    return config.make_wsgi_app()
