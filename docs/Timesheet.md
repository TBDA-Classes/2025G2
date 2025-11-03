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
| Atle Sund | Frontend/Backend | Setup Backend | Set up a simple backend project in FastAPI | 2025-10-06 | 1 |
| Jovan Bajcetic | UI/UX + Scrum master | Meeting with client and PO | Meeting with the client to see requirements related to UI/UX and data + Resolution of some doubts about the project with the PO | 2025-10-09 | 1 |
| Javier Pajares | Data Analyst | Meeting with client and PO | Meeting with the client to see requirements related to UI/UX and data + Resolution of some doubts about the project with the PO | 2025-10-09 | 1 |
| Atle Sund | Frontend/Backend | Setup Backend | Successfully connected to the PostgreSQL DB and created an endpoint for the frontend to access | 2025-10-12 | 1 |
| Atle Sund | Frontend/Backend | Setup Frontend and connect to Backend | Created a frontend project in Next.js and connected to an existing GET endpoint in the backend. The data was retrieved successfully and shown in localhost | 2025-10-12 | 1.5 |
| Atle Sund | Frontend/Backend | Backend | Generated ER diagrams (using DBeaver, found at docs/ER_diagrams) of tables 1245 and 2207 which are useful for us in the backend when creating models (see backend/models.py). | 2025-10-12 | 0.5 |
| Erik Alexander Standal | Frontend / Backend | Study and evaluate project technologies | Read documentation and watched some videos on the project tech | 2025-10-17 | 1 |
| Erik Alexander Standal | Frontend / Backend | GitHub cleanup | Made a documentation folder and updated the README.md file | 2025-10-20 | 0.5 |
| Jovan Bajcetic | UI/UX + Scrum master | UI/UX research doc | Creation and elaboration of the ui_ux_research.md document with the research done | 2025-10-23 | 1 |
| Jovan Bajcetic | UI/UX + Scrum master | UI/UX research doc | Revision of some points and links on the doc + restructuration of the file | 2025-10-24 | 0.5 |
| Atle Sund | Frontend/Backend | Data analysis and frontend | Read through the documentation by the data analysis team and worked on their quieries and findings in order to understand better which elements we need in the frontend. Spent some time also looking into the libraries recharts, nivo, react-charjs-2, visx etc. Landed on using nivo for the basic plots as it is comprehensive enough and fast. Created two static plots using this, one calendar plot and one stacked bar plot  | 2025-10-26 | 5 |
| Atle Sund | Frontend/Backend | Backend | Changed the approach to utilize sqlalchemy to the fullest. Now we don't query with raw SQL, only with ORM, see main.py | 2025-10-26 | 2 |
| Atle Sund | Frontend/Backend | Backend | Created a document to explain to the data analysis team exactly how we need to receive their data based on the queries they have made | 2025-10-27 | 1 |
| Atle Sund | Frontend/Backend | Backend | Made a docs/backend and docs/frontend, and filled in our existing documentation. Created an endpoint for the current query from DA (successful) | 2025-10-29 | 4 |
| Erik Alexander Standal | Frontend | Connect to backend endpoint | Used the endpoint created by the backend developers to make the bar plot dynamic. It works, but the query seems to be very slow, and I will wait with the calendar view because it is more comprehensive, and not possible with the current query time | 2025-11-03 | 4 |
| Jovan Bajcetic | UI/UX + Scrum master | UI/UX prototype | Creation of the figma prototype and edition | 2025-11-02 | 1.5 |
---

 *Tip:*  
If the text in “Description” is long, you can use line breaks (`<br>`) to keep it readable.  
Example:  
`Reviewed UI screens<br>Created wireframes for dashboard`

---






