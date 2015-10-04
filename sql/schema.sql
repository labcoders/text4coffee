DROP TABLE IF EXISTS link_privilege_account;
DROP TABLE IF EXISTS privilege;
DROP TABLE IF EXISTS account;

CREATE TABLE account (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    number VARCHAR UNIQUE NOT NULL
);

CREATE TABLE privilege (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

INSERT INTO privilege ( name ) VALUES ( 'control' );
INSERT INTO privilege ( name ) VALUES ( 'admin' );
INSERT INTO privilege ( name ) VALUES ( 'query' );

CREATE TABLE link_privilege_account (
    account_id INTEGER REFERENCES account ( id ),
    privilege_id INTEGER REFERENCES privilege ( id )
);
