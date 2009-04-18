import os

user = os.getenv('USER')
db_parameters = dict(dbn="postgres", db="electionspot", user=user, pw="")

search_db = "db"
maproot = "http://maps.electionspot.in/KMAP"

