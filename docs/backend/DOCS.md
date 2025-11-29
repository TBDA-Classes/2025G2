# Backend Documentation

**2025G2**  
**November 2025**

## Introduction

The backend uses **SQLAlchemy** as the Python SQL toolkit and Object Relational Mapper (ORM).  
This allows us to work with the database using Python classes and objects instead of hardcoded SQL queries.  
By doing so, data retrieved from the database can be handled as Python objects rather than tuples or dictionaries, providing a cleaner and more intuitive syntax.

## Database Driver

We use **psycopg3** as our PostgreSQL driver.  
A driver is a software component that enables communication between the application and the database system.  
In this context, **psycopg3** acts as the bridge between Python (through SQLAlchemy) and the PostgreSQL server, translating SQLAlchemy's commands into actual SQL understood by the database.

The newest version of psycopg (**psycopg3**) supports both *synchronous* and *asynchronous* modes. In asynchronous mode, queries can be executed concurrently without blocking, allowing for more efficient handling of multiple database operations—useful for concurrent operations and event-driven applications like ours. This might be useful at a later point.

## Environment Variables

We use a `.env` file to store sensitive information such as database usernames, passwords, and connection details.  
This keeps secret credentials out of the source code, which is important both for security and for flexibility when moving between different environments (for example, development and production).

The file is loaded automatically at runtime using the `python-dotenv` package.  
Once loaded, the variables can be accessed in Python through `os.getenv()`, which allows us to build the database connection string dynamically without exposing the actual credentials.

An example of a typical `.env` file:

```
DB_USER=atle
DB_PASSWORD=secretpassword
DB_HOST=localhost
DB_NAME=mydatabase
```


## Data Aggregation Strategy

The production database contains 321M+ rows of sensor data, making direct queries extremely slow (from several seconds to minutes to request). Since we want to follow industry standards, which says that the user should not wait more than 10 seconds without getting the results, and no more than 3 seconds before they see some animation, we use a **dual-database architecture** with an ETL process:

### Architecture

```
Production DB (Read-Only)  →  ETL Script  →  Aggregation DB  →  FastAPI
   321M rows                                  Pre-computed       10-50ms
```

- **Production Database**: Read-only access to raw sensor data
- **Aggregation Database**: Separate PostgreSQL database we control, stores pre-computed aggregations
- **ETL Script** (`backend/scripts/...`): Will contain scripts that extracts data from production, transforms via aggregation queries, and loads results into our database.


### Features for better performance

#### B-Tree indexing

We will use B-Tree indexes for dates since the `SELECT` statements comming from the backend will almost all the time contain a `WHERE date = . AND sensor_name = .` clause. A B-Tree index is a separate structure that creates some sorting algorithm. This way, the lookup is logarithmic instead of linear. Note: If you use `EXPLAIN ANALYZE` as the first row in a SQL statement, it will say "Index Scan ..." if the index was utilized, if not it will say "Seq Scan".

#### Views for up to date status on data in aggregation DB

We have created a view which gives useful insights in agg_sensor_stats, such as the first and last date of entries. This is crucial since we want to restrict the options for the user to the dates we actually have data for.

---

# Reference Guide

*The following sections contain setup instructions and useful commands we have encountered during the project which is continously updated.*

---

## Database Connection Setup

This section documents the process of establishing a connection to the remote PostgreSQL database server used in this project.

### Prerequisites

#### VPN Connection
Access to the PostgreSQL database server requires an active VPN connection to the university network.

#### PostgreSQL Installation
While the database server is remote, a local PostgreSQL client installation is required to test connections and interact with the database from the command line. On macOS, PostgreSQL can be installed via Homebrew:

```
brew install postgresql@14
brew services start postgresql@14
```

Note: The local PostgreSQL server is not required for the application to function, but is useful for development and testing purposes.

### Connection Parameters

The database server uses non-standard connection parameters:

- **Host:** `138.100.82.184` (IP address)
- **Port:** `2345` (non-standard port)
- **Username:** `lectura`
- **Database:** Multiple databases accessible (see Section Accessible Databases)

The hostname `apiict00.etsii.upm.es` resolves to `138.100.82.170`, which does not accept connections. However, phpPgAdmin shows the server running on `138.100.82.184:2345`. Therefore, we use the direct IP address.

The port `2345` is used instead of the default PostgreSQL port `5432`. This is likely a security measure to reduce automated attacks on the standard port, or to allow multiple PostgreSQL instances on the same server.

### Accessing PostgreSQL from Terminal

#### Basic Connection Command

To connect to the database from the command line:

```
psql -h 138.100.82.184 -U lectura -d <database_name> -p 2345
```

Where `<database_name>` is one of the accessible databases (e.g., `postgres`, `1245`, or `2207`).

#### Useful PostgreSQL Prompt Commands

Once connected to the database (indicated by the `database_name=>` prompt), the following commands are useful:

| Command | Description |
|---------|-------------|
| `\l` | List all databases on the server |
| `\dt` | List all tables (relations) in the current database |
| `\dv` | List all views (relations) in the current database |
| `\d <table_name>` | Describe the structure of a specific table |
| `\du` | List all users/roles |
| `\conninfo` | Display current connection information |
| `\c <database>` | Connect to a different database |
| `\x` | Toggle expanded (vertical) display mode for better readability |
| `\q` | Quit the PostgreSQL prompt |
| `q` | Quit the current pager view |

#### JSON Operations in PostgreSQL

PostgreSQL provides powerful operators and functions for working with JSON and JSONB data types:

| Operator/Function | Description |
|-------------------|-------------|
| `->` | Extract JSON object field or array element (returns JSON/JSONB) |
| `->>` | Extract JSON object field or array element as text |
| `#>` | Extract nested JSON object at specified path (returns JSON/JSONB) |
| `#>>` | Extract nested JSON object at specified path as text |
| `jsonb_array_length()` | Returns the number of elements in the outermost JSON array |
| `jsonb_object_keys()` | Returns set of keys in the outermost JSON object |
| `jsonb_pretty()` | Returns JSONB data as indented JSON text for readability |
| `jsonb_typeof()` | Returns the type of the outermost JSON value as a text string |
| `jsonb_array_elements()` | Expands a JSON array to a set of JSON values (one per row) |
| `jsonb_each()` | Expands outermost JSON object into key-value pairs |

**Example:** For a JSON column `data` containing `{"user": {"name": "John"}, "count": 5}`:
- `data->'user'` returns `{"name": "John"}` as JSONB
- `data->>'count'` returns `"5"` as text
- `data->'user'->>'name'` returns `"John"` as text

#### Advanced SQL Operations

Beyond basic SELECT and FROM clauses, the following SQL operations are frequently used in our queries:

| Operation | Description |
|-----------|-------------|
| `INNER JOIN` | Returns only rows with matching values in both tables |
| `LEFT JOIN` | Returns all rows from left table and matching rows from right table (NULLs if no match) |
| `COUNT(*)` | Counts the number of rows (requires GROUP BY when used with non-aggregated columns) |
| `GROUP BY` | Groups rows sharing a property so aggregate functions can be applied to each group |
| `HAVING` | Filters groups after GROUP BY (WHERE filters rows before grouping) |
| `TO_TIMESTAMP()` | Converts Unix timestamp (seconds since epoch) to PostgreSQL timestamp |
| `EXTRACT()` | Extracts sub-fields from date/time values (e.g., EXTRACT(YEAR FROM date)) |
| `COALESCE()` | Returns the first non-NULL value in a list of arguments |
| `CASE WHEN` | Conditional expression allowing if-then-else logic in SQL |
| `DISTINCT` | Removes duplicate rows from the result set |
| `DISTINCT ON` | Returns first row of each group of duplicates based on specified columns |
| `PARTITION BY` | Divides result set into partitions for window functions |

**Important note on aggregation:** When using aggregate functions like `COUNT(*)`, `SUM()`, or `AVG()`, all non-aggregated columns in the SELECT clause must appear in the GROUP BY clause.

### Accessible Databases

Using the command `\l`, we determined that the `lectura` user has CONNECT privileges (`c`) on the following databases:

- `1245` -- 51 GB database (Access: `lectura=c/ncorrea`)
- `2207` -- 32 GB database (Access: `lectura=c/ncorrea`)
- `postgres` -- Default administrative database

### Testing the Connection

The FastAPI application includes a status endpoint at `/api/status` that tests the database connection by executing `SELECT version()`.

### API Connection Status

```
{
  "status": "API is running",
  "database": "Connected",
  "version": "('PostgreSQL 14.17...',)"
}
```
