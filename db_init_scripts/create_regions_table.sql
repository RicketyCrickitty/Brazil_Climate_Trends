use catalog brazil_db; -- For use in DBX ONLY
use schema mini_world;

drop table if exists region_types;
drop table if exists regions;

create table region_types (
    region_type string primary key,
    description string,
    region_weaknesses string
);

create table regions (
    region_id int primary key,
    region_name string,
    region_type string,
    constraint fk_region_type
    foreign key (region_type) 
    references region_types(region_type)
);