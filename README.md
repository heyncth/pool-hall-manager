# Pool Hall Manager

A command-line tool to run a billiards hall: track table occupancy, compute
session bills, keep reservations and manage the stock of drinks and snacks.

This project started as a Java Swing prototype for a final course project and
was later ported to a Python CLI so it can be driven from the terminal and
scripted easily.

## Install

```bash
pip install -e .
```

## Usage

```bash
# open table 3 for play
poolhall open 3

# close table 3 and print the receipt
poolhall close 3 --discount 10

# reserve table 5 for a customer at 20:00
poolhall reserve 5 "Nguyen An" 20:00 --minutes 90

# check stock levels
poolhall inventory
poolhall inventory --restock "Chalk" 12

# daily report
poolhall report

# table status overview
poolhall status
```

## Configuration

Data is stored as JSON under `~/.poolhall/`. Defaults such as the hourly
rate, opening hours and VAT live in `poolhall/config.py` and can be tweaked
there without touching the CLI.

## Tests

```bash
python -m pytest tests/
```
