create database weather_database;
use weather_database;

-- Create Tables for store records
create table cities (
	city_id int primary key,
    city_name varchar(50),
    country varchar(5),
    latitude decimal(8,5),
    longitude decimal(8,5)
);

create table weather_conditions (
	condition_id int auto_increment primary key,
    main varchar(50),
    description varchar(100),
    icon varchar(10)
);

create table weather_records (
	record_id int auto_increment primary key,
    city_id int,
    condition_id int,
    temerature float,
    feels_like float,
    temp_min float,
    temp_max float,
    pressure int,
    humidity int,
    visibility int,
    recorded_at datetime,
    foreign key (city_id) references cities(city_id),
    foreign key (condition_id) references weather_conditions(condition_id)
);

alter table weather_records
rename column temerature to temperature;

create table wind_data(
	wind_id int auto_increment primary key,
    record_id int,
    wind_speed float,
    wind_deg int,
    foreign key (record_id) references weather_records (record_id)
);

show tables;