drop table if exists tracks;

create table if not exists tracks (
    id integer primary key,
    title text,
    artist text,
    album text,
    n_components integer not null,
    gmm_means blob not null,
    gmm_covs blob not null,
    gmm_weights blob not null
);

insert into schema_version (version, description)
values (2, 'refactored tracks table');