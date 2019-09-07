# Defines what exists and where it is 

import os
from pathlib import Path

root = Path(os.path.abspath(__file__)).parent.parent
interviewRoot = root/"interviews"
sources = {
    interviewRoot/"jess_hexsel.txt": [
        interviewRoot/"jess_hexsel.codes.cp.txt"
    ],
    interviewRoot/"smita_kolhatkar.txt": [
        interviewRoot/"smita_kolhatkar.codes.cp.txt"
    ],
    interviewRoot/"cara_stoneburner.txt": [
        interviewRoot/"cara_stoneburner.codes.cp.txt"
    ],
    interviewRoot/"chris_cuzsmal.txt": [
        interviewRoot/"chris_cuzsmal.codes.cp.txt",
        interviewRoot/"chris_cuzsmal.codes.mb.txt"
    ],
    interviewRoot/"emily_garrison.txt": [
        interviewRoot/"emily_garrison.codes.cp.txt"
    ],
    interviewRoot/"suz_antik.txt": [
        interviewRoot/"suz_antik.codes.cp.txt"
    ],
    interviewRoot/"suz_antik_2.txt": [
        interviewRoot/"suz_antik_2.codes.cp.txt"
    ],
    interviewRoot/"josh_paley.txt":[
        interviewRoot/"josh_paley.codes.cp.txt" 
    ],
    interviewRoot/"ken_dauber.txt":[
        interviewRoot/"ken_dauber.codes.cp.txt" 
    ],
    interviewRoot/"board_2017.txt":[
        interviewRoot/"board_2017.codes.cp.txt" 
    ],
    interviewRoot/"board_2018.txt":[
        interviewRoot/"board_2018.codes.cp.txt" 
    ],
}
codefiles = sum([cfs for source, cfs in sources.items()], [])
codebook = root/"codes.yaml"
