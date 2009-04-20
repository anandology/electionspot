import web
import itertools

import config

db = None

def getdb():
    global db
    if db is None:
        db = web.database(**config.db_parameters)
    return db

class storage(web.storage):
	def __getattr__(self, key):
		try:
			return web.storage.__getattr__(self, key)
		except AttributeError:
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
        
def list_parties():
    result = getdb().query("SELECT * FROM party ORDER BY shortname").list()
    for row in result:
        row.id = "party/" + row.id
    return result

def list_states():
    result = getdb().query("SELECT * FROM state ORDER BY union_teritory, name").list()
    for row in result:
        row.id = row.id.lower()
    return result

def list_constituencies(state_id):
    result = getdb().query("SELECT * FROM constituency WHERE state=$state_id ORDER BY name", vars=locals()).list()
    for row in result:
        row.id = state_id.lower() + "/" + row.id
    return result

def get_party(id):
    def parse(d):
        x = d[0].party
        x.election_history = [r.pop('party') and r for r in d]

        years = {}
        for e in x.election_history:
            y = years.setdefault(e.year, storage(year=e.year, contested=0, won=0))
            y.contested += 1
            if e.won:
                y.won += 1
        x.performance = sorted(years.values(), key=lambda p: p.year, reverse=True)
        return x

    d = get_election_history(party_id=id)
    return d and parse(d)
    
def groupby(data, keys, params):
    keyfunc = lambda d: [d[k] for k in keys]
    data = sorted(data, key=keyfunc)
    for xkeys, values in itertools.groupby(data, keyfunc):
        d = storage(zip(keys, xkeys))
        values = list(values)
        for p in params:
            d[p] = params[p](values)
        yield d

def get_candidate(id):
    def parse(d):
        x = d[0].candidate
        x.election_history = [r.pop('candidate') and r for r in d]
        return x

    d = get_election_history(candidate_id=id)
    return d and parse(d)

def get_state(id):
    def group(data):
        data = groupby(data, ["year", "party"], dict(contested=lambda values: len(values), won=lambda values: len([x for x in values if x.won])))
        result = {}
        for k, v in itertools.groupby(data, lambda d: d.year):
            result[k] = list(v)
        return result
            
    def parse(d):
        x = d[0].constituency.state
        #x.election_history = d
        x.performance = group(d)
        return x

    d = get_election_history(state_id=id.upper())
    return d and parse(d)
        
def get_constituency(state, id):
    def parse_candidate(d):
        candidate = d.pop('candidate')
        d.pop('constituency')
        candidate.update(d)
        return candidate
        
    def parse(d):
        constituency = d[0].constituency
        constituency.election_history = []
        
        for year, data in itertools.groupby(d, lambda row: row.year):
            data = list(data)
            h = storage(
                year=year,
                numvoters=data[0].numvoters,
                turnout=data[0].turnout,
                candidates=[parse_candidate(r) for r in data]
            )
            constituency.election_history.append(h)
        return constituency
        
    d = get_election_history(constituency_id=id)
    return d and parse(d)

def get_election_history(constituency_id=None, party_id=None, candidate_id=None, state_id=None):
    wheres = []
    if constituency_id: 
        wheres.append('constituency_id = $constituency_id')
    if party_id:
        wheres.append('party_id = $party_id')
    if candidate_id:
        wheres.append('candidate_id = $candidate_id')
    if state_id:
        wheres.append('c.state = $state_id')
    wheres = " AND ".join(wheres)
    
    result = query("SELECT election.*" 
        + " , c.id as c_id, c.name as c_name, c.state as state_id"
        + " , s.id as s_id, s.name as s_name"
        + " , p.name AS p_name, p.id as p_id, p.shortname as p_shortname"
        + " , m.id as m_id, m.name as m_name"
        + " FROM election "
        + " JOIN constituency AS c ON election.constituency_id=c.id"
        + " JOIN state AS s ON c.state=s.id"
        + " JOIN party AS p ON election.party_id=p.id"
        + " JOIN candidate AS m ON election.candidate_id=m.id"
        + " WHERE " + wheres
        + " ORDER BY year desc, percentage_votes_polled desc",
        vars=locals())
        
    def parse_row(row):
        return storage(
            year=row.year,
            numvoters=row.total_votes,
            turnout=row.turnout,
            percentage_votes_polled=row.percentage_votes_polled,
            constituency = storage(
                id= row.s_id + "/" + row.c_id, 
                name=row.c_name,
                state=storage(
                    id=row.s_id,
                    name=row.s_name
                )
            ),
            candidate= storage(
                id="candidate/" + row.m_id,
                name=row.m_name
            ),
            party=storage(
                id="party/" + row.p_id,
                shortname=row.p_shortname,
                name=row.p_name
            ),
            won=row.won,
        )
    
    d = [parse_row(row) for row in result]
    return d or None
