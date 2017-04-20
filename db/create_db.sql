PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
CREATE TABLE "sensor" (
    "sensor_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "type" TEXT NOT NULL,
    "name" TEXT NOT NULL
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE "data" (
    "data_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "sensor_id" INTEGER NOT NULL,
    "data" INTEGER,
    "raw_data" INTEGER,
    "date" INTEGER NOT NULL,
    FOREIGN KEY(sensor_id) REFERENCES sensor(sensor_id)
);
CREATE TABLE event (
    "event_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "tbl" TEXT NOT NULL,
    "rowid" INTEGER NOT NULL
);
CREATE TRIGGER "onInsert"
   AFTER 
   INSERT
   ON `data`
   FOR EACH ROW
BEGIN
    INSERT INTO event (tbl, rowid) 
        VALUES ("data", (SELECT MAX(data.data_id) from data));
END;
COMMIT;
