# Text-based Dungeon Crawling Game

This repository contains a Python implementation of the text-based dungeon crawling game.

## Install

Create a new conda environment with the necessary packages:
```
conda env create -f env/environment.yml
```
For development and test purposes, use env/environment_dev.yml. 

You can activate the environment at any time with the command:
```
conda activate <name_env>
```

## Run

In the activated environment, run the following command:
```
python main.py
```

## Test

In the activated environment, run the following command:
```
python -m unittest
```
To enable a higher level of verbosity, use the -v flag.