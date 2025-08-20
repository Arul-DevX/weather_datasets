create database weather_database;
use weather_database;

-- Create Tables for store records into the data base
-- cities
create table cities (
	city_id int primary key,
    city_name varchar(50),
    country varchar(5),
    latitude decimal(8,5),
    longitude decimal(8,5)
);
-- weather conditions
create table weather_conditions (
	condition_id int auto_increment primary key,
    main varchar(50),
    description varchar(100),
    icon varchar(10)
);
-- main weather records
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
-- wind records
create table wind_data(
	wind_id int auto_increment primary key,
    record_id int,
    wind_speed float,
    wind_deg int,
    foreign key (record_id) references weather_records (record_id)
);

show tables;
select * from weather_records;
-- 1.	City Weather Insights
	-- i.	Count monitored cities:
	select city_name,count(distinct city_id) from weather_records
	join cities
	using (city_id)
	group by city_name;
    
    -- ii.	Highest and lowest temperatures:
		-- a. Highest temperatures and Lowest temperatures
        drop view if exists tempearture_min_max_data;
        create view tempearture_min_max_data as( 
        with 
			cte_1 as (select temp_max,temp_min from weather_records),
            cte_2 as (select round(max(temp_max),2) as max_temp from cte_1),
            cte_3 as (select round(min(temp_min),2) as min_temp from cte_1)
            select c2.max_temp,c3.min_temp from cte_2 c2,cte_3 c3
        );
        select * from tempearture_min_max_data ;
        
	-- iii.	Averages across all cities:
        select wc.main,
        count(*) condition_count, 
		round((count(*)*100/(select count(*) from weather_records))) as percentage,
        AVG(temperature) as avg_temperature, 
        AVG(feels_like) as avg_feel_like,
        AVG(pressure) as avg_pressure,
        AVG(humidity) as avg_humidity,
        AVG(visibility) as avg_availability
        from weather_records as wr
        join weather_conditions wc
        on wr.condition_id = wc.condition_id
        group by wc.main
        order by wc.main;
        
-- 2.	Weather Condition Trends
	with 
		cte_1 as (
			select 
			c.country,
			wc.main ,
			count(*) as condition_count
			from cities c
			join weather_records wr
			on c.city_id = wr.city_id
			join weather_conditions wc
			on wr.condition_id = wc.condition_id
			group by c.country,wc.main
			),
		cte_2 as (
			select 
			country,
			main,condition_count,
			row_number() over (partition by country order by condition_count desc) as rn
			from cte_1
		)
		select 
		country,
		main as most_common_condition,
		condition_count
		from cte_2
		where rn = 1
		order by country;
-- 3.	Temperature & Humidity Analysis

	select 
	(
	sum(temperature*humidity)-(sum(temperature)*sum(humidity)/count(*))
	) / 
	sqrt(
	(sum(power(temperature,2))-power(sum(temperature),2)/count(*))
	*
	(sum(power(humidity,2))-power(sum(humidity),2)/count(*))
	)
	as correlation_coefficient from weather_records;
-------------------------------------------------------------------------------------

	WITH city_condition_counts AS (
    SELECT 
        c.city_id,
        c.city_name,
        c.country,
        wc.main,
        COUNT(*) AS condition_count
    FROM weather_records wr
    JOIN weather_conditions wc 
        ON wr.condition_id = wc.condition_id
    JOIN cities c 
        ON wr.city_id = c.city_id
    GROUP BY c.city_id, c.city_name, c.country, wc.main
	),
	city_totals AS (
		SELECT 
			city_id,
			SUM(condition_count) AS total_records
		FROM city_condition_counts
		GROUP BY city_id
	),
	city_max_condition AS (
		SELECT 
			ccc.city_id,
			ccc.city_name,
			ccc.country,
			MAX(ccc.condition_count) AS max_condition_count
		FROM city_condition_counts ccc
		GROUP BY ccc.city_id, ccc.city_name, ccc.country
	)
	SELECT 
		cmc.city_name,
		cmc.country,
		ROUND((cmc.max_condition_count / ct.total_records) * 100, 2) AS stability_percentage
	FROM city_max_condition cmc
	JOIN city_totals ct 
		ON cmc.city_id = ct.city_id
	ORDER BY stability_percentage DESC;
---------------------------------------------------------------------------------------------------------------
-- 4.	Wind Analysis
	-- Average Wind Speeds in Different Regions (Countries)
SELECT 
    c.country,
    ROUND(AVG(w.wind_speed), 2) AS avg_wind_speed
FROM wind_data w
JOIN weather_records wr 
    ON w.record_id = wr.record_id
JOIN cities c 
    ON wr.city_id = c.city_id
GROUP BY c.country
ORDER BY avg_wind_speed DESC;

-- Cities with the Highest Wind Speeds
SELECT 
    c.city_name,
    c.country,
    MAX(w.wind_speed) AS max_wind_speed
FROM wind_data w
JOIN weather_records wr 
    ON w.record_id = wr.record_id
JOIN cities c 
    ON wr.city_id = c.city_id
GROUP BY c.city_name, c.country
ORDER BY max_wind_speed DESC
LIMIT 10;




-- Build “Latest Weather by City” View
create view latest_city_weather as
with 
cte_1 as (
select 
	record_id,
	city_id,
    condition_id
    recorded_at,
    row_number() over (partition by  city_id order by recorded_at desc ) as rn
     from weather_records
)
select 
	c.city_id,
    c.city_name,
    w.wind_speed,
    wr.temperature,
    wr.humidity,
    wc.main,
    cte_1.recorded_at
from cte_1
join cities c 
on cte_1.city_id=c.city_id
join weather_records wr
on cte_1.record_id = wr.record_id
join wind_data w
on cte_1.record_id = w.record_id
join weather_condition wc
on cte_1.condition_id = wc.condition_id
where rn = 1;
select * from latest_city_weather;


-- Condition Frequency & Rankings
-- syntax for percentage calculation
		-- SELECT 
		--     column_name,
		--     COUNT(*) AS cnt,
		--     (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM table_name)) AS percentage
		-- FROM table_name
		-- GROUP BY column_name;
