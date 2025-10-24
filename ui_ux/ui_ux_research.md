# UI/UX Research: Interfaces for NC Machine Operations

This document compiles a survey of user interfaces, dashboards, and interaction patterns relevant to a system that analyzes high‑frequency data from **Numerical Control (NC) machines** and transforms it into actionable insights. The research focuses on visual and interactive solutions that help operators and engineers understand **machine operation**, **energy usage**, **timing per program**, and **alerts**, with examples from different sources. The purpose of this research is also to give to the frontend developers some ideas and insights on how the team can approach the design of the UI/UX.

The structure follows the project’s needs and proposes concrete UI components for each one, with references and example visuals.

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

**Examples**
- **MachineMetrics – “Current Shift Dashboard”** (real‑time factory dashboards with color‑coded status and OEE context).  
  ![MachineMetrics current shift dashboard](https://www.machinemetrics.com/hubfs/current-shift-dashboard.png)  
  _Source: MachineMetrics, “CNC Machine Monitoring Software.”_  
  <https://www.machinemetrics.com/machine-monitoring>

- **Ignition (Inductive Automation) – OEE dashboards** (customer projects showing real‑time and historical production insight; role‑based overview → detail screens).  
  Source: Inductive Automation, customer project overview.  
  <https://inductiveautomation.com/resources/customerproject/oee-spc-and-realtime-dashboards-for-greater-insight-into-six-production-lines>

**Component suggestions**
- `MachineStateTimeline` (bands for RUN/IDLE/ALARM, hover tooltips, shift shading).
- `DowntimePareto` (top N reasons; clickable to filter timeline).
- `UtilizationSummaryCard` (RUN %, planned vs. actual).

### Component Details

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

**Example**
- **Siemens MindSphere / Insights Hub – Dashboard Designer** (rich visualizations, queries, and OEE building blocks).  
  Docs (web): <https://documentation.mindsphere.io/MindSphere/apps/dashboard-designer-v10/creating-dashboards.html>  
  PDF (v10): <https://documentation.mindsphere.io/MindSphere/output-pdf-files/Dashboard%20Designer%20v10.pdf>

- **Tulip Interfaces – manufacturing dashboards** (production dashboards with real‑time data collection and app‑driven UI).  
  Blog (ES): <https://tulip.co/es/blog/6-manufacturing-dashboards-for-visualizing-production/>  
  Blog (EN): <https://tulip.co/blog/6-manufacturing-dashboards-for-visualizing-production/>  
  Product page: <https://tulip.co/production-management/manufacturing-dashboards/>

**Component suggestions**
- `RoleSwitcher` (operator/supervisor toggle with remembered preference).
- `QuickFilters` (shift, line, machine, program; pill UI with clear-all).
- `LayoutGrid` (cards with reflow for large monitors vs. tablets).

---

## 3) Determination of when the machine is working (state/condition)
**Goal:** Provide at-a-glance status and drill‑down into causes.

**UI patterns & components**
- **Status header** per machine (icon + state text + since duration).
- **Andon indicator** (large, color-coded signal with sound/notification hooks).
- **Tool/Spindle widget** (RPM, load, temperature, following error; sparklines).
- **Job/Program panel** (program name, count, cycle time, remaining).

**Examples**
- **MachineMetrics – real‑time dashboards & alerts** (status color coding, notifications).  
  <https://www.machinemetrics.com/machine-monitoring>

- **FANUC MT‑LINKi** (monitoring many CNCs; dashboards of utilization, cycle time, alarms).  
  Brochure (PDF): <https://www.fanucamerica.com/docs/default-source/cnc-files/brochures/mt-linki%28e%29-01.pdf>  
  Product page: <https://www.fanucamerica.com/products/cnc/cnc-software/machine-tool-data-collection-software/cnc-machine-monitoring-software-mtlink-i>  
  Overview article: <https://www.fanucamerica.com/news-resources/articles/fanuc-s-cnc-software-solutions-mt-link-i-and-fasdata>

**Component suggestions**
- `MachineStatusCard` (state, since, job, operator, OEE mini).
- `ProgramNow` (program name, cycle time rolling avg, next tool).
- `AlarmMiniFeed` (latest N events with severity chip).

---

## 4) Calculation of timing and energy demands per program name
**Goal:** Attribute cycle time and **energy consumption** to program/runs for cost and sustainability KPIs.

**UI patterns & components**
- **Energy-over-time with thresholds**, **stacked by machine** or **by program**.
- **Per‑program summary**: avg cycle time, kWh/cycle, cost per unit.
- **Daily/shift usage histograms** with anomaly flags.
- **Correlation view**: energy vs. spindle load vs. feed rate.

**Examples**
- **Grafana – Energy Monitoring dashboards** (open templates; time series + KPIs + histograms).  
  ![Grafana energy monitoring dashboard](https://grafana.com/api/dashboards/12091/images/7918/image)  
  _Source: Grafana Labs, “Energy Monitoring” dashboard template._  
  <https://grafana.com/grafana/dashboards/12091-energy-monitoring/>

- **Grafana – Energy Overview** (additional template).  
  <https://grafana.com/grafana/dashboards/17181-energy/>

**Component suggestions**
- `EnergyKPI` (Current Usage, Daily kWh, Cost; tariff-aware).  
- `ProgramEnergyTable` (program → kWh/cycle, cost/cycle, variance).  
- `EnergyHistogram` (last 30 days usage; click to filter time series).

---

## 5) Determination of alerts and their context (type & location)
**Goal:** Reduce response time by presenting **what**, **where**, and **who** should act.

**UI patterns & components**
- **Alert banner** with severity and affected scope (line/machine).
- **Alarm panel** with filters (type, location, time, program).
- **Context panel** that shows the related timeline window, last events, and playbook steps.
- **Notification routing** (email/SMS/in-app) with acknowledgement flow.

**Examples**
- **Ignition (Inductive Automation) – customer projects with real-time alarming and mobile access.**  
  <https://inductiveautomation.com/resources/customerproject/oee-spc-and-realtime-dashboards-for-greater-insight-into-six-production-lines>

- **FANUC MT‑LINKi** – email notifications & alarm history in multi‑machine dashboards.  
  Product: <https://www.fanucamerica.com/products/cnc/cnc-software/machine-tool-data-collection-software/cnc-machine-monitoring-software-mtlink-i>

**Component suggestions**
- `AlarmFeed` (live list; ack/assign; jump-to-time on click).
- `RootCausePanel` (last N sensor deviations; links to maintenance SOP).
- `MapToCell` (line → cell → machine breadcrumb).

---

## 6) Documentation of approach & algorithms (UX for transparency)
**Goal:** Make the system’s logic visible and trustworthy for operators and engineers.

**UI patterns & components**
- **“How it’s computed” drawers** on KPIs (Availability, Performance, Quality, OEE formula).
- **Model status** (last data ingest, latency, missing sensors).
- **Change log & data lineage** (source → transform → KPI).

**Reference examples**
- **MindSphere / Performance Insight**—end‑user dashboard creation and KPI building blocks.  
  PDF: <https://support.industry.siemens.com/cs/attachments/109777035/109777035_MindSphere_Applications_PerformanceInsight_DOC_v10_en.pdf>

- **Data‑Parc (ES)**—guides on real‑time manufacturing dashboards and OEE templates.  
  Intro (ES): <https://www.dataparc.com/es/blog/real-time-manufacturing-dashboard-setup-importance-benefits/>  
  OEE templates (EN): <https://www.dataparc.com/blog/oee-dashboard-templates-for-smarter-manufacturing/>

**Component suggestions**
- `KPIInfoPopover` (math, windowing, exclusions; mini examples).
- `DataQualityBadge` (OK / Delayed / Missing).
- `AuditTrail` (who changed thresholds, when).

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
- **Global navigation:** `AppShell`, breadcrumb for Line → Cell → Machine.
- **Overview dashboard:** `KPIBar` (OEE, Availability, Performance, Quality), `FleetGrid` (status per machine), `AlertTicker`.
- **Machine detail:** `MachineStatusCard`, `MachineStateTimeline`, `ProgramNow`, `ToolSpindleWidget`, `AlarmFeed`.
- **Energy & cost:** `EnergyKPI`, `EnergyOverTime`, `EnergyHistogram`, `ProgramEnergyTable`.
- **Analysis:** `DowntimePareto`, `DrilldownTabs` (Overview, Shift, Program, Alarms, Energy).
- **Transparency:** `KPIInfoPopover`, `DataQualityBadge`, `AuditTrail`.

---

## Notes on licensing and usage of assets
- All external screenshots are used for **research and comparative analysis**. Each image is linked to its public source (see captions/links above). Verify product licenses/permissions if reusing beyond internal research.
- Product names and logos are trademarks of their respective owners.

