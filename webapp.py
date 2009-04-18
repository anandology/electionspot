#! /usr/bin/env python
import web
import pygooglechart
import urllib

import utils
import db
import search
import config

urls = (
    "/", "home",
    "/about", "about",
    "/search", "do_search",
    "(/.*)/", "redirect",
    "/party", "parties",
    "/party/(.*)", "party",
    "/candidate/(.*)", "candidate",
    "/([A-Za-z-]*)", "state",
    "/([A-Za-z-]*)/([A-Za-z-_]*)", "constituency",
)

app = web.application(urls, globals())

tglobals = {
    "maproot": config.maproot,
    "sorted": sorted,
    "str": str,
    "changequery": web.changequery,
    "GroupedVerticalBarChart": pygooglechart.GroupedVerticalBarChart,
    "PieChart": pygooglechart.PieChart2D,
}
render = web.template.render("templates", base="layout", globals=tglobals)
app.notfound = lambda: web.notfound(render.notfound(""))
app.add_processor(utils.json_processor)
app.add_processor(utils.cache_processor)

class redirect:
    def GET(self, path):
        raise web.seeother(path)

class home:
    def GET(self):
        return render.home({})

class parties:
    def GET(self):
        return render.list("Parties", db.list_parties())

class party:
    def GET(self, name):
        d = db.get_party(name)
        return render.party(d)

    def GET_json(self, name):
        return db.get_party(name)

class candidate:
    def GET(self, name):
        d = db.get_candidate(name)
        if d is None:
            raise web.seeother('/search?' + urllib.urlencode(dict(q=name.replace('_', ' '))))
        return render.candidate(d)

    def GET_json(self, name):
        d = db.get_candidate(name)
        if d is None:
            raise web.notfound()
        return d

class state:
    def GET(self, name):
        d = db.get_state(name)
        return render.state(d)

class constituency:
    def GET(self, state, name):
        d = db.get_constituency(state, name)
        return render.constituency(d)

    def GET_json(self, state, name):
        d = db.get_constituency(state, name)

class do_search:
    def GET(self):
        i = web.input(q="", page=1)
        page = int(i.page)
        nmatched, results = search.search(i.q, page=page-1)
        if len(results) == 1 and page == 1:
            raise web.seeother(results[0].id)
        else:
            return render.search(results, nmatched, page)

class about:
    def GET(self):
        return render.about({})

if __name__ == "__main__":
    app.run()
