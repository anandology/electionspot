
import web

def storify(d):
    if isinstance(d, list):
        return [storify(x) for x in d]
    elif isinstance(d, dict):
        return web.storage((k, storify(v)) for k, v in d.items())
    else:
        return d

def get_party(name):
    return web.storage()

def get_candidate(name):
    return web.storage()

def get_state(name):
    return web.storage()

def get_constituency(state, name):
    return storify({
        "id": "%s/%s" % (state, name),
        "name": name
    });
