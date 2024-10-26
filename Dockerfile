FROM postgres:16-alpine

COPY sql/dbinit.sql /docker-entrypoint-initdb.d/