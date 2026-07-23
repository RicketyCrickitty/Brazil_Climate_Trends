use catalog brazil_db; -- For use in DBX ONLY
use schema mini_world;

drop table if exists region_types;
drop table if exists regions;
drop table if exists region_managers;
drop table if exists land_use_types;
drop table if exists land_usage;
drop table if exists climate_markers;

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

create table region_managers (
    region_id int primary key,
    m_first_name string,
    m_last_name string,
    constraint fk_region_id_rm
    foreign key (region_id) 
    references regions(region_id)
);


create table land_use_types (
    land_use_type string primary key,
    description string
);

create table land_usage (
    region_id int,
    year int,
    land_use_type string,
    percent double,
    primary key (region_id, year),
    constraint fk_region_id_lu
    foreign key (region_id) 
    references regions(region_id),
    constraint fk_land_use_type
    foreign key (land_use_type)
    references land_use_types(land_use_type)
);

create table climate_markers (
    region_id int,
    year int,
    co2_emission float,
    deforestation float, 
    primary key (region_id, year),
    constraint fk_region_id_cm
    foreign key (region_id) 
    references regions(region_id)
);
