import web
import simplejson
import re

import config

def json_processor(handler):
    if web.ctx.path.endswith('.json'):
        web.ctx.path = web.ctx.path[:-len(".json")]
        web.ctx.method = "GET_json"
        web.header('Content-Type', 'application/json')
        d = handler()
        return simplejson.dumps(d)
    else:
        return handler()

cache = {}        

re_accepts_gzip = re.compile(r'\bgzip\b')

def cache_processor(handler):
    """cache and gzip processor. 
    Inspired by django.middleware.gzip.GZipMiddleware
    """
    ae = web.ctx.env.get('HTTP_ACCEPT_ENCODING', '')
    if config.cache and web.ctx.method in ["GET", "GET_json"] and re_accepts_gzip.search(ae):
        if web.ctx.path not in cache:
            data = handler()
            cache[web.ctx.fullpath] = compress(web.safestr(data))
        web.expires(3600) # one hour
        web.header('Content-Encoding', 'gzip')
        return cache[web.ctx.fullpath]
    else:
        return handler()

def compress(data):
    from cStringIO import StringIO
    import gzip
    f = StringIO()
    gz = gzip.GzipFile(fileobj=f, mode='wb')
    gz.write(data)
    gz.flush()
    return f.getvalue()
