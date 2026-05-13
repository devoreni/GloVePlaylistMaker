drop table if exists tracks;
drop table if exists schema_version;

create table if not exists schema_version (
    version integer primary key,
    description text
    );

create table if not exists tracks (
    id integer primary key,
    title text,
    artist text,
    album text,
    gmm blob not null,
    path text not null
);

insert into schema_version (version, description)
values (3, 'initial schema');
