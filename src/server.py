#!/usr/bin/env python
# encoding: utf-8
"""
server.py

Created by Sergey Safonov on 2013-02-20.
Copyright (c) 2013. All rights reserved.
"""
import os
import time
import logging
import datetime

import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.options import define, options
from tornado.locale import load_translations, set_default_locale

from jinja2 import Environment, FileSystemLoader

PROJECT_DIR = os.path.dirname(__file__)

PAGES = [
    {'title': 'Home', 'url': '/', 'name': 'main'},
    {'title': 'Projects', 'url': '/', 'name': 'projects'},
    {'title': 'Services', 'url': '/', 'name': 'services'},
    {'title': 'Downloads', 'url': '/', 'name': 'downloads'},
    {'title': 'About', 'url': '/', 'name': 'about'},
    {'title': 'Contact', 'url': '/', 'name': 'contact'},
]

PAGES_DICT = dict((p['name'], p) for p in PAGES)


def _generate_news(num=100):
    news = []
    for i in range(num):
        news_body = {
            'date': datetime.datetime.now(),
            'title': 'News title %s' % i,
            'body': ('Donec id elit non mi porta gravida at eget metus. '
                     'Fusce dapibus, tellus ac cursus commodo, tortor mauris '
                     'condimentum nibh, ut fermentum massa justo sit amet '
                     'risus. Etiam porta sem malesuada magna mollis euismod. '
                     'Donec sed odio dui.'),
        }
        news.append(news_body)
    return news

NEWS = _generate_news()


def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def datetimeformat(value, format='%H:%M / %d-%m-%Y'):
    return value.strftime(format)


class BaseHandler(tornado.web.RequestHandler):
    def get(self):
        """This GET method is equal for both handlers"""
        context = {
            'links': PAGES,
            'news': NEWS,
        }

        page = self.get_argument('page', 'main')
        if page not in PAGES_DICT:
            page = 'main'

        if page != 'main':
            context['news'] = []

        context['active'] = page
        page = PAGES_DICT[page]
        context['title'] = page['title']

        self.render("index.html", **context)


class TornadoHandler(BaseHandler):
    """Handler that uses tornado template engine"""

    def get_template_path(self):
        template_path = super(BaseHandler, self).get_template_path()
        return os.path.join(template_path, 'tornado')

    def render_string(self, template_name, **kwargs):
        kwargs['chunks'] = chunks
        kwargs['datetimeformat'] = datetimeformat
        t1 = time.time()
        output = super(TornadoHandler, self).render_string(template_name,
                                                           **kwargs)
        t2 = time.time() - t1
        logging.info('render time: %.10f', t2)
        self.application.full_response_times.append(t2)
        return output


class JinjaHandler(BaseHandler):
    """Handler that uses Jinja2 as template engine"""

    def render_string(self, template_name, **kwargs):
        t1 = time.time()
        env = self.application.env
        template = env.get_template(template_name)
        t2 = time.time()

        output = template.render(**kwargs)
        t3 = time.time()
        full_render_time = t3 - t1
        render_time = t2 - t1
        logging.info('render time: %.10f', full_render_time)

        self.application.full_response_times.append(full_render_time)
        self.application.response_times.append(render_time)

        return output


class StatusHandler(BaseHandler):
    """Status page handler"""

    def _calc_avg(self, times):
        if times:
            avg_time = 1000.0 * float(sum(times)) / len(times)
        else:
            avg_time = 0.0
        return avg_time

    def get(self):
        avg_time = self._calc_avg(self.application.response_times)
        full_avg_time = self._calc_avg(self.application.full_response_times)
        self.write('Render time (avg): %.4f ms<br>'
                    'Full render time (avg): %.4f ms' % (avg_time,
                                                         full_avg_time))


class ClearHandler(BaseHandler):
    """Handler that resets all status messages"""

    def get(self):
        self.application.response_times = []
        self.application.full_response_times = []
        self.write('OK')


class Application(tornado.web.Application):
    def __init__(self):
        self.response_times = []
        self.full_response_times = []

        static_path = os.path.abspath(os.path.join(PROJECT_DIR, '../static/'))
        app_handlers = [
            (r"/tornado/", TornadoHandler),
            (r"/jinja/", JinjaHandler),
            (r"/status/", StatusHandler),
            (r"/clear/", ClearHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler,
                {'path': static_path})
        ]

        template_path = os.path.abspath(os.path.join(PROJECT_DIR,
                                                     '../templates/'))
        autoescape = bool(options['autoescape'].value())
        config = {
            'template_path': template_path,
            'debug': bool(options['debug'].value()),
        }
        if not autoescape:
            config['autoescape'] = None

        # create jinja evironment here to make its own cache works
        template_path = os.path.join(template_path, 'jinja')
        self.env = Environment(loader=FileSystemLoader(template_path),
                               auto_reload=config['debug'],
                               autoescape=autoescape,
                               extensions=['jinja2.ext.autoescape'])
        self.env.filters['chunks'] = chunks
        self.env.filters['datetimeformat'] = datetimeformat

        super(Application, self).__init__(app_handlers, **config)


if __name__ == "__main__":
    define("debug", default=0, help="run debug mode", type=int)
    define("autoescape", default=0, help="enable autoescape", type=int)
    define("port", default=8888, help="run on the given port", type=int)

    tornado.options.parse_command_line()
    translations = os.path.join(PROJECT_DIR, "../translations")
    load_translations(translations)
    set_default_locale("ru_RU")

    logging.info("start server on port %s" % options.port)
    application = tornado.httpserver.HTTPServer(Application())
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
