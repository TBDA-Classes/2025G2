FRONTEND OVERVIEW
=================

Introduction
------------
The frontend is built with Next.js, React, TypeScript, and
Tailwind CSS. It provides a modern, responsive, and performant UI that interacts
with the backend API through Axios.

The design follows the UI/UX prototype created in Figma, resulting in a clear,
user-friendly monitoring interface.


Project Structure
-----------------
::

   frontend/
   ├── public/
   ├── src/
   │   ├── app/
   │   │   ├── layout.tsx
   │   │   ├── page.tsx
   │   │   └── dashboard/
   │   │       ├── [date]/page.tsx
   │   │       ├── alerts/page.tsx
   │   │       ├── calendar/page.tsx
   │   │       └── energy/page.tsx
   │   ├── components/
   │   │   ├── BarChart.tsx
   │   │   ├── BoxPlot.tsx
   │   │   ├── TimelineChart.tsx
   │   │   ├── Datepicker.tsx
   │   │   └── Sidebar.tsx
   │   ├── lib/api.ts
   │   └── types/
   │       ├── DateState.ts
   │       ├── Temperature.ts
   │       └── 
   └── README.md


Setup Instructions
------------------
::

   npm install
   npm run dev

Production build:

::

   npm run build
   npm start

Environment Variable:

::

   NEXT_PUBLIC_API_URL=http://localhost:8000


Pages and Routing
-----------------
Next.js App Router conventions:

* ``page.tsx`` – main entry for each route  
* ``layout.tsx`` – shared layout (sidebar, navbar)  
* ``loading.tsx`` – suspense state  
* ``error.tsx`` – error handler  
* ``not-found.tsx`` – 404 fallback  

Routes implemented:

* ``/dashboard``  
* ``/dashboard/[date]``  
* ``/energy``  
* ``/alerts``  


UI Components
-------------
* **Sidebar:**  
  Navigation between Dashboard, Energy, and Alerts.

* **Datepicker:**  
  Allows selecting any date from the production calendar.

* **TimelineChart:**  
  Displays RUN / IDLE / DOWN segments in 10-minute windows.

* **BarChart & BoxPlot:**  
  Used for energy and temperature visualizations.

* **Responsive Cards:**  
  Show machine utilization percentages, power readings, alerts summary, etc.


Data Flow
---------
All data requests are handled through ``lib/api.ts``:

* Machine utilization  
* Timeline segments  
* Temperature history  
* Energy metrics  
* Alerts lists and details  

The frontend’s reactivity and performance are driven by:

* Suspense boundaries  
* Client components  
* Lightweight Axios wrappers  
* Tailwind-based styling system  

All data comes from the aggregation pipeline described in :doc:`db_sql`.
