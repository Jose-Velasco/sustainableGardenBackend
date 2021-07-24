#!/bin/sh

psql -U sustainablegardenuser sustainablegarden < garden.dump

exit