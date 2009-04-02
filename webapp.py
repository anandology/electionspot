import web

import utils
import db

urls = (
    "/", "home",
    "/party/(.*)", "party",
    "/candidate/(.*)", "candidate",
    "/([A-Za-z-]*)", "state",
    "/([A-Za-z-]*)/([A-Za-z-]*)", "constituency",
)

app = web.application(urls, globals())
app.add_processor(web.loadhook(utils.json_processor))


tglobals = dict(maproot="http://122.170.127.7/KMAP")
render = utils.Render("templates", base="layout", globals=tglobals)

class home:
    def GET(self):
        return render.home({})

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

