#!/bin/zsh

python GenerateProblems.py configs/ProblemSettings/dummy.yaml
python GenerateProblems.py configs/ProblemSettings/dummy_c1.yaml
python GenerateProblems.py configs/ProblemSettings/dummy_c3.yaml

python SolveProblems.py configs/SolveSettings/dummy.yaml
python SolveProblems.py configs/SolveSettings/dummy_c1.yaml
python SolveProblems.py configs/SolveSettings/dummy_c3.yaml
