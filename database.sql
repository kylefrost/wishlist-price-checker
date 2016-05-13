CREATE DATABASE amazon;

USE amazon;

CREATE TABLE items (
    title VARCHAR(500),
    price VARCHAR(10),
    amazonid VARCHAR(11),
    internalid INT NOT NULL AUTO_INCREMENT,
    userid INT,
    date_added DATETIME,
    PRIMARY KEY(internalid)
)
