# Database Schema Design

A relational database schema with tables, views, and data loading scripts.

## What it does

- Defines normalized tables with primary/foreign keys
- Creates views for common queries
- Loads data from external sources
- Includes drop scripts for cleanup

## Files

- `createTables.sql` — table definitions
- `createViews.sql` — view definitions
- `loadData.sql` — data loading
- `dropTables.sql` / `dropViews.sql` — cleanup

## Use

```bash
sqlite3 mydb < createTables.sql
sqlite3 mydb < loadData.sql
sqlite3 mydb < createViews.sql
```

## Key concepts

- Relational schema design
- Normalization
- SQL DDL (CREATE, DROP)
- Views and data loading
