# REST API in C++

A JSON REST API for an office hours queue, implemented in C++ with a Python test server.

## What it does

- Handles GET/POST/DELETE requests for a queue management system
- Parses JSON requests and responses using a single-header JSON library
- Implements a custom doubly-linked list
- Serves a static HTML/CSS frontend

## Files

- `api.cpp` — C++ API request handler
- `List.h` — custom linked list implementation
- `server.py` — Python test server
- `index.html` / `index.css` — frontend
- `Makefile` — build rules

## Build

```bash
make
./api.exe < requests.txt
```

`requests.txt` contains sample HTTP requests (GET, POST, DELETE) that exercise the queue endpoints.

## Key concepts

- REST API design
- JSON parsing
- Custom linked lists
- C++ I/O and string parsing
