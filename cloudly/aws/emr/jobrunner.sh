#!/bin/bash

HOME=/home/hadoop
VENV=venv

source $HOME/$VENV/bin/activate
python -m $1
