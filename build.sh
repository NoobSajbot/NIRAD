!/usr/bin/env bash
# Install GLPK
apt-get update && apt-get install -y glpk-utils libglpk-dev

# Install Python packages
pip install -r requirements.txt
