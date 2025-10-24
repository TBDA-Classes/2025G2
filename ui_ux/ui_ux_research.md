# UI/UX Research: Interfaces for NC Machine Operations

This document compiles a survey of user interfaces, dashboards, and interaction patterns relevant to a system that analyzes high‑frequency data from **Numerical Control (NC) machines** and transforms it into actionable insights. The research focuses on visual and interactive solutions that help operators and engineers understand **machine operation**, **energy usage**, **timing per program**, and **alerts**, with examples from different sources. The purpose of this research is also to give to the frontend developers some ideas and insights on how the team can approach the design of the UI/UX.

**The structure follows the project’s needs and proposes concrete UI components for each one, with references and example visuals.**

---

## 1) Identification of operation periods
- **Goal:** Clearly show periods of **RUN / IDLE / DOWN** and transitions over time.
- **RUN** → the machine is actively working (executing a program, cutting, milling, etc.).
- **IDLE** → the machine is powered on but not performing productive work (waiting, setup, no command).
- **DOWN** → the machine is stopped due to an error, maintenance, or shutdown

**UI patterns & components**
- **State timeline / band chart** (stacked color bands per machine state).
- **Utilization trend + thresholds** (sparklines, line charts with shift markers).
- **Gantt‑like run timeline per machine** (one row per machine; zoom & pan).
- **Shift overlays** (background shading for shifts/breaks).
- **Downtime reason overlay** (tooltips with coded reasons).

**Why this pattern works**
- Operators can instantly read *when* and *how long* a machine ran, idled, or stopped and correlate with shifts and programs.
- Pairing the timeline with a **Pareto of downtime reasons** supports root‑cause analysis.

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
- Bands for **RUN / IDLE / ALARM** states with distinct color coding.  
- **Hover tooltips** showing details such as timestamps, duration, and cause of state changes.  
- **Shift shading** to visually differentiate work shifts or production periods.  
- Supports **zooming and panning** for detailed inspection of specific time windows.  
- Optional **real-time refresh** to update ongoing operations.

**Why it matters:**  
This visualization makes it easy for operators and engineers to identify when and for how long the machine was running, idle, or down. It provides immediate situational awareness, helps correlate events with production schedules, and supports decision-making for efficiency improvements.

---

#### **2. `DowntimePareto`**

**Description:**  
A Pareto chart that highlights the most frequent or impactful causes of machine downtime. It organizes downtime categories (e.g., maintenance, tool change, material shortage) by frequency or duration to reveal the dominant factors affecting productivity.

**Features:**  
- Displays the **top N downtime reasons** sorted by impact.  
- **Interactive filtering**—clicking on a downtime reason filters the timeline to highlight the corresponding events.  
- **Tooltips** showing cumulative percentages and occurrence counts.  
- Can switch between **duration-based** and **frequency-based** ranking.  
- Optional **export** or **drill-down** to view detailed event logs.

**Why it matters:**  
By visualizing which issues cause the most downtime, teams can prioritize corrective actions and maintenance planning. Connecting it with the timeline view helps users link root causes to specific time periods, making the analysis both quantitative and contextual.

---

#### **3. `UtilizationSummaryCard`**

**Description:**  
A compact KPI component that summarizes machine utilization over a selected time window. It shows the percentage of time spent in each operational state and compares planned vs. actual utilization.

**Features:**  
- Displays **RUN %**, **IDLE %**, and **DOWN %** in numeric or gauge form.  
- Highlights **planned vs. actual** utilization for performance tracking.  
- Supports **color coding** (green/yellow/red) for performance thresholds.  
- Can include **mini-trend sparkline** to show utilization evolution over time.  
- Responsive layout suitable for dashboards, tablets, or mobile screens.

**Why it matters:**  
This card offers a concise snapshot of performance for quick daily or shift reviews. It supports supervisors and operators by providing an at-a-glance understanding of machine effectiveness, helping to identify deviations and confirm improvements after interventions.

---

## 2) User interfaces to facilitate interaction
**Goal:** Make information accessible for different roles (operator vs. supervisor) and contexts (large screen, tablet, mobile).

**Design guidance**
- **Role‑based layouts**: concise KPIs for operators; comparative and historical views for supervisors.
- **Consistent color semantics** (e.g., RUN=green, IDLE=yellow, ALARM=red, SETUP=blue). Add text labels for accessibility.
- **Progressive disclosure**: overview → line → machine → program → cycle.
- **Real‑time feedback** with low-latency widgets and non-blocking updates.
- **Keyboard + touch affordances** (big hit targets, sticky headers, multi-select filters).
- **Dark theme** option for shop‑floor glare; high‑contrast theme for accessibility.

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
A UI control that allows users to switch between different interface modes depending on their role—such as **Operator**, **Supervisor**, or **Manager**. Each role can access a customized layout, data scope, and level of detail suitable for their responsibilities.

**Features:**  
- **Toggle or dropdown selector** for role choice.  
- Remembers the user’s **last selected role** for convenience.  
- Dynamically adjusts visible dashboards, KPIs, and available filters.  
- Integrates with **user authentication** or permissions for secure access.  
- Supports **visual cues** (icons, color headers) to indicate current mode.

**Why it matters:**  
Manufacturing environments have multiple user profiles with distinct needs. A `RoleSwitcher` ensures that each user sees the most relevant information without being overwhelmed. It enhances usability, reduces clutter, and supports efficient workflows.

---

#### **2. `QuickFilters`**

**Description:**  
A set of compact, easily accessible filters that allow users to narrow down data by key attributes such as **shift**, **production line**, **machine**, or **program name**. It enables rapid navigation and focused data exploration.

**Features:**  
- Filter chips or “pills” representing active filters, with **clear-all** functionality.  
- Support for **multi-select** and **hierarchical filters** (e.g., line → machine).  
- **Instant filtering** without reloading the entire dashboard (real-time updates).  
- Works seamlessly on **touch screens** and desktop interfaces.  
- Optional **search or dropdown selector** for long lists of items.  

**Why it matters:**  
Quick, intuitive filtering is essential for operators and supervisors who need to analyze specific subsets of data (e.g., a single shift or machine). This component improves interaction speed and makes dashboards more adaptable in fast-paced environments.

---

#### **3. `LayoutGrid`**

**Description:**  
A flexible layout system that organizes multiple dashboard components (cards, charts, KPIs) into a responsive grid. It ensures the interface remains functional and aesthetically consistent across different devices—from large control room screens to tablets or mobile devices.

**Features:**  
- **Responsive grid system** that automatically rearranges cards based on screen size.  
- Supports **drag-and-drop reordering** for customizable dashboards.  
- **Adaptive reflow** of elements for portrait and landscape orientations.  
- Adjustable **column and row spans** for different component priorities.  
- **Consistent spacing, padding, and alignment** to maintain readability.  

**Why it matters:**  
Manufacturing dashboards are often viewed on diverse hardware (HMI panels, tablets, desktop PCs). A well-designed `LayoutGrid` ensures information is readable and accessible everywhere, maintaining usability and visual hierarchy regardless of the display.

---

## 3) Determination of when the machine is working (state/condition)
**Goal:** Provide at-a-glance status and drill‑down into causes.

**UI patterns & components**
- **Status header** per machine (icon + state text + since duration).
- **Andon indicator** (large, color-coded signal with sound/notification hooks).
- **Tool/Spindle widget** (RPM, load, temperature, following error; sparklines).
- **Job/Program panel** (program name, count, cycle time, remaining).

**Examples & references**
- **MachineMetrics – real‑time dashboards & alerts** (status color coding, notifications).  
  <https://www.machinemetrics.com/machine-monitoring>

- **FANUC MT‑LINKi** (monitoring many CNCs; dashboards of utilization, cycle time, alarms).  
  Brochure (PDF): <https://www.fanucamerica.com/docs/default-source/cnc-files/brochures/mt-linki%28e%29-01.pdf>  
  Product page: <https://www.fanucamerica.com/products/cnc/cnc-software/machine-tool-data-collection-software/cnc-machine-monitoring-software-mtlink-i>  
  Overview article: <https://www.fanucamerica.com/news-resources/articles/fanuc-s-cnc-software-solutions-mt-link-i-and-fasdata>

### Component suggestions

#### **1. `MachineStatusCard`**

**Description:**  
A compact yet informative card showing the **current operational state** of a specific machine. It summarizes essential data such as status (RUN, IDLE, DOWN), how long it has been in that state, which job or program is running, and who is operating the machine.

**Features:**  
- Displays **current state** (color-coded icon and text).  
- Shows **duration since last state change** (e.g., “Running for 2h 15m”).  
- Option to include **operator name**, **machine ID**, and **OEE mini indicator**.  
- Supports **hover details** with performance metrics and job info.  
- Can integrate a **small trend sparkline** for cycle time or load.  

**Why it matters:**  
This component provides a quick, real-time snapshot of a machine’s activity and health. It helps operators monitor status at a glance and allows supervisors to see multiple machines’ conditions in a consistent visual format, improving situational awareness across the shop floor.

---

#### **2. `ProgramNow`**

**Description:**  
A focused panel displaying information about the **currently active CNC program or job**. It provides production context, including program name, part count, estimated cycle time, and tooling information.

**Features:**  
- Shows **active program name**, **cycle time (average and current)**, and **remaining operations**.  
- Displays **part counter** (produced vs. target).  
- Lists **next tool** and key process parameters (spindle load, feed rate).  
- Supports **rolling averages** for cycle-time performance tracking.  
- Optional integration with **job scheduling or MES system** for context.  

**Why it matters:**  
Operators and engineers need to understand what the machine is doing at any moment. The `ProgramNow` panel makes it easier to monitor job progress, detect delays, and optimize cycle performance, directly connecting operational data with production targets.

---

#### **3. `AlarmMiniFeed`**

**Description:**  
A live feed showing the most recent **alarm or event notifications** related to a specific machine or group of machines. Each event is represented with a short message and a visual severity indicator.

**Features:**  
- Lists the **latest N alarms or warnings**, with timestamps.  
- Includes **severity chips or color tags** (e.g., red for critical, yellow for warning).  
- Allows **click-through** to detailed alarm history or troubleshooting guide.  
- Can auto-refresh in real-time and support **acknowledgment** by users.  
- Optional **filter** by type (mechanical, electrical, program, safety).  

**Why it matters:**  
Quick visibility of recent alarms helps operators respond faster to critical issues and reduces downtime. The `AlarmMiniFeed` component integrates seamlessly with the dashboard, ensuring that alerts are visible without switching screens, supporting efficient problem resolution.


---

## 4) Calculation of timing and energy demands per program name
**Goal:** Attribute cycle time and **energy consumption** to program/runs for cost and sustainability KPIs.

**UI patterns & components**
- **Energy-over-time with thresholds**, **stacked by machine** or **by program**.
- **Per‑program summary**: avg cycle time, kWh/cycle, cost per unit.
- **Daily/shift usage histograms** with anomaly flags.
- **Correlation view**: energy vs. spindle load vs. feed rate.

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
A compact widget displaying the key **energy-related performance indicators** for each machine or group of machines. It provides real-time and aggregated metrics such as current power usage, total energy consumed, and cost estimates based on tariffs.

**Features:**  
- Shows **current power draw (kW)** and **daily/shift energy usage (kWh)**.  
- Calculates **cost estimates** dynamically based on energy tariffs.  
- Displays **trend arrows** (up/down) compared to the previous period.  
- Optional **threshold indicators** (e.g., red if exceeding target consumption).  
- Integrates with **sustainability KPIs** like CO₂ emissions per cycle.  

**Why it matters:**  
Energy usage is a significant cost driver in manufacturing. The `EnergyKPI` component makes consumption transparent, enabling teams to monitor efficiency and correlate energy peaks with machine activity. It also supports sustainability tracking by converting energy data into actionable cost and environmental metrics.

---

#### **2. `ProgramEnergyTable`**

**Description:**  
A data table summarizing **energy performance per program or job**, allowing comparison of energy consumption, cycle time, and cost efficiency across multiple production runs.

**Features:**  
- Lists **programs/jobs** with columns for average **kWh/cycle**, **cost per cycle**, and **variance** from baseline.  
- Supports **sorting and filtering** (e.g., by machine, operator, or date).  
- Option to **aggregate data** by shift, line, or production batch.  
- Provides **trend indicators** showing improvements or regressions.  
- Can include **export to CSV/XLSX** for reporting and analysis.  

**Why it matters:**  
Different CNC programs may have drastically different energy demands. The `ProgramEnergyTable` allows engineers to identify high-consumption programs, optimize machining parameters, and evaluate the cost-benefit of energy-saving measures. It bridges operational data with financial and sustainability perspectives.

---

#### **3. `EnergyHistogram`**

**Description:**  
A histogram visualization that displays **energy consumption distribution** over time (e.g., daily, shift-based, or program-based). It highlights peaks, anomalies, and overall consumption patterns.

**Features:**  
- Shows **bar charts** representing energy usage for defined time intervals (e.g., hours, shifts, or days).  
- Can be **stacked by machine, line, or energy source**.  
- Allows **click-to-filter** interaction—selecting a bar filters related time series views.  
- Supports **anomaly markers** or alerts for abnormal energy spikes.  
- Option to overlay **average and target lines** for performance comparison.  

**Why it matters:**  
Visualizing energy usage distribution helps detect irregularities, inefficiencies, and opportunities for savings. The `EnergyHistogram` component provides a clear overview of consumption trends, allowing teams to quickly identify when and where excessive energy is being used.

---

## 5) Determination of alerts and their context (type & location)
**Goal:** Reduce response time by presenting **what**, **where**, and **who** should act.

**UI patterns & components**
- **Alert banner** with severity and affected scope (line/machine).
- **Alarm panel** with filters (type, location, time, program).
- **Context panel** that shows the related timeline window, last events, and playbook steps.
- **Notification routing** (email/SMS/in-app) with acknowledgement flow.

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
- **Live feed** showing the most recent alarms and events.  
- **Severity color coding** (e.g., red = critical, orange = warning, blue = info).  
- **Acknowledgement and assignment** controls (ack, resolve, assign to user).  
- **Click-to-time** link: selecting an alarm highlights the corresponding moment in the machine timeline.  
- Supports **real-time refresh** and sorting by priority, time, or machine.  
- Optional **filter panel** for alarm type, location, or affected program.  

**Why it matters:**  
Timely visibility of alarms is essential for minimizing downtime and ensuring safety. The `AlarmFeed` component helps teams react quickly by combining alarm data with contextual information and providing direct access to the relevant time window or machine involved.

---

#### **2. `RootCausePanel`**

**Description:**  
A contextual panel designed to explain *why* an alarm occurred by showing relevant data from sensors, logs, or process conditions preceding the event. It acts as a quick diagnostic tool that links alarms to possible causes and standard operating procedures (SOPs).

**Features:**  
- Displays the **last N sensor deviations** or anomalies before an alarm.  
- Shows **trend charts** of key parameters leading up to the event.  
- Includes **links to maintenance SOPs** or troubleshooting guides.  
- **Highlight correlations** (e.g., high spindle load → tool wear).  
- Option to **attach operator notes or photos** for future reference.  

**Why it matters:**  
Understanding the root cause of an alarm reduces repetitive failures and improves preventive maintenance. The `RootCausePanel` connects alarms to data-driven explanations and actionable steps, turning reactive troubleshooting into a proactive process.

---

#### **3. `MapToCell`**

**Description:**  
An interactive breadcrumb-style navigation component that helps users locate the **physical position** of a machine or alarm source within the production hierarchy (e.g., Plant → Line → Cell → Machine).

**Features:**  
- **Hierarchical navigation**: from plant overview down to specific machine.  
- Displays **current selection** and allows quick navigation back up levels.  
- Highlights **machines or cells** affected by active alarms.  
- Can include **mini-map or schematic view** for spatial context.  
- Supports integration with **floor plan or layout diagrams**.  

**Why it matters:**  
When alarms occur, knowing *where* they happened is as important as knowing *what* happened. The `MapToCell` component provides spatial and organizational context, helping maintenance teams quickly locate equipment, coordinate responses, and avoid confusion in large facilities.

---

## 6) Documentation of approach & algorithms (UX for transparency)
**Goal:** Make the system’s logic visible and trustworthy for operators and engineers.

**UI patterns & components**
- **“How it’s computed” drawers** on KPIs (Availability, Performance, Quality, OEE formula).
- **Model status** (last data ingest, latency, missing sensors).
- **Change log & data lineage** (source → transform → KPI).

**Examples & references**
- **MindSphere / Performance Insight**—end‑user dashboard creation and KPI building blocks.  
  PDF: <https://support.industry.siemens.com/cs/attachments/109777035/109777035_MindSphere_Applications_PerformanceInsight_DOC_v10_en.pdf>

- **Data‑Parc (ES)**—guides on real‑time manufacturing dashboards and OEE templates.  
  Intro (ES): <https://www.dataparc.com/es/blog/real-time-manufacturing-dashboard-setup-importance-benefits/>  
  OEE templates (EN): <https://www.dataparc.com/blog/oee-dashboard-templates-for-smarter-manufacturing/>

### Component suggestions

#### **1. `KPIInfoPopover`**

**Description:**  
An interactive information popover attached to each KPI widget that explains **how the metric is calculated**, including formulas, data sources, time windows, and applied exclusions. It helps users understand the logic behind key performance indicators.

**Features:**  
- Displays **KPI formula** (e.g., *OEE = Availability × Performance × Quality*).  
- Lists **included and excluded data sources** or conditions.  
- Shows **calculation window** (e.g., last shift, rolling 24 hours).  
- Provides **mini example** with sample input and output values.  
- Optional link to **detailed documentation** or SOP.  

**Why it matters:**  
Transparency builds trust. When users can see *how* a KPI is computed, they’re more confident in the system’s accuracy. The `KPIInfoPopover` helps demystify analytics and supports training, auditing, and troubleshooting processes.

---

#### **2. `DataQualityBadge`**

**Description:**  
A small status indicator that shows the **quality or freshness of data** feeding the dashboard or KPI. It immediately signals whether the displayed information is reliable, delayed, or incomplete.

**Features:**  
- **Color-coded states:**  
  - 🟢 **OK** – data updated within the expected window.  
  - 🟡 **Delayed** – last update older than expected.  
  - 🔴 **Missing** – data unavailable or invalid.  
- Displays **timestamp of last successful update**.  
- Tooltip showing **data source** and **expected frequency**.  
- Integrates with system alerts when data quality drops.  
- Can appear globally (for all data) or per widget.  

**Why it matters:**  
In industrial systems, decisions depend on reliable data. The `DataQualityBadge` increases user confidence and prevents misinterpretation of stale or incomplete metrics by making data health visible and explicit in the UI.

---

#### **3. `AuditTrail`**

**Description:**  
A component that logs and displays **changes made to system configurations or KPIs**, including who made the change, what was modified, and when. It provides traceability and accountability for threshold adjustments, formula edits, or data corrections.

**Features:**  
- Lists **recent modifications** with timestamp, user ID, and description.  
- Allows **filtering by user, date range, or component**.  
- Supports **export or print** for compliance documentation.  
- Can include **diff view** to highlight what changed (old vs. new values).  
- Integrates with role-based permissions for secure visibility.  

**Why it matters:**  
Traceability is critical in regulated and data-driven environments. The `AuditTrail` ensures accountability and enables teams to review and validate changes that affect KPIs or production analytics. It supports both governance and continuous improvement processes.


---

## Additional sources (ecosystem context)
- **Asseco Spain** – MES/MOM & dashboards in production control (Spanish article).  
  <https://assecospaingroup.es/noticias/details/sistemas-mes-y-mom-de-control-digital-de-produccion-industrial-462/>

- **Tulip (ES)** – dashboards de fabricación y orígenes de datos típicos.  
  <https://tulip.co/es/blog/6-manufacturing-dashboards-for-visualizing-production/>

- **SCADA academic example (ES)** – diseño de interfaz para línea automatizada (PDF).  
  <https://www.dspace.espol.edu.ec/bitstream/123456789/54280/1/T-112156%20CORELLA%20ZAMORA-REYES%20ANGUISACA.pdf>

---

## Summary of recommended UI component library (for implementation)

Below is an overview of the key UI components recommended for implementation, grouped by functionality area.  
Each component includes a representative image example and a link to its original source for reference.

---

###  **Global Navigation**

- **`AppShell`** — overall application layout, including header, sidebar, and breadcrumb navigation (Line → Cell → Machine).  
  ![Dashboard layout shell example](https://miro.medium.com/v2/resize:fit:1400/1*fT2r2A4OAjr2z0uvhsp0MA.png)  
  _Source: “Building dashboards with navigation in React” (Medium)._  
  <https://medium.com/>

---

###  **Overview Dashboard**

- **`KPIBar`** — top-level metrics such as OEE, Availability, Performance, and Quality.  
  ![KPI bar example](https://grafana.com/api/dashboards/14500/images/11716/image)  
  _Source: Grafana Labs – “KPI Dashboard Template.”_  
  <https://grafana.com/grafana/dashboards/14500/>

- **`FleetGrid`** — grid view of machine statuses (RUN/IDLE/DOWN).  
  ![Fleet grid example](https://www.machinemetrics.com/hubfs/current-shift-dashboard.png)  
  _Source: MachineMetrics – “Current Shift Dashboard.”_  
  <https://www.machinemetrics.com/machine-monitoring>

- **`AlertTicker`** — scrolling ticker showing active alerts.  
  ![Alert ticker example](https://cdn.dribbble.com/userupload/11293439/file/original-0d174b1b8a16a040b216bc6f8b1c70f4.png)  
  _Source: Dribbble – “Factory Dashboard Alert UI.”_  
  <https://dribbble.com/>

---

###  **Machine Detail**

- **`MachineStatusCard`** — displays current state, operator, job, and OEE mini metric.  
  ![Machine status card example](https://cdn.dribbble.com/userupload/9953919/file/original-9db6875b8b7a9c30a63b856ca81d8ad7.png)  
  _Source: Dribbble – “Industrial Dashboard Card Design.”_

- **`MachineStateTimeline`** — shows RUN/IDLE/ALARM states over time.  
  ![Machine state timeline example](https://cdn.worldvectorlogo.com/logos/gantt-chart-example.svg)  
  _Source: Wikimedia Commons – “Gantt chart example.”_

- **`ProgramNow`** — current job information and cycle progress.  
  ![Program panel example](https://cdn.dribbble.com/userupload/9729802/file/original-06a99a20a7dbf3aee73640b6a8fbd1e3.png)  
  _Source: Dribbble – “Manufacturing Process Dashboard.”_

- **`ToolSpindleWidget`** — displays spindle load, RPM, and temperature with sparklines.  
  ![Spindle widget example](https://cdn.dribbble.com/userupload/8560649/file/original-676b78b946f41c52df95f2077af3b4a2.png)  
  _Source: Dribbble – “Equipment Performance Monitor.”_

- **`AlarmFeed`** — shows the latest alarms with severity levels.  
  ![Alarm feed example](https://cdn.dribbble.com/userupload/10873644/file/original-4fcb1b9127b257a7a89c97dc6ddda96f.png)  
  _Source: Dribbble – “Alert Feed UI.”_

---

###  **Energy & Cost**

- **`EnergyKPI`** — real-time and cumulative energy consumption and cost.  
  ![Energy KPI example](https://grafana.com/api/dashboards/12091/images/7918/image)  
  _Source: Grafana Labs – “Energy Monitoring Dashboard.”_  
  <https://grafana.com/grafana/dashboards/12091-energy-monitoring/>

- **`EnergyOverTime`** — line chart of energy usage across time intervals.  
  ![Energy over time chart example](https://grafana.com/api/dashboards/17181/images/12544/image)  
  _Source: Grafana Labs – “Energy Overview Dashboard.”_  
  <https://grafana.com/grafana/dashboards/17181-energy/>

- **`EnergyHistogram`** — histogram of energy consumption by shift/day.  
  ![Energy histogram example](https://cdn.dribbble.com/userupload/11195486/file/original-bab272cb482f837c348b2e552063fcb5.png)  
  _Source: Dribbble – “Data Histogram Visualization.”_

- **`ProgramEnergyTable`** — per-program table with kWh/cycle, cost, and efficiency variance.  
  ![Energy program table example](https://cdn.dribbble.com/userupload/10701647/file/original-1e35ee779e49ed0c901b1b0e8ff5b183.png)  
  _Source: Dribbble – “Energy Data Table UI.”_

---

###  **Analysis**

- **`DowntimePareto`** — Pareto chart showing top causes of downtime.  
  ![Downtime Pareto example](https://www.researchgate.net/publication/342784709/figure/fig3/AS:917180184514561@1594019950399/Pareto-Chart-showing-the-distribution-of-downtime-reasons.png)  
  _Source: ResearchGate – “Pareto Chart for Downtime Analysis.”_

- **`DrilldownTabs`** — navigational tabs for switching between Overview, Shift, Program, Alarms, and Energy views.  
  ![Drilldown tabs example](https://cdn.dribbble.com/userupload/10490916/file/original-716acb48c84bb2b342ff53e5d89fc1a4.png)  
  _Source: Dribbble – “Dashboard Navigation Tabs.”_

---

###  **Transparency**

- **`KPIInfoPopover`** — explains formulas, data sources, and examples for each KPI.  
  ![KPI info popover example](https://cdn.dribbble.com/userupload/10804343/file/original-44e0139d4ab95c42de6ee568a4b53c5b.png)  
  _Source: Dribbble – “Tooltip Information Component.”_

- **`DataQualityBadge`** — indicates data freshness and reliability.  
  ![Data quality badge example](https://cdn.dribbble.com/userupload/11098943/file/original-5a5e9f9fd9a24c74541f4ad8f2b7db35.png)  
  _Source: Dribbble – “Status Indicator UI.”_

- **`AuditTrail`** — log of user and configuration changes for traceability.  
  ![Audit trail example](https://cdn.dribbble.com/userupload/10518883/file/original-36d0590f3b37b5f6bb9e3a0db13fa0c8.png)  
  _Source: Dribbble – “Activity Log Dashboard.”_



---

## Notes on licensing and usage of assets
- All external screenshots are used for **research and comparative analysis**. Each image is linked to its public source (see captions/links above). Verify product licenses/permissions if reusing beyond internal research.
- Product names and logos are trademarks of their respective owners.

