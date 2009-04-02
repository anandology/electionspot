
import web
import itertools

db = None

def getdb():
    global db
    if db is None:
        db = web.database(**web.config.db_parameters)
    return db

class storage(web.storage):
	def __getattr__(self, key):
		try:
			return web.storage.__getattr__(self, key)
		except KeyError:
			if key.startswith("_"):
				raise
			else:
				return None
    
def query(*a, **kw):
    return getdb().query(*a, **kw)

def storify(d):
    if isinstance(d, list):
        return [storify(x) for x in d]
    elif isinstance(d, dict):
        return storage((k, storify(v)) for k, v in d.items())
    else:
        return d

def get_party(id):
    id = id.upper()
    try:
        return query("SELECT * FROM party WHERE id=$id", vars=locals())[0]
    except IndexError:
        return None

def get_candidate(name):
    return web.storage(id=name, name=name)

def get_state(id):
    id = id.upper()
    try:
        return query("SELECT * FROM state WHERE id=$id", vars=locals())[0]
    except IndexError:
        return None

def get_constituency(state, id):
    try:
        constituency = query("SELECT * FROM constituency where id=$id", vars=locals())[0]
    except IndexError:
        return None
        
    d = storage()
    d.id = id
    d.name = constituency.name
    d.state = get_state(constituency.state)
    d.election_history = list(get_election_history(id))
    d.stats = None
    d.upcoming_elections = None
    return d
    
def get_election_history(constituency_id):
    def parse_candidate(d):
        out = storage()
        out.id = d.candidate_id
        out.party = storage(id="party/" + d.party_id, name=d.party_id)
        out.percentage_votes = d.percentage_votes_polled
        return out
    
    result = query("SELECT * FROM election where constituency_id=$constituency_id ORDER BY year desc, percentage_votes_polled desc", vars=locals())

    for year, data in itertools.groupby(result, lambda row: row.year):
        data = list(data)
        x = storage()
        x.year = year
        x.numvoters = data[0].total_votes
        x.candidates = [parse_candidate(d) for d in data]
        yield x
