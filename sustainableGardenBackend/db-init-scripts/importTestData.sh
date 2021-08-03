#!/bin/sh

# adds the test data in the .dump file into the database
psql -U sustainablegardenuser sustainablegarden < garden.dump

exit