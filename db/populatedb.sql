-- Add some sensors
INSERT INTO sensor (type, name) VALUES ('a', 'batt1');
INSERT INTO sensor (type, name) VALUES ('a', 'batt2');

-- Add data from sensors
INSERT INTO data (sensor_id, data, raw_data, date)
            VALUES (2, 123, 987, 2017032723);
INSERT INTO data (sensor_id, data, raw_data, date)
            VALUES (1, 456, 654, 2017032723);
INSERT INTO data (sensor_id, data, raw_data, date)
            VALUES (1, 789, 321, 2017032723);
INSERT INTO data (sensor_id, data, raw_data, date)
            VALUES (2, 012, 098, 2017032723);
