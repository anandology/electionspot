"""Parse election data.

Parses the following types of data.

* Election analysis summary from eci.nic.in
* Statistical reports from eci.nic.in

Usage:
    
    python parse.py summary filename
    python parse.py report filename
"""
from BeautifulSoup import BeautifulSoup, Tag
import urllib
import pprint
import simplejson

class storage(dict):
    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError, key

def storify(d):
    if isinstance(d, dict):
        return storage((k, storify(v)) for k, v in d.items())
    elif isinstance(d, list):
        return [storify(v) for v in d]
    else:
        return d

def htmlunquote(text):
    """
    Decodes `text` that's HTML quoted.

        >>> htmlunquote('&lt;&#39;&amp;&quot;&gt;')
        '<\\'&">'

    (from web.py, public domain.)
    """
    text = text.replace("&nbsp;", ' ')
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    text = text.replace("&gt;", ">")
    text = text.replace("&lt;", "<")
    text = text.replace("&amp;", "&") # Must be done last!
    return text

def extract_text(soup):
    return ''.join([htmlunquote(str(e).strip()) for e in soup.recursiveChildGenerator() if isinstance(e,unicode)])

def parse_table(table):
    return [[extract_text(td) for td in tr.findAll("td")] for tr in table.findAll(["tr", "tr ", "tr  "])]

def extract_tables(filename):
    soup = BeautifulSoup(open(filename).read())
    return [parse_table(t) for t in soup.findAll("table")]

def parse_affidavit(filename):
    """Parse affidavit data from myneta.info
    """
    soup = BeautifulSoup(open(filename).read())

    for t in soup.findAll(["h2", "h3", "table"]):
        if t.name in ["h2", "h3"]:
            print "---"
            print "**", extract_text(t)
            print
        elif t.name == "table":
            pprint.pprint(parse_table(t))

def parse_summary(filename):
    """Parse election analysis summary file..

    Sample URL: http://eci.nic.in/electionanalysis/GE/PartyCompWinner/S01/partycomp01.htm
    """
    # The page has 6 tables
    # 0. website header - not required
    # 1. state and constituency name
    # 2. Percentage of Valid Votes Cast in favour of Party in Parliamentary Elections
    # 3. List Of Winning Candidates
    # 4. Legend - not required
    # 5. empty - not required

    def parse_state(table):
        state = table[1][0].title()
    
        name = table[3][0] # N - foo bar Parliamentary Constituency
        tokens = name.split()
        index = int(tokens[0])
        name = " ".join(tokens[2:-2]).title() # skip 'N -' and 'Parliamentary Constituency'

        return state, index, name

    def parse_votes_summary(table):
        header = table[1]
        return [dict(zip(header, r)) for r in table[2:]]

    def parse_winning_candidates(table):
        rows = table[3:] # skip headers
        result = []
        for r in rows:
            year, voters, turnout, name1, votes1, party1, name2, votes2, party2 = r
            d = storage()
            d.year = year
            d.voters = int(float(voters) * 1000)
            d.turnout = turnout + '%'
            d.winner = dict(candidate=name1.title(), party=party1, votes=votes1 + '%')
            d.runnerup = dict(candidate=name2.title(), party=party2, votes=votes2 + '%')
            result.append(d)
        return result

    tables = extract_tables(filename)

    d = storage()
    d.state, d.index, d.name = parse_state(tables[1])
    d.votes_summary = parse_votes_summary(tables[2])
    d.winning_candidates = parse_winning_candidates(tables[3])

    return d

def parse_report(filename):
    """Parse election statistics report.
    """
    # TODO
    return ""

def parse_dbf(filename):
    from dbfpy import dbf
    db = dbf.Dbf(filename)
    heders = db.fieldNames
    rows = [[r[f] for f in db.fieldNames] for r in db]
    return heders, rows

def parse_summary_json(filename):
    """Converts summary json to tabular format."""
    def parse(d):
        for row in d.winning_candidates:
            yield d.name, d.state, row.year, row.voters, row.turnout[:-1], row.winner.candidate, row.winner.party, row.winner.votes[:-1]
            yield d.name, d.state, row.year, row.voters, row.turnout[:-1], row.runnerup.candidate, row.runnerup.party, row.runnerup.votes[:-1]

    d = simplejson.loads(open(filename).read())
    d = storify(d)
    return "\n".join("\t".join(map(str, row)) for row in parse(d))

def main(filetype, filename):
    if filetype == "dbf":
        headers, rows = parse_dbf(filename)
        import pprint
        print headers
        pprint.pprint(dict(zip(headers, rows[1])))
    elif filetype == "summary":
        print simplejson.dumps(parse_election_analysis(filename), indent=4)
    elif filetype == "report":
        print simplejson.dumps(parse_report(filename), indent=4)
    elif filetype == "affidavit":
        print simplejson.dumps(parse_affidavit(filename), indent=4)
    elif filetype == "summary_json":
        print parse_summary_json(filename)
    else:
        print >> sys.stderr, "unknown filetype: %s " % repr(filetype)
        print >> sys.stderr, __doc__

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print >> sys.stderr, __doc__
    else:
        main(sys.argv[1], sys.argv[2])
