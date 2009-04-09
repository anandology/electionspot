#! /usr/bin/env python
import web
import pygooglechart
import urllib

import utils
import db
import search

urls = (
    "/", "home",
    "/search", "do_search",
    "(/.*)/", "redirect",
    "/party", "parties",
    "/party/(.*)", "party",
    "/candidate/(.*)", "candidate",
    "/([A-Za-z-]*)", "state",
    "/([A-Za-z-]*)/([A-Za-z-_]*)", "constituency",
)

app = web.application(urls, globals())
app.add_processor(web.loadhook(utils.json_processor))

tglobals = {
    "maproot": "http://122.170.127.7/KMAP",
    "sorted": sorted,
    "str": str,
    "changequery": web.changequery,
    "GroupedVerticalBarChart": pygooglechart.GroupedVerticalBarChart,
    "PieChart": pygooglechart.PieChart2D,
}
# render = utils.Render("templates", base="layout", globals=tglobals)
render = utils.Render("templates", base="es_layout", globals=tglobals)
app.notfound = lambda: web.notfound(render.notfound(""))

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

class candidate:
    def GET(self, name):
        d = db.get_candidate(name)
        if d is None:
            raise web.seeother('/search?' + urllib.urlencode(dict(q=name.replace('_', ' '))))
        return render.candidate(d)
        

class state:
    def GET(self, name):
        d = db.get_state(name)
        print >> web.debug, d
        return render.state(d)

class constituency:
    def GET(self, state, name):
        d = db.get_constituency(state, name)
        return render.constituency(d)

class do_search:
    def GET(self):
        i = web.input(q="", page=1)
        page = int(i.page)
        nmatched, results = search.search(i.q, page=page-1)
        if len(results) == 1 and page == 1:
            raise web.seeother(results[0].id)
        else:
            return render.search(results, nmatched, page)

if __name__ == "__main__":
    app.run()
