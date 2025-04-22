![NIRAD Logo](images/nirad.jpg)

# 🧠 N.I.R.A.D. – Network Interdiction Resilience Advanced Defense

**N.I.R.A.D.** is a tactical decision-support system designed for solving robust network interdiction problems using optimization and generative AI. It features both a CLI and a stylized GUI complete with sound and terminal aesthetics.

---

## 📂 Project Structure

### **Directories**
- **`images/`**: Contains icons and other graphical assets used in the user interface.
- **`input/`**: Stores network input files required for simulations and analysis, such as `network_test.txt`.
- **`static/`**: Contains sound effects used in the GUI. All sound effects are free to use and sourced from [Mixkit](https://mixkit.co/).

### **Python Scripts**
- **`feasibility_robust.py`**: Implements the feasibility robustness model using Pyomo.
- **`max_flow.py`**: Implements the maximum flow model using Pyomo.
- **`optimality_robust.py`**: Implements the optimality robustness model using Pyomo.
- **`nirad_utils.py`**: Contains utility functions, including agent configurations, LLM prompts, and solver configurations (e.g., GLPK).
- **`nirad_CLI.py`**: Provides a command-line interface for interacting with N.I.R.A.D.
- **`nirad_GUI.py`**: Implements the graphical user interface using Streamlit, including sound effects for user interaction.

### **Other Files**
- **`README.md`**: This file, providing an overview of the repository and its components.
- **`requirements.txt`**: Lists the Python dependencies required to run the project.---

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

    4. Set-up your GOOGLE_API_KEY in the nirad_utils.py file for using Gemini (or the appropriate key if you replace the LLM)  


📜 License

Released under the Apache 2.0 License.

    🛰️ "Infiltrate the graph. Eliminate uncertainty. Restore flow."
    — N.I.R.A.D.