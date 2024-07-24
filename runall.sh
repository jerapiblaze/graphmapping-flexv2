#!/bin/zsh

python GenerateProblems.py -c configs/ProblemSettings/dummy.yaml
python GenerateProblems.py -c configs/ProblemSettings/dummy_c1.yaml
python GenerateProblems.py -c configs/ProblemSettings/dummy_c3.yaml

python SolveProblems.py -c configs/SolveSettings/dummy.yaml
python SolveProblems.py -c configs/SolveSettings/dummy_c1.yaml
python SolveProblems.py -c configs/SolveSettings/dummy_c3.yaml
