import json

subjects = json.load(open("data/subjects.json",encoding="utf-8"))
assignments = json.load(open("data/assignments.json",encoding="utf-8"))

by_id = {s["id"]: s for s in subjects}
known = {} # caracter : stadiu SRS [i.e: 0-9, unde 0 = necunoscut si 9 = complet cunoscut]
for a in assignments:
    d = a["data"]
    s = by_id.get(d["subject_id"])
    if s and s["data"].get("characters"):
        known[s["data"]["characters"]] = d["srs_stage"]

def learner(level, stage=5): #estimare foarte generoasa momentan, un cursant la nivelul N stie totul inclusiv
    return {
        s["data"]["characters"]: stage
        for s in subjects
        if s["data"]["level"] <= level and s["data"].get("characters")
    }

