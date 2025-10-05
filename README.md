# 2025G2

## Project Overview
This project focuses on analyzing data collected from **Numerical Control (NC) machines** (milling, lathe, planner, etc.) to transform high-frequency data into human-understandable insights.

The aim is to support operators and engineers by providing information on machine operation, energy usage, and alerts in a structured and accessible way.

---

## Business Case
To analyze information collected by the numerical control and stored in high frequency, and to provide clear and understandable hints for human users.

---

## Needs
- Identify operation periods of the machine  
- Create a user interface to facilitate interaction  
- Determine when the machine is working  
- Calculate timing and energy demands per program name  
- Determine alerts and contextualize them (type and location)  
- Document the approach and algorithms  

---

## Approach
We will use:  
- **Backend:** FastAPI to process data, implement algorithms, and provide APIs  
- **Frontend:** React to build an interactive and user-friendly interface  
- **Database (if necessary):** A SQL-based database may be added later for storing and querying high-frequency data, depending on project scope and needs

This approach reflects how similar systems are implemented in real-world industry, ensuring scalability and maintainability beyond a prototype.

---

## Work Plan
We will follow an **iterative approach using Scrum with weekly sprints**. The development will focus first on delivering a minimal version of the system (MVP) and then expanding its functionality step by step.

- **Initial focus (MVP):** detect and display basic machine states (*working / idle*) through a FastAPI backend and a simple React dashboard.  
- **Further iterations:** add energy calculations per program, contextualized alerts and improved visualizations.
- **Continuous improvement:** refine the UI, extend backend endpoints, and ensure scalability so the solution can resemble a real-world system.  

---

## Structure (draft)
```
.
├── backend/        # FastAPI services & algorithms
├── frontend/       # React app
├── docs/           # Documentation & approach
└── README.md
