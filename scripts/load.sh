#! /bin/bash

db=electionspot
dropdb $db
createdb $db
psql $db < schema.sql

for t in state candidate constituency party election
do
    cat data/$t.txt | psql $db -c "copy $t from stdin"
done

rm -rf db
python search.py
