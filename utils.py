import web
import simplejson

def json_processor(handler):
    if web.ctx.path.endswith('.json'):
        web.ctx.path = web.ctx.path[:-len(".json")]
        web.ctx.method = "GET_json"
        web.header('Content-Type', 'application/json')
        d = handler()
        return simplejson.dumps(d)
    else:
        return handler()
        
