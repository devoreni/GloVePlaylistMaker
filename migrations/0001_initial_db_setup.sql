create table if not exists schema_version (
    version integer primary key,
    description text
    );

insert into schema_version (version, description)
values (1, 'initial schema');

create table if not exists tracks (
    id integer primary key,
    title text,
    artist text,
    album text,
    embedding blob not NULL
    );