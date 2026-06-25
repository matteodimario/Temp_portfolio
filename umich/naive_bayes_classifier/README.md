# Naive Bayes Classifier in C++

A text classifier using a bag-of-words Naive Bayes model, implemented from scratch in C++.

## What it does

- Parses CSV training data of labeled posts
- Computes word frequencies and conditional probabilities per label
- Classifies new posts using log-probability scoring
- Debug mode prints the full probability calculation

## Files

- `main.cpp` — classifier implementation
- `BinarySearchTree.h` — BST for ordered storage
- `Map.h` — hash map for frequency tables
- `TreePrint.h` — tree visualization utility
- `csvstream.h` — CSV parsing utility
- `Makefile` — build rules

## Build

```bash
make
./main.exe train.csv test.csv
```

Sample `train.csv` and `test.csv` are included. The CSV must have `tag` and `content` columns.

```bash
# with debug output
./main.exe train.csv test.csv --debug
```

## Key concepts

- Naive Bayes text classification
- Bag-of-words model
- Log-probability computation
- Custom data structures (BST, hash map)
