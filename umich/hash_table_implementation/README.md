# Templated Hash Table

A generic hash table using open addressing with linear probing.

## What it does

- Templated key/value storage with a custom Hasher functor
- Linear probing for collision resolution
- Automatic rehashing and growth when load factor exceeds threshold
- Tracks bucket status (Empty, Occupied, Deleted)
- Supports insert, erase, and operator[]

## Files

- `hashtable.h` — hash table class template
- `hash.cpp` — test driver
- `Makefile` — build rules

## Build

```bash
make
```

## Key concepts

- Hash tables with open addressing
- Linear probing
- Template metaprogramming
- Automatic rehashing
