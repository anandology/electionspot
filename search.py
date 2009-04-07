import xappy

def search(s):
    conn = xappy.SearchConnection("db")
    q = conn.query_parse(conn.spell_correct(s))
    return [x.data for x in conn.search(q, 0, 10)]

def index():
    """Index entire database."""
    indexer = xappy.IndexerConnection("db")
    indexer.add_field_action("name", xappy.FieldActions.INDEX_FREETEXT, spell=True)
    indexer.add_field_action("id", xappy.FieldActions.INDEX_EXACT)

    def add_to_index(data):
        doc = xappy.UnprocessedDocument()
        doc.id = data.id
        for k, v in data.items():
            doc.fields.append(xappy.Field(k, v))
        doc = indexer.process(doc)
        doc.data = data
        indexer.replace(doc)

    import db
    def add_table(table, id_prefix="", type=""):
        for d in db.getdb().select(table):
            d.id = id_prefix + d.id
            d.type = type
            if table == "constituency":
                d.id = d.state + "/" + d.id
            add_to_index(d)

    add_table("party", "party/", "party")
    add_table("state", type="state")
    add_table("constituency", type="constituency")
    add_table("candidate", "candidate/", type="candidate")

    indexer.flush()
    indexer.close()

if __name__ == "__main__":
    import web
    user = "anand"
    web.config.db_parameters = dict(dbn="postgres", db="electionspot", user=user, pw="")
    import sys
    if len(sys.argv) > 1:
        print list(search(sys.argv[1]))
    else:
        index()
