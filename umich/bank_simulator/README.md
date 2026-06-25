# Bank Transaction Simulator

A discrete-event simulation of a banking system with scheduled transactions, fee calculation, and fraud detection.

## What it does

- Loads registered users from a file
- Processes login/logout/place commands
- Maintains a min-heap priority queue of pending transactions keyed by execution date
- Applies fee calculation (percentage, min/max caps, loyalty discounts)
- Validates transactions against fraud rules (IP-address checking)
- Supports query commands with binary search on sorted transaction logs

## Files

- `bank.cpp` — main command loop and simulation driver
- `classes.h` — User, Transaction, and Bank classes
- `Makefile` — build rules

## Build

```bash
make
./bank < commands.txt
```

## Key concepts

- Min-heap priority queue
- Discrete-event simulation
- Fee logic and fraud detection
- File I/O and command parsing
