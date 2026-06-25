# Custom String Class

A reimplementation of a subset of the C++ `<string>` library using raw `char*` memory.

## What it does

- Dynamic memory management with manual allocation/reallocation
- Implements `erase()`, `insert()`, `replace()`, `find_first_of()`, `find_last_of()`
- Copy-swap idiom for assignment
- Move constructor and move assignment (C++11)
- Null-terminator handling throughout

## Files

- `String.h` — class interface
- `String.cpp` — implementation
- `Makefile` — build rules

## Build

```bash
make
```

## Key concepts

- Raw pointer manipulation
- Manual memory management
- Rule of Five (constructor, destructor, copy, move, assignment)
- Copy-swap idiom
