# GitHub Repository Review Log: 2026-05-20

This review pass screened GitHub repositories from the `data center cooling`, `datacenter cooling`, `PUE data center`, and `data center liquid cooling` search streams. The goal was to promote relevant repositories into the main README while preserving caveats about validation, educational status, or vendor/product positioning.

## Promoted To README

| Repository | Decision | Rationale |
| --- | --- | --- |
| [cldunlap73/BubbleID](https://github.com/cldunlap73/BubbleID) | Include | Lab-related paper artifact and open-source framework for pool-boiling bubble interface dynamics analysis using segmentation, tracking, and classification. |
| [UARK-NED3/BubbleID-Flow](https://github.com/UARK-NED3/BubbleID-Flow) | Include | Lab adaptation workspace for flow-boiling bubble segmentation, ROI preprocessing, high-speed image sequence handling, COCO annotation utilities, and Mask R-CNN fine-tuning. |
| [UARK-NED3/FlowLab](https://github.com/UARK-NED3/FlowLab) | Include | Lab toolkit for single-phase and two-phase liquid-cooling experiments, multimodal flow-loop data collection, acoustic emission, accelerometers, and analysis notebooks. |
| [UARK-NED3/AELab](https://github.com/UARK-NED3/AELab) | Include | Lab acoustic-emission analysis workspace for phase-change processes, flow boiling, pool boiling, and sensing-system tutorials. |
| [UARK-NED3/CFDTwin](https://github.com/UARK-NED3/CFDTwin) | Include | Lab desktop app for Ansys Fluent DOE automation, POD plus neural-network surrogate training, and Fluent comparison validation workflows. |
| [HewlettPackard/dc-rl](https://github.com/HewlettPackard/dc-rl) | Include | SustainDC provides documented Python environments for sustainable data center control, including cooling optimization, workload scheduling, battery management, Gymnasium integration, benchmarking algorithms, metrics, and a paper link. |
| [wfzheng/AlphaDataCenterCooling](https://github.com/wfzheng/AlphaDataCenterCooling) | Include | Virtual testbed with Docker service, Gymnasium environment, Modelica/FMU resources, and real-data-based cooling-system structure. |
| [nuoaleon/Data-center-PUE-prediction-tool](https://github.com/nuoaleon/Data-center-PUE-prediction-tool) | Include | Physics-based PUE prediction notebooks tied to a peer-reviewed Energy paper, climate-zone analysis, sensitivity analysis, and uncertainty quantification. |
| [2listic/datacenter-planner](https://github.com/2listic/datacenter-planner) | Include with caveat | Useful rack/room layout visualization tool for placing racks and cooling equipment; not a validated thermal solver. |
| [vk22006/predictive-cooling-optimizer-for-data-centers](https://github.com/vk22006/predictive-cooling-optimizer-for-data-centers) | Educational include | Documented predictive chiller scheduling project with feature engineering, XGBoost models, tests, and dashboard; useful as an educational predictive-control example. |
| [imamdoula004/AI-Hybrid-EMPC-DataCenter-Cooling](https://github.com/imamdoula004/AI-Hybrid-EMPC-DataCenter-Cooling) | Include as paper artifact | Simulation code for an IEEE manuscript on LSTM forecasting, hybrid economic MPC, PID supervision, cyber-physical resilience, cost, carbon, and ASHRAE constraints. |
| [4g/dcool](https://github.com/4g/dcool) | Include with caveat | Early reinforcement-learning/data-driven cooling control example; valuable historically and conceptually, but not a universal validated controller. |
| [kardashev-lab/datacenter-cooling-sim](https://github.com/kardashev-lab/datacenter-cooling-sim) | Candidate include | Simulation framework combining AI workload simulation, cooling simulation, AlphaDataCenterCooling adapters, telemetry, and dashboards; needs deeper validation review. |
| [ME421-Capstone-Project/chiller-model](https://github.com/ME421-Capstone-Project/chiller-model) | Educational include | Chiller array simulation package with thermal interference, greedy optimization, aging, startup ramp, wind, dynamic load, tests, and docs. |
| [femmetronics/Data-Center-Cooling-System](https://github.com/femmetronics/Data-Center-Cooling-System) | Educational include | Smart cooling/workload scheduling simulation with water, energy, carbon, psychrometric calculations, and cooling mode selection. |
| [Jalaljalili/Cooling-Dynamic-Model](https://github.com/Jalaljalili/Cooling-Dynamic-Model) | Educational include | RC thermal model and PID controller with transfer functions, Bode plots, disturbance injection, actuator limits, and closed-loop visualization. |
| [D1D104/fuzzy-miso-datacenter-cooling](https://github.com/D1D104/fuzzy-miso-datacenter-cooling) | Educational include | Fuzzy/Mamdani CRAC control prototype using MQTT and Node-RED monitoring. |
| [Lucabr01/RL-and-Gradient-Free-Based-Datacenter-Cooling-Controller](https://github.com/Lucabr01/RL-and-Gradient-Free-Based-Datacenter-Cooling-Controller) | Educational include | Sinergym/EnergyPlus project comparing Soft Actor-Critic and evolutionary strategies for data center HVAC energy and thermal safety. |
| [rishithayanidhi/Data_Center_Cooling_Optimization_Environment](https://github.com/rishithayanidhi/Data_Center_Cooling_Optimization_Environment) | Candidate include | FastAPI/Hugging Face style RL environment for multi-zone temperature management and energy optimization; needs validation review. |
| [SohelHossain1218/Smart-IoT-Data-Center-Cooling-Environment-Monitor](https://github.com/SohelHossain1218/Smart-IoT-Data-Center-Cooling-Environment-Monitor) | Prototype include | ESP8266 server-room monitoring and dual-AC control prototype with sensors, Telegram alerts, and hardware documentation. |
| [eeyx1/cooling-fan-predictive-maintenance-digital-twin](https://github.com/eeyx1/cooling-fan-predictive-maintenance-digital-twin) | Prototype include | Cooling fan digital twin and predictive maintenance prototype with ESP32/MQTT, BMS dashboard, ML pipelines, simulated validation, and feedback retraining. |
| [HyperYJ/ai-liquid-council](https://github.com/HyperYJ/ai-liquid-council) | Include in skills section | Agent skill for AI data center liquid-cooling technical/investment due diligence across cold plates, CDUs, manifolds, QDs, direct-to-chip, immersion, retrofit constraints, and deployment reality. |

## Kept With Low-Confidence Caveat

| Repository | Decision | Rationale |
| --- | --- | --- |
| [iaziz6/Digital-Twin-for-Data-Center-Cooling](https://github.com/iaziz6/Digital-Twin-for-Data-Center-Cooling) | Low-confidence candidate | Minimal README, but stated scope is physics-regularized 3D U-Net with uncertainty quantification for rack cooling. |
| [xiaodongwang991481/energy_saving](https://github.com/xiaodongwang991481/energy_saving) | Low-confidence candidate | Minimal README, but stated scope is machine-learning-based data center cooling energy saving. |
| [xenabmirza/magnetocaloric-thin-film-cooling](https://github.com/xenabmirza/magnetocaloric-thin-film-cooling) | Low-confidence candidate | No README fetched during review; repository description suggests magnetocaloric thin-film cooling for microchip and data center applications. |

## Other Reviewed Items And Caveats

| Repository | Decision | Rationale |
| --- | --- | --- |
| [AbdulrabDev/data-center-cooling-optimization](https://github.com/AbdulrabDev/data-center-cooling-optimization) | Keep in candidate queue | Numerical-analysis course project with simplified fan-speed cost model; useful but too simplified for main README until reviewed more deeply. |
| [sharmaankita3387/vedaCooling](https://github.com/sharmaankita3387/vedaCooling) | Keep in candidate queue | README only states AI-based predictive water reduction; not enough substance yet. |
| [LianLiTech/In-Rack-Coolant-Distribution-Unit](https://github.com/LianLiTech/In-Rack-Coolant-Distribution-Unit) | Include with vendor caveat | Hardware overview is directly relevant but mostly product/market material; included only as landscape orientation. |
| [LianLiTech/Data-Center-Liquid-Cooling-System](https://github.com/LianLiTech/Data-Center-Liquid-Cooling-System) | Include with vendor caveat | Product-oriented liquid cooling overview; included only as market/hardware orientation. |
| Quora Datacenter Cooling challenge repositories | Exclude | Algorithm challenge solutions are not data center cooling research tools. |
