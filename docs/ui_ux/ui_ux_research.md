# UI/UX Research: Interfaces for NC Machine Operations

FIGMA PROTOTYPE: https://www.figma.com/make/RSHfWMGrR5SyWN58c47tp1/Industrial-Dashboard-Prototype?fullscreen=1

The document presents research on user interfaces, dashboards, and interaction patterns for a system that analyzes high-frequency data from Numerical Control (NC) machines to generate actionable insights. It focuses on visual and interactive solutions that help operators and engineers understand machine performance, energy consumption, program timing, and alerts, including examples from various sources. Additionally, it aims to provide frontend developers with ideas and references for designing the UI/UX. The structure aligns with the project’s needs and proposes specific interface components with visual examples
---

## 1) Identification of operation periods
- **Goal:** Clearly show periods of **RUN / IDLE / DOWN** and transitions over time.
- **RUN** → the machine is actively working (executing a program, cutting, milling, etc.).
- **IDLE** → the machine is powered on but not performing productive work (waiting, setup, no command).
- **DOWN** → the machine is stopped due to an error, maintenance, or shutdown

**Examples & references**
- **MachineMetrics – “Current Shift Dashboard”** (real‑time factory dashboards with color‑coded status and OEE context).  
  ![MachineMetrics current shift dashboard](https://www.machinemetrics.com/hubfs/current-shift-dashboard.png)  
  _Source: MachineMetrics, “CNC Machine Monitoring Software.”_  
  <https://www.machinemetrics.com/machine-monitoring>

- **Ignition (Inductive Automation) – OEE dashboards** (customer projects showing real‑time and historical production insight; role‑based overview → detail screens).  
  Source: Inductive Automation, customer project overview.  
  <https://inductiveautomation.com/resources/customerproject/oee-spc-and-realtime-dashboards-for-greater-insight-into-six-production-lines>

### Component suggestions

#### **1. `MachineStateTimeline`**

**Description:**  
A timeline visualization that displays each machine’s activity across time, using colored bands to represent operational states such as RUN, IDLE, and ALARM. It allows users to instantly interpret how the machine’s condition changes during the day or across shifts.

**Features:**  
- Bands for RUN / IDLE / ALARM states with distinct color coding.  
- Hover tooltips showing details such as timestamps, duration, and cause of state changes.  
- Shift shading to visually differentiate work shifts or production periods.  
- Supports zooming and panning for detailed inspection of specific time windows.  
- Optional real-time refresh to update ongoing operations.

---

#### **2. `DowntimePareto`**

**Description:**  
A Pareto chart that highlights the most frequent or impactful causes of machine downtime. It organizes downtime categories (e.g., maintenance, tool change, material shortage) by frequency or duration to reveal the dominant factors affecting productivity.

**Features:**  
- Displays the top N downtime reasons sorted by impact.  
- Interactive filtering—clicking on a downtime reason filters the timeline to highlight the corresponding events.  
- Tooltips showing cumulative percentages and occurrence counts.  
- Can switch between duration-based and frequency-based ranking.  
- Optional export or drill-down to view detailed event logs.

---

#### **3. `UtilizationSummaryCard`**

**Description:**  
A compact KPI component that summarizes machine utilization over a selected time window. It shows the percentage of time spent in each operational state and compares planned vs. actual utilization.

**Features:**  
- Displays RUN %, IDLE %, and DOWN % in numeric or gauge form.  
- Highlights planned vs. actual utilization for performance tracking.  
- Supports color coding (green/yellow/red) for performance thresholds.  
- Can include mini-trend sparkline to show utilization evolution over time.  
- Responsive layout suitable for dashboards, tablets, or mobile screens.


---

## 2) User interfaces to facilitate interaction
**Goal:** Make information accessible for different roles (operator vs. supervisor) and contexts (large screen, tablet, mobile).

**Examples & references**
- **Siemens MindSphere / Insights Hub – Dashboard Designer** (rich visualizations, queries, and OEE building blocks).  
  Docs (web): <https://documentation.mindsphere.io/MindSphere/apps/dashboard-designer-v10/creating-dashboards.html>  
  PDF (v10): <https://documentation.mindsphere.io/MindSphere/output-pdf-files/Dashboard%20Designer%20v10.pdf>

- **Tulip Interfaces – manufacturing dashboards** (production dashboards with real‑time data collection and app‑driven UI).  
  Blog (ES): <https://tulip.co/es/blog/6-manufacturing-dashboards-for-visualizing-production/>  
  Blog (EN): <https://tulip.co/blog/6-manufacturing-dashboards-for-visualizing-production/>  
  Product page: <https://tulip.co/production-management/manufacturing-dashboards/>

### Component suggestions

#### **1. `RoleSwitcher`**

**Description:**  
A UI control that allows users to switch between different interface modes depending on their role—such as Operator, Supervisor, or Manager. Each role can access a customized layout, data scope, and level of detail suitable for their responsibilities.

**Features:**  
- Toggle or dropdown selector for role choice.  
- Remembers the user’s last selected role for convenience.  
- Dynamically adjusts visible dashboards, KPIs, and available filters.  
- Integrates with user authentication or permissions for secure access.  
- Supports visual cues (icons, color headers) to indicate current mode.


---

#### **2. `QuickFilters`**

**Description:**  
A set of compact, easily accessible filters that allow users to narrow down data by key attributes such as shift, production line, machine, or program name. It enables rapid navigation and focused data exploration.

**Features:**  
- Filter chips or “pills” representing active filters, with clear-all functionality.  
- Support for multi-select and hierarchical filters (e.g., line → machine).  
- Instant filtering without reloading the entire dashboard (real-time updates).  
- Works seamlessly on touch screens and desktop interfaces.  
- Optional search or dropdown selector for long lists of items.  

---

#### **3. `LayoutGrid`**

**Description:**  
A flexible layout system that organizes multiple dashboard components (cards, charts, KPIs) into a responsive grid. It ensures the interface remains functional and aesthetically consistent across different devices—from large control room screens to tablets or mobile devices.

**Features:**  
- Responsive grid system that automatically rearranges cards based on screen size.  
- Supports drag-and-drop reordering for customizable dashboards.  
- Adaptive reflow of elements for portrait and landscape orientations.  
- Adjustable column and row spans for different component priorities.  
- Consistent spacing, padding, and alignment to maintain readability.  


---

## 3) Determination of when the machine is working (state/condition)
**Goal:** Provide at-a-glance status and drill‑down into causes.


**Examples & references**

- **FANUC MT‑LINKi** (monitoring many CNCs; dashboards of utilization, cycle time, alarms).  
  Brochure (PDF): <https://www.fanucamerica.com/docs/default-source/cnc-files/brochures/mt-linki%28e%29-01.pdf>  
  Product page: <https://www.fanucamerica.com/products/cnc/cnc-software/machine-tool-data-collection-software/cnc-machine-monitoring-software-mtlink-i>  
  Overview article: <https://www.fanucamerica.com/news-resources/articles/fanuc-s-cnc-software-solutions-mt-link-i-and-fasdata>

### Component suggestions

#### **1. `MachineStatusCard`**

**Description:**  
A compact yet informative card showing the current operational state of a specific machine. It summarizes essential data such as status (RUN, IDLE, DOWN), how long it has been in that state, which job or program is running, and who is operating the machine.

**Features:**  
- Displays current state (color-coded icon and text).  
- Shows duration since last state change (e.g., “Running for 2h 15m”).  
- Option to include operator name, machine ID, and OEE mini indicator.  
- Supports hover details with performance metrics and job info.  
- Can integrate a small trend sparkline for cycle time or load.  



---

#### **2. `ProgramNow`**

**Description:**  
A focused panel displaying information about the currently active CNC program or job. It provides production context, including program name, part count, estimated cycle time, and tooling information.

**Features:**  
- Shows active program name, cycle time (average and current), and remaining operations.  
- Displays part counter (produced vs. target).  
- Lists next tool and key process parameters (spindle load, feed rate).  
- Supports rolling averages for cycle-time performance tracking.  
- Optional integration with job scheduling or MES system for context.  


---

#### **3. `AlarmMiniFeed`**

**Description:**  
A live feed showing the most recent alarm or event notifications related to a specific machine or group of machines. Each event is represented with a short message and a visual severity indicator.

**Features:**  
- Lists the latest N alarms or warnings, with timestamps.  
- Includes severity chips or color tags (e.g., red for critical, yellow for warning).  
- Allows click-through to detailed alarm history or troubleshooting guide.  
- Can auto-refresh in real-time and support acknowledgment by users.  
- Optional filter by type (mechanical, electrical, program, safety).  



---

## 4) Calculation of timing and energy demands per program name
**Goal:** Attribute cycle time and energy consumption to program/runs for cost and sustainability KPIs.


**Examples & references**
- **Grafana – Energy Monitoring dashboards** (open templates; time series + KPIs + histograms).  
  ![Grafana energy monitoring dashboard](https://grafana.com/api/dashboards/12091/images/7918/image)  
  _Source: Grafana Labs, “Energy Monitoring” dashboard template._  
  <https://grafana.com/grafana/dashboards/12091-energy-monitoring/>

- **Grafana – Energy Overview** (additional template).  
  <https://grafana.com/grafana/dashboards/17181-energy/>

### Component suggestions

#### **1. `EnergyKPI`**

**Description:**  
A compact widget displaying the key energy-related performance indicators for each machine or group of machines. It provides real-time and aggregated metrics such as current power usage, total energy consumed, and cost estimates based on tariffs.

**Features:**  
- Shows current power draw (kW) and daily/shift energy usage (kWh).  
- Calculates cost estimates dynamically based on energy tariffs.  
- Displays trend arrows (up/down) compared to the previous period.  
- Optional threshold indicators (e.g., red if exceeding target consumption).  
- Integrates with sustainability KPIs like CO₂ emissions per cycle.  


---

#### **2. `ProgramEnergyTable`**

**Description:**  
A data table summarizing energy performance per program or job, allowing comparison of energy consumption, cycle time, and cost efficiency across multiple production runs.

**Features:**  
- Lists programs/jobs with columns for average kWh/cycle, cost per cycle, and variance from baseline.  
- Supports sorting and filtering (e.g., by machine, operator, or date).  
- Option to aggregate data by shift, line, or production batch.  
- Provides trend indicators showing improvements or regressions.  
- Can include export to CSV/XLSX for reporting and analysis.  

---

#### **3. `EnergyHistogram`**

**Description:**  
A histogram visualization that displays energy consumption distribution over time (e.g., daily, shift-based, or program-based). It highlights peaks, anomalies, and overall consumption patterns.

**Features:**  
- Shows bar charts representing energy usage for defined time intervals (e.g., hours, shifts, or days).  
- Can be stacked by machine, line, or energy source.  
- Allows click-to-filter interaction—selecting a bar filters related time series views.  
- Supports anomaly markers or alerts for abnormal energy spikes.  
- Option to overlay average and target lines for performance comparison.  


---

## 5) Determination of alerts and their context (type & location)
**Goal:** Reduce response time by presenting what, where, and who should act.


**Examples & references**
- **Ignition (Inductive Automation) – customer projects with real-time alarming and mobile access.**  
  <https://inductiveautomation.com/resources/customerproject/oee-spc-and-realtime-dashboards-for-greater-insight-into-six-production-lines>

- **FANUC MT‑LINKi** – email notifications & alarm history in multi‑machine dashboards.  
  Product: <https://www.fanucamerica.com/products/cnc/cnc-software/machine-tool-data-collection-software/cnc-machine-monitoring-software-mtlink-i>

### Component suggestions

#### **1. `AlarmFeed`**

**Description:**  
A dynamic component that displays a live list of active and recent alarms across machines or production lines. It provides instant visibility into what’s going wrong, when, and at what severity, with the ability to acknowledge and assign alerts.

**Features:**  
- Live feed showing the most recent alarms and events.  
- Severity color coding (e.g., red = critical, orange = warning, blue = info).  
- Acknowledgement and assignment controls (ack, resolve, assign to user).  
- Click-to-time link: selecting an alarm highlights the corresponding moment in the machine timeline.  
- Supports real-time refresh and sorting by priority, time, or machine.  
- Optional filter panel for alarm type, location, or affected program.  



---

#### **2. `RootCausePanel`**

**Description:**  
A contextual panel designed to explain *why* an alarm occurred by showing relevant data from sensors, logs, or process conditions preceding the event. It acts as a quick diagnostic tool that links alarms to possible causes and standard operating procedures (SOPs).

**Features:**  
- Displays the last N sensor deviations or anomalies before an alarm.  
- Shows trend charts of key parameters leading up to the event.  
- Includes links to maintenance SOPs or troubleshooting guides.  
- Highlight correlations (e.g., high spindle load → tool wear).  
- Option to attach operator notes or photos for future reference.  



---

#### **3. `MapToCell`**

**Description:**  
An interactive breadcrumb-style navigation component that helps users locate the physical position of a machine or alarm source within the production hierarchy (e.g., Plant → Line → Cell → Machine).

**Features:**  
- Hierarchical navigation: from plant overview down to specific machine.  
- Displays current selection and allows quick navigation back up levels.  
- Highlights machines or cells affected by active alarms.  
- Can include **mini-map or schematic view for spatial context.  
- Supports integration with floor plan or layout diagrams.  



---

## 6) Documentation of approach & algorithms (UX for transparency)
**Goal:** Make the system’s logic visible and trustworthy for operators and engineers.



**Examples & references**
- **MindSphere / Performance Insight**—end‑user dashboard creation and KPI building blocks.  
  PDF: <https://support.industry.siemens.com/cs/attachments/109777035/109777035_MindSphere_Applications_PerformanceInsight_DOC_v10_en.pdf>

- **Data‑Parc (ES)**—guides on real‑time manufacturing dashboards and OEE templates.  
  Intro (ES): <https://www.dataparc.com/es/blog/real-time-manufacturing-dashboard-setup-importance-benefits/>  
  OEE templates (EN): <https://www.dataparc.com/blog/oee-dashboard-templates-for-smarter-manufacturing/>

### Component suggestions

#### **1. `KPIInfoPopover`**

**Description:**  
An interactive information popover attached to each KPI widget that explains how the metric is calculated, including formulas, data sources, time windows, and applied exclusions. It helps users understand the logic behind key performance indicators.

**Features:**  
- Displays KPI formula (e.g., *OEE = Availability × Performance × Quality*).  
- Lists included and excluded data sources or conditions.  
- Shows calculation window (e.g., last shift, rolling 24 hours).  
- Provides mini example with sample input and output values.  
- Optional link to detailed documentation or SOP.  



---

#### **2. `DataQualityBadge`**

**Description:**  
A small status indicator that shows the quality or freshness of data feeding the dashboard or KPI. It immediately signals whether the displayed information is reliable, delayed, or incomplete.

**Features:**  
- Color-coded states:  
  -  OK – data updated within the expected window.  
  -  Delayed – last update older than expected.  
  -  Missing – data unavailable or invalid.  
- Displays timestamp of last successful update.  
- Tooltip showing data source and expected frequency.  
- Integrates with system alerts when data quality drops.  
- Can appear globally (for all data) or per widget.  



---

#### **3. `AuditTrail`**

**Description:**  
A component that logs and displays changes made to system configurations or KPIs, including who made the change, what was modified, and when. It provides traceability and accountability for threshold adjustments, formula edits, or data corrections.

**Features:**  
- Lists recent modifications with timestamp, user ID, and description.  
- Allows filtering by user, date range, or component.  
- Supports export or print for compliance documentation.  
- Can include diff view to highlight what changed (old vs. new values).  
- Integrates with role-based permissions for secure visibility.  



---

