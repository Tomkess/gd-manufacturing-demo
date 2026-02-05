# Manufacturing

example dataset to deploy:

- available as [github raw csv file](https://raw.githubusercontent.com/kubow/Data_playground/main/output/production_line.csv)
- Motherduck can speed up processing by runing below query:
```sql
CREATE OR REPLACE TABLE orders AS
      FROM READ_CSV_AUTO('https://raw.githubusercontent.com/kubow/Data_playground/main/output/production_line.csv', header=True)
```
- you can then create data connection and an empty workspace using the REST file or manually (update in `gooddata.yaml` and `.env` files accordingly)
- last part is to restore analytics using node-CLI tool:
```shell
gd validate
gd deploy
```
- alternatively you can directly upload the csv file to gooddata cloud

## Free datasets available

- SECOM Manufacturing Data
    - Semiconductor manufacturing processes
    - Source: UCI Machine Learning Repository ([link](https://archive.ics.uci.edu/ml/datasets/SECOM))
- FordA and FordB Datasets
    - Car production line
    - Source: UCR Time Series Classification Archive ([link](NA))
- Bosch Production Line Performance
    - Sensor data from a manufacturing production line
    - Source: [Kaggle](https://www.kaggle.com/c/bosch-production-line-performance)
- Tennessee Eastman Process Simulation Data
    - Chemical production process with multivariate time-series data
    - Source: [The Tennessee Eastman Process: an Open Source Benchmark | KeepFloyding](https://keepfloyding.github.io/posts/Ten-East-Proc-Intro/)
- CMAPSS (The Commercial Modular Aero-Propulsion System Simulation) Data:
    - Description: simulation of a jet engine
    - Source: [NASA](https://data.nasa.gov/Aerospace/CMAPSS-Jet-Engine-Simulated-Data/ff5v-kuh6/about_data)


## Example Dataset fields

### General Information

- Powerline ID: A unique identifier for each powerline.
- Segment ID: Identifier for segments within a powerline.
- Line Name: The name or designation of the powerline.
- Substation ID: ID of the substation to which the powerline is connected.
- Voltage Level: Operating voltage of the powerline (e.g., 110kV, 220kV).
- Circuit Type: Type of electrical circuit (single-circuit, double-circuit).
- Line Type: Overhead, underground, or submarine.
- Operational Status: Status of the powerline (active, decommissioned, under maintenance).

### Geospatial Data

- Latitude: Latitude coordinates of specific points on the powerline.
- Longitude: Longitude coordinates of specific points on the powerline.
- Elevation: Elevation above sea level at specific points.
- Line Length: Length of the powerline segment.
- Route Description: Details of the route (urban, rural, forested areas).
- Nearby Infrastructure: Proximity to roads, railways, water bodies, etc.
- Crossing Points: Points where the line crosses roads, rivers, railways, etc.

### Structural Data

- Tower ID: Unique identifier for each tower/pole.
- Tower Type: Type of tower (e.g., suspension, tension).
- Tower Height: Height of the tower.
- Span Length: Distance between two towers.
- Conductor Type: Type of conductor used (material, size).
- Insulator Type: Type of insulator (porcelain, glass, composite).
- Foundation Type: Type of foundation used for towers/poles.
- Ground Clearance: Minimum clearance of the line from the ground.

### Environmental Data

- Temperature: Ambient temperature near the powerline.
- Wind Speed: Wind speed data at various points.
- Weather Conditions: Historical weather conditions (rain, snow, fog).
- Solar Radiation: Solar radiation intensity in the area.
- Vegetation Density: Vegetation near the powerline.
- Corrosion Factors: Data on corrosion risks (salt, humidity, pollution).

### Electrical Data

- Current Load: Electrical current passing through the line.
- Power Factor: Power factor for the segment.
- Line Losses: Power losses in the line.
- Impedance: Impedance of the line.
- Voltage Drop: Voltage drop along the line.
- Thermal Rating: Maximum current carrying capacity of the line.

### Inspection and Maintenance Data

- Inspection Date: Date of the last inspection.
- Inspection Method: Method used (e.g., drone, helicopter, ground).
- Fault Records: History of faults (e.g., short circuits, breakages).
- Maintenance History: Records of maintenance activities performed.
- Repair History: Details of any repairs carried out.
- Damage Type: Type of damage observed (e.g., broken conductor, insulator damage).
- Criticality: Assessment of the criticality of the observed issues.

### Asset Data

- Installation Date: Date when the powerline or segment was installed.
- Asset Age: Age of the asset in years.
- Manufacturer: Manufacturer details of the line components.
- Warranty Status: Warranty status of various components.
- Depreciation: Depreciation value of the asset.

### Operational Data

- Outage Records: History of outages on the powerline.
- Load Data: Historical load data.
- Fault Frequency: Frequency of faults over a period.
- Protection Settings: Settings of the protection equipment (e.g., relays, breakers).
- Resilience Measures: Measures in place to enhance line resilience.

### Regulatory and Compliance Data

- Safety Standards: Applicable safety standards and compliance.
- Environmental Compliance: Compliance with environmental regulations.
- Zoning Laws: Information on zoning laws affecting the powerline route.
- Inspection Compliance: Records of regulatory inspections.

### Operational Constraints

- Right-of-Way: Data on the right-of-way along the powerline.
- Access Restrictions: Restrictions for accessing certain areas of the line.
- Permits: Required permits for maintenance, repair, or expansion.
- Nearby Sensitive Areas: Proximity to sensitive areas like schools, hospitals, etc.

### Reliability and Performance Metrics

- SAIDI (System Average Interruption Duration Index): Average outage duration.
- SAIFI (System Average Interruption Frequency Index): Frequency of outages.
- CAIDI (Customer Average Interruption Duration Index): Average time to restore power.
- MAIFI (Momentary Average Interruption Frequency Index): Frequency of momentary interruptions.
- MTBF (Mean Time Between Failures): Average time between failures.

### Historical Data

- Previous Configurations: Historical configurations of the line.
- Past Failures: Documented past failures and their causes.
- Line Upgrades: Records of any upgrades made to the line.
- Past Environmental Data: Historical environmental data affecting the line.

### Advanced Analytics (if applicable)

- Predictive Maintenance Scores: Scores predicting the likelihood of failure.
- Risk Assessment: Risk scores based on various factors.
- Asset Health Index: Overall health index of the powerline.
- Anomaly Detection Records: Records of detected anomalies.

### Imagery and Sensor Data (if applicable)

- Infrared Imaging: Thermal imaging data.
- Lidar Data: Lidar data for precise measurements.
- Camera Footage: Footage from inspection cameras or drones.
- Vibration Data: Data from vibration sensors on the line.
- Sag Measurements: Data on conductor sag.
- Partial Discharge Data: Data on partial discharge activity.

### Comments and Annotations

- Inspector Notes: Notes and observations from inspectors.
- Maintenance Crew Feedback: Feedback from the maintenance team.
- Stakeholder Comments: Comments from stakeholders like landowners, regulators.
