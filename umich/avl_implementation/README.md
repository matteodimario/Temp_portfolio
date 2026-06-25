# AVL Tree Implementation

A self-balancing binary search tree with automatic rebalancing via rotations.

## What it does

- Implements AVL insertion with all four rotation cases (LL, RR, LR, RL)
- Maintains balance factor after every insertion
- Includes a tree-diagram printer for debugging

## Files

- `avl_lab.h` — AVL tree class with Node struct, rotations, and insertion
- `avl_lab.cpp` — test driver
- `Makefile` — build rules

## Build

```bash
make
```

## Key concepts

- Pointer manipulation for tree restructuring
- Balance factor tracking
- Self-balancing binary search trees
