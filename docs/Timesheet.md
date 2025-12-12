# Team Timesheet

This file is used by all team members to record their working hours and activities.

---

## How to add a new activity

1. Scroll down to the **Activity Log Table** below.  
2. Add a **new row at the bottom of the table** following the same format.  
3. Do **not** modify other members’ entries.  
4. Make sure each field is separated by a vertical bar `|` and that you keep one space around it for readability.  
5. Use the date format `YYYY-MM-DD`.  

---

## Column definitions

| Column | Description |
|--------|--------------|
| **Name** | Your full name (e.g., `Jovan Bajcetic`) |
| **Role** | Your role in the team (e.g., `UI/UX`, `Scrum Master`, `Backend`, `Data Analyst`, etc.) |
| **Activity** | Short title of the task or meeting |
| **Description** | A short summary of what was done |
| **Date** | The date of the activity in `YYYY-MM-DD` format |
| **Working Hours** | Number of hours worked (decimal values are fine, e.g., `1`, `0.5`, `2.25`) |

---

## Activity Log Table (editable)

> **Instructions:** Add your new record as a new line below the header row,  
> keeping the `|` separators and the same order of columns.

| Name | Role | Activity | Description | Date | Working Hours |
|------|------|-----------|--------------|------|----------------|
| Andres Janeiro | Data Analyst | Analysis | Initial analysis of the data in the php | 2025-10-02 | 3 |
| Javier Pajares | Data Analyst | Analysis | Initial analysis of the data in the php | 2025-10-02 | 3 |
| Andres Janeiro | Data Analyst | Documentation | Creation of the document containing all the info | 2025-10-05 | 2 |
| Javier Pajares | Data Analyst | Documentation | Creation of the document containing all the info | 2025-10-05 | 2 |
| Atle Sund | Frontend/Backend | Setup Backend | Set up a simple backend project in FastAPI | 2025-10-06 | 1 |
| Javier Pajares | Data Analyst | Queries | Creation of the first queries | 2025-10-07 | 1.5 |
| Jovan Bajcetic | UI/UX + Scrum master | Meeting with client and PO | Meeting with the client to see requirements related to UI/UX and data + Resolution of some doubts about the project with the PO | 2025-10-09 | 1 |
| Javier Pajares | Data Analyst | Meeting with client and PO | Meeting with the client to see requirements related to UI/UX and data + Resolution of some doubts about the project with the PO | 2025-10-09 | 1 |
| Atle Sund | Frontend/Backend | Setup Backend | Successfully connected to the PostgreSQL DB and created an endpoint for the frontend to access | 2025-10-12 | 1 |
| Atle Sund | Frontend/Backend | Setup Frontend and connect to Backend | Created a frontend project in Next.js and connected to an existing GET endpoint in the backend. The data was retrieved successfully and shown in localhost | 2025-10-12 | 1.5 |
| Atle Sund | Frontend/Backend | Backend | Generated ER diagrams (using DBeaver, found at docs/ER_diagrams) of tables 1245 and 2207 which are useful for us in the backend when creating models (see backend/models.py). | 2025-10-12 | 0.5 |
| Erik Alexander Standal | Frontend | Study and evaluate project technologies | Read documentation and watched some videos on the project tech | 2025-10-17 | 1 |
| Javier Pajares | Data Analyst | Queries | Queries for the working time of the machine | 2025-10-18 | 2.5 |
| Andres Janeiro | Data Analyst | Queries | Queries for the working time of the machine | 2025-10-18 | 2 |
| Andres Janeiro | Data Analyst | Documentation | Creation of the ERD | 2025-10-18 | 1.5 |
| Javier Pajares | Data Analyst | Documentation | Create a description for each table of the php | 2025-10-18 | 0.5 |
| Andres Janeiro | Data Analyst | Documentation | Create a description for each table of the php | 2025-10-18 | 0.5 |
| Erik Alexander Standal | Frontend | GitHub cleanup | Made a documentation folder and updated the README.md file | 2025-10-20 | 0.5 |
| Clemence Tardivel | UI/UX | UI/UX prototype | First version of the figma protype | 2025-10-22 | 1.5  |
| Jovan Bajcetic | UI/UX + Scrum master | UI/UX research doc | Creation and elaboration of the ui_ux_research.md document with the research done | 2025-10-23 | 1 |
| Jovan Bajcetic | UI/UX + Scrum master | UI/UX research doc | Revision of some points and links on the doc + restructuration of the file | 2025-10-24 | 0.5 |
| Javier Pajares | Data Analyst | Documentation | Creation of the markdown document | 2025-10-25 | 1 |
| Atle Sund | Frontend/Backend | Data analysis and frontend | Read through the documentation by the data analysis team and worked on their quieries and findings in order to understand better which elements we need in the frontend. Spent some time also looking into the libraries recharts, nivo, react-charjs-2, visx etc. Landed on using nivo for the basic plots as it is comprehensive enough and fast. Created two static plots using this, one calendar plot and one stacked bar plot  | 2025-10-26 | 5 |
| Atle Sund | Frontend/Backend | Backend | Changed the approach to utilize sqlalchemy to the fullest. Now we don't query with raw SQL, only with ORM, see main.py | 2025-10-26 | 2 |
| Atle Sund | Frontend/Backend | Backend | Created a document to explain to the data analysis team exactly how we need to receive their data based on the queries they have made | 2025-10-27 | 1 |
| Atle Sund | Frontend/Backend | Backend | Made a docs/backend and docs/frontend, and filled in our existing documentation. Created an endpoint for the current query from DA (successful) | 2025-10-29 | 4 |
| Erik Alexander Standal | Frontend | Connect to backend endpoint | Used the endpoint created by the backend developers to make the bar plot dynamic. It works, but the query seems to be very slow, and I will wait with the calendar view because it is more comprehensive, and not possible with the current query time | 2025-11-03 | 4 |
| Jovan Bajcetic | UI/UX + Scrum master | UI/UX prototype | Actualization of first figma protype and edition | 2025-11-02 | 1.5 |
| Clemence Tardivel | UI/UX | UI/UX prototype | Edition of the figma protype | 2025-11-02 | 1.5  |
| Atle Sund | Frontend/Backend | Frontend | Created a production worthy structure for the fronetend dividing the dashboard folder into dashboard-index, alerts and energy. Created a sidebar navigation. Started on the layout for the main Dashbaord, now waiting for confirmation that the data used by the plots are plausible from the data analysis team.   | 2025-11-14 | 3.5 |
| Javier Pajares | Data Analyst | Queries | Transform the queries for the frontend team | 2025-11-14 | 2 |
| Javier Pajares | Data Analyst | Queries | Identify and study the exact times of the machine | 2025-11-14 | 2 |
| Atle Sund | Frontend/Backend | Frontend | Finalized the "homepage" and made navigation possible  | 2025-11-19 | 1 |
| Atle Sund | Frontend/Backend | Backend | First doing data analysis to understand better the data and possibilities, also had meeting with Javier to discuss which information we need and how we can retrieve them  | 2025-11-20 | 2 |
| Atle Sund | Frontend/Backend | Backend | Created an aggregation database for better performance. This required setup for an additional DB connection, as well as new models found in models.py. Since our aggregation DB will be simple, SQLAlchemy will be used  | 2025-11-21 | 2 |
| Javier Pajares | Data Analyst | Queries | Review Figma Data & Graph Feasibility | 2025-11-24 | 1 |
| Javier Pajares | Data Analyst | Queries | Coordination between Data Analysis - UI/UX | 2025-11-24 | 1.5 |
| Atle Sund | Frontend/Backend | Backend | Worked on the ETL script to facilitate date inputs, this way it will be easier to test. Will also add sensor type as an argument.  | 2025-11-25 | 1.5 |
| Atle Sund | Frontend/Backend | Backend | Created connection to the aggregation DB using the credentials given by the professor. Created the DB and loaded data. | 2025-11-27 | 2 |
| Javier Pajares | Data Analyst | Queries | Make suggestion for layout on the machines "Working hours" | 2025-12-01 | 1.5 |
| Javier Pajares | Data Analyst | Queries | Finalize the queries for the first Figma Page | 2025-12-01 | 2 |
| Andrés Janeiro | Data Analyst | Queries | Finalize the queries for the first Figma Page | 2025-12-01 | 1 |
| Atle Sund | Frontend/Backend | Frontend/Backend | ETL scripts, models, types, api endpoints | 2025-12-03 | 3 |
| Erik Alexander Standal | Frontend | Frontend | Worked on the frontend, api connections and graphs| 2025-12-04 | 4 |
| Jovan Bajcetic | UI/UX + Scrum master | Documentation | Created first version of the project documentation using sphinx and created instructions to see this documentation on sphinx_documentation file | 2025-12-08 | 3 |
| Andres Janeiro | Data Analyst | Queries | Created queries for the energy page on Figma | 2025-12-10 | 3 |
| Javier Pajares | Data Analyst | Queries | Modify queries for working hours and program history | 2025-12-10 | 1.5 |
| Atle Sund | Frontend/Backend | Frontend/Backend | ETL scripts, models, types, api endpoints and graphs | 2025-11-03 | 3 |
| Atle Sund | Frontend/Backend | Frontend/Backend | ETL scripts, models, types, api endpoints and graphs | 2025-12-03 | 2 |
---

 *Tip:*  
If the text in “Description” is long, you can use line breaks (`<br>`) to keep it readable.  
Example:  
`Reviewed UI screens<br>Created wireframes for dashboard`

---






