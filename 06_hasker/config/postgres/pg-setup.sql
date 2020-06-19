CREATE DATABASE hasker;
CREATE USER hasker WITH PASSWORD 'hasker';
ALTER ROLE hasker SET client_encoding TO 'utf8';
ALTER ROLE hasker SET default_transaction_isolation TO 'read committed';
ALTER ROLE hasker SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE hasker TO hasker;
