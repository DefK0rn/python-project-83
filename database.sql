create table if not exists urls(
    id serial primary key,
    "name" varchar(255) not null unique,
    created_at timestamp default current_timestamp
);

create table if not exists url_checks(
    id serial primary key,
    url_id integer not null,
    status_code varchar(3) null,
    h1 varchar(255) null,
    title varchar(255) null,
    "description" varchar(255) null,
    created_at timestamp default current_timestamp,
    FOREIGN KEY (url_id) REFERENCES urls(id) ON DELETE CASCADE
);