#!/bin/bash

/usr/bin/mongod &
sleep 1
/miniconda/bin/python flask_app.py
