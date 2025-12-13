DEVOPS & DEPLOYMENT
==================

Overview
--------
This project does not rely on a fully automated CI/CD pipeline, but it follows
clear deployment and operational practices adapted to its architecture.

The system is composed of:

- A **frontend** deployed on a managed platform (Vercel)
- A **backend API** executed as a long-running service
- **Scheduled ETL scripts** that populate an aggregation database
- Two PostgreSQL databases (production and aggregation)

The deployment strategy prioritizes simplicity, reproducibility, and separation
of concerns over heavy automation.


Deployment Architecture
-----------------------
The deployment model follows the logical architecture described in
:doc:`architecture`:

- The **Frontend** is a stateless Next.js application.
- The **Backend** is a FastAPI service exposing read-only analytical endpoints.
- **ETL scripts** are executed independently of the API lifecycle.
- The **Aggregation Database** is updated periodically and queried by the API.

No component requires tight coupling to another at runtime, except:

- Frontend → Backend (HTTP)
- Backend → Aggregation DB
- ETL scripts → Production DB + Aggregation DB


Frontend Deployment (Vercel)
----------------------------
The frontend is a Next.js application designed for seamless deployment on Vercel.

**Deployment workflow**:

1. Push the frontend code to a GitHub repository.
2. Import the repository into Vercel.
3. Configure environment variables.
4. Trigger automatic deployment.

Environment variables required:

::

   NEXT_PUBLIC_API_URL=http://localhost:8000

Vercel provides:

- Automatic builds on push
- Preview deployments for pull requests
- CDN-backed global delivery
- HTTPS and caching out of the box

No custom server configuration is required.


Backend Deployment
------------------
The backend is a FastAPI application intended to run as a persistent service on a
local or remote server.

Supported execution modes:

- Development: ``uvicorn --reload``
- Production:
  - ``uvicorn``
  - ``gunicorn`` with Uvicorn workers
  - Containerized execution (Docker)

**Recommended production command**:

::

   uvicorn main:app --host 0.0.0.0 --port 8000

The backend:

- Does not manage authentication
- Exposes read-only endpoints
- Depends on external PostgreSQL services
- Must remain available for frontend requests


Backend Environment Configuration
---------------------------------
All backend configuration is managed via environment variables loaded from a
``.env`` file using ``python-dotenv``.

Typical variables include:

::

   DB_USER=atle
   DB_PASSWORD=********
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=production_db
   AGG_DB_NAME=aggregation_db

The ``.env`` file must be present on the backend host but **must not** be
committed to version control.

An ``env_example.txt`` file is provided as a template.


ETL Scripts Execution
---------------------
ETL scripts are **not part of the API runtime**. They are executed independently
to populate and refresh the aggregation database.

Scripts are located in:

::

   backend/scripts/

Key ETL scripts include:

- ``etl_agg_sensor_stats.py`` – hourly sensor statistics
- ``etl_agg_utilization.py`` – daily machine utilization
- ``etl_agg_program_history.py`` – program execution durations
- ``etl_agg_alerts.py`` – alert counts and details
- ``etl_agg_energy_daily.py`` – energy consumption
- ``etl_agg_daily_runner.py`` – orchestrates incremental ETL runs

Execution modes:

- Manual execution from CLI
- Scheduled execution (cron, task scheduler, CI runner)

ETL scripts:

- Read from the **production database**
- Write to the **aggregation database**
- Are idempotent where applicable
- Can be safely re-run for backfills


Database Deployment Considerations
----------------------------------
Two PostgreSQL databases are required:

1. **Production Database**
   - Read-only access
   - High-volume raw sensor data
   - Never queried directly by the frontend

2. **Aggregation Database**
   - Custom schema created via ``create_agg_database.sql``
   - Optimized for analytics
   - Queried exclusively by the backend API

The aggregation schema must be initialized **once** before running ETL scripts.


Operational Workflow Summary
----------------------------
A typical operational flow is:

1. Production database receives raw machine data.
2. ETL scripts aggregate and store derived metrics.
3. Backend API serves aggregated data.
4. Frontend visualizes data via dashboards.

Each step can be monitored and debugged independently.


Logging and Monitoring
----------------------
Logging is handled at multiple levels:

- **Backend**
  - Uvicorn logs (startup, requests, errors)
  - Python logging inside ETL scripts

- **Frontend**
  - Vercel deployment logs
  - Runtime logs via browser developer tools

- **Database**
  - PostgreSQL logs (optional, environment-dependent)

No centralized logging system is currently configured, but the architecture
allows adding one if needed.



