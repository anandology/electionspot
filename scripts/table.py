import sys

def xopen(filename, *a, **kw):
    if isinstance(filename, str):
        return open(filename, *a, **kw)
    else:
        return filename
    
def read_tsv(filename, delim="\t"):
    return [line.strip().split(delim) for line in xopen(filename)]
    
def write_tsv(filename, data):
    f = xopen(filename, 'w')
    f.writelines("\t".join(row) + "\n" for row in data)
    f.close()
    
def normalize(name):
    return name.replace('&', 'and').replace('   ', ' ').replace('  ', ' ').replace(' ', '_').lower()

def process(election_file, states_file):
    states = dict((name, id) for id, name, _ in read_tsv(states_file))
    
    restates = {
        "National Capital Territory Of Delhi": "Delhi",
        "Andaman & Nicobar Islands": "Andaman & Nicobar",
        "Pondicherry": "Puducherry",
    }
    constituencies = {}
    candidates = {}
    parties = {}
    rows = []
    
    for constituency, state, year, votes, turnout, candidate, party, percentage_votes, won in read_tsv(election_file):
        state = restates.get(state, state)
        state_id = states[state]
        
        constituency_id = normalize(constituency)
        constituencies[constituency_id] = [constituency_id, constituency, state_id]
        
        candidate_id = normalize(candidate)
        candidates[candidate_id] = [candidate_id, candidate]
        
        row = year, constituency_id, votes, turnout, candidate_id, party, percentage_votes, won
        rows.append(row)
        
    return constituencies.values(), candidates.values(), rows
    
def main(election_file, states_file):
    constituencies, candidates, data = process(election_file, states_file)
    
    write_tsv("data/constituency.txt", constituencies)
    write_tsv("data/candidate.txt", candidates)
    write_tsv("data/election.txt", data)

if __name__ == '__main__':
    main("election.txt", "data/state.txt")
