import web

import utils
import db
import pygooglechart

urls = (
    "/", "home",
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
    "GroupedVerticalBarChart": pygooglechart.GroupedVerticalBarChart,
    "PieChart": pygooglechart.PieChart2D,
}
render = utils.Render("templates", base="layout", globals=tglobals)

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
        return render.candidate(d)

class state:
    def GET(self, name):
        d = db.get_state(name)
        return render.state(d)

class constituency:
    def GET(self, state, name):
        d = db.get_constituency(state, name)
        return render.constituency(d)

if __name__ == "__main__":
    import os
    user = os.getenv('USER')
    web.config.db_parameters = dict(dbn="postgres", db="electionspot", user=user, pw="")
    app.run()

