#!/bin/bash

# turn on bash's job control
set -m

python -m game_engine &

yarn --cwd game_frontend serve &

fg %1
