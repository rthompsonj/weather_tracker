#!/bin/bash

## DOCKER bash script.
## used inside of the docker container to launch the app.

/usr/bin/mongod &
sleep 1
/miniconda/bin/python flask_app.py
