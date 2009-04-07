import xappy
import config

def search(s, page=0):
    conn = xappy.SearchConnection(config.search_db)
    q = conn.query_parse(conn.spell_correct(s))
    result = conn.search(q, page*20, page*20+20)
    return result.matches_estimated, [x.data for x in result]

def index():
    """Index entire database."""
    indexer = xappy.IndexerConnection(config.search_db)
    indexer.add_field_action("name", xappy.FieldActions.INDEX_FREETEXT, spell=True)
    indexer.add_field_action("id", xappy.FieldActions.INDEX_EXACT)
    indexer.add_field_action("type", xappy.FieldActions.INDEX_EXACT)

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
    import sys
    if len(sys.argv) > 1:
        print sorted(d.name for d in search(sys.argv[1]))
    else:
        index()
