drop table if exists entries;
create table entries (
    id integer primary key autoincrement,
    key text not null,
    definition text not null,
    definer text not null,
    timestamp datetime default current_timestamp not null
);
