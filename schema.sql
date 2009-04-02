
create table state (
    id char(2) primary key,
    name text,
    union_teritory boolean
);

create table constituency (
    id text primary key,
    name text,
    state char(2) references state
);

create table candidate (
    id text primary key,
    name text
);

create table party (
    id text primary key,
    shortname text,
    name text
);

create table election (
    year char(4),
    
    constituency_id text references constituency,
    total_votes int,
    turnout real,
    
    candidate_id text references candidate,
    party_id text references party,
    percentage_votes_polled real,
    won boolean default 'f',
    
    UNIQUE (year, constituency_id, candidate_id)
);


