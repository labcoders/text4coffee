#!/bin/bash

source bin/activate

python photographer.py > photographer.log &
python analyzer.py > analyzer.log &
python run.py
