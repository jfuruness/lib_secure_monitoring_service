#!/bin/bash
#SBATCH --partition=lo-core                   # Name of partition
#SBATCH --ntasks=150                            # Request Number of CPU cores
#SBATCH --mail-type=BEGIN,END,FAIL              # Event(s) that triggers email notification (BEGIN,END,FAIL,ALL)
#SBATCH --mail-user=reynaldo.morillo@uconn.edu  # Destination email address

# Setup python environment
source /home/rjm11010/miniconda3/etc/profile.d/conda.sh
conda activate v4sims

export PYTHONHASHSEED=0
python ../../python_scripts/artemis_main.py neustar 1
#python ../../python_scripts/artemis_main.py neustar 2  # Needs to be run
#python ../../python_scripts/artemis_main.py neustar 5  # Needs to be run
