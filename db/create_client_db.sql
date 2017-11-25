PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
CREATE TABLE "sensor" (
    "sensor_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "type" TEXT NOT NULL,
    "name" TEXT NOT NULL
);

CREATE TABLE "data" (
    "data_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "sensor_id" INTEGER NOT NULL,
    "data" INTEGER,
    "raw_data" INTEGER,
    "date" INTEGER NOT NULL,
    FOREIGN KEY(sensor_id) REFERENCES sensor(sensor_id)
);

COMMIT;
