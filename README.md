
![NIRAD Logo](images/nirad.jpg)

# 🧠 N.I.R.A.D. – Network Interdiction Resilience Advanced Defense

**N.I.R.A.D.** is a tactical decision-support system designed for solving robust network interdiction problems using optimization and generative AI. It features both a CLI and a stylized GUI complete with sound and terminal aesthetics.

---

## 📂 Project Structure
nirad/ ├── images/ # UI icons ├── input/ # Network input files (e.g., network_test.txt) ├── static/ # GUI sound effects ├── feasibility_robust.py # Pyomo model: Feasibility robustness ├── max_flow.py # Pyomo model: Maximum flow ├── optimality_robust.py # Pyomo model: Optimality robustness ├── nirad_utils.py # Agents, LLM prompts, solver configs (GLPK) ├── nirad_CLI.py # Command-line interface ├── nirad_GUI.py # Streamlit GUI with sounds ├── README.md └── requirements.txt


---

## 📈 Input Format

Place your network file inside the `input/` folder. For example: `network_test.txt`

Each row in the file represents a link (arc) and follows the format:

node_i node_j capacity destruction_cost

- The **first** node listed in the file is treated as the **source**.
- The **last** node listed is treated as the **terminal**.

---

## 🧩 Optimization Models

All models are built in [Pyomo](http://www.pyomo.org/) and solved using the open-source **GLPK** solver.

- `max_flow.py`: Basic maximum flow problem
- `feasibility_robust.py`: Interdiction via feasibility robustness
- `optimality_robust.py`: Interdiction via optimality robustness

---

## 🧠 Intelligence Engine

The `nirad_utils.py` module includes:
- LLM-based agent reasoning
- Prompt templates
- Settings for model, solver, and output behavior

Currently supports **OpenAI** models and **GLPK** as the MILP solver.

---

## 🖥️ CLI Usage

Run the command-line interface with:

```bash
python nirad_CLI.py


🎛️ GUI Usage

The Streamlit GUI features:

    Terminal-style visuals

    Custom fonts

    Embedded tactical sound effects

Launch with:

python -m streamlit run nirad_GUI.py


📦 Installation

    1. Clone the repository

    2. Install dependencies:

    `pip install -r requirements.txt`

    3. Ensure glpsol (GLPK solver) is available on your system path.


📜 License

Released under the Apache 2.0 License.

    🛰️ "Infiltrate the graph. Eliminate uncertainty. Restore flow."
    — N.I.R.A.D.