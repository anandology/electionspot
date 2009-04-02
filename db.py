
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

def get_party(id):
    def parse(d):
        x = d[0].party
        x.election_history = [r.pop('party') and r for r in d]
        return x

    d = get_election_history(party_id=id)
    return d and parse(d)

def get_candidate(id):
    def parse(d):
        x = d[0].candidate
        x.election_history = [r.pop('candidate') and r for r in d]
        return x

    d = get_election_history(candidate_id=id)
    return d and parse(d)

def get_state(id):
    id = id.upper()
    try:
        return query("SELECT * FROM state WHERE id=$id", vars=locals())[0]
    except IndexError:
        return None
        
def pop_many(row, *keys):
    for k in keys:
        row.pop(k)
    return row

def get_constituency(state, id):
    def parse(d):
        constituency = d[0].constituency
        constituency.election_history = []
        
        for year, data in itertools.groupby(d, lambda row: row.year):
            data = list(data)
            h = storage(
                year=year,
                numvoters=data[0].numvoters,
                turnout=data[0].turnout,
                candidates=[pop_many(r, "constituency") for r in data]
            )
            constituency.election_history.append(h)
        return constituency
        
    d = get_election_history(constituency_id=id)
    return d and parse(d)
    
def xget_election_history(constituency_id):
    def parse_candidate(d):
        out = storage()
        out.id = d.candidate_id
        out.party = storage(id="party/" + d.party_id, name=d.party_id)
        out.percentage_votes = d.percentage_votes_polled
        return out
    
    result = query("SELECT * FROM election "
        + " JOIN constituency ON election.constituency_id=constituency.id"
        + " JOIN party ON election.party_id=party.id"
        + " WHERE constituency_id=$constituency_id ORDER BY year desc, percentage_votes_polled desc",     
        vars=locals())
        
    for year, data in itertools.groupby(result, lambda row: row.year):
        data = list(data)
        print data
        x = storage()
        x.year = year
        x.numvoters = data[0].total_votes
        x.candidates = [parse_candidate(d) for d in data]
        yield x

def get_election_history(constituency_id=None, party_id=None, candidate_id=None, state_id=None):
    args = dict((k, v) for k, v in locals().items() if v)
    wheres = [web.reparam("%s = $v" % k, {'v': v}) for k, v in args.items()]
    
    result = query("SELECT election.* " 
        + " , c.id as c_id, c.name as c_name, c.state as state_id"
        + " , s.id as s_id, s.name as s_name"
        + " , p.name AS p_name, p.id as p_id, p.shortname as p_shortname "
        + " , m.id as m_id, m.name as m_name"
        + " FROM election "
        + " JOIN constituency AS c ON election.constituency_id=c.id"
        + " JOIN state AS s ON c.state=s.id"
        + " JOIN party AS p ON election.party_id=p.id"
        + " JOIN candidate AS m ON election.candidate_id=m.id"
        + " WHERE " + web.SQLQuery.join(wheres, "AND")
        + " ORDER BY year desc, percentage_votes_polled desc")
        
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
            )
        )
    
    d = [parse_row(row) for row in result]
    return d or None
