#!/usr/bin/env bash

echo "The unit tests will be run in"
echo $PWD

# Run Reservation Service unit tests
echo "About to run Reservation Service unit tests"
nosetests -sv -x ../test --processes=-1 --process-timeout=300 --process-restartworker
