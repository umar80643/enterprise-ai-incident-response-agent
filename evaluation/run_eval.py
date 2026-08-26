import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).parents[1]/"backend"))
from app.rag.chunking import ingest_tree
from app.rag.retrieval import hybrid_retrieve

root=Path(__file__).parents[1]
dataset=json.loads((root/"evaluation/datasets/incidents.json").read_text())
chunks=ingest_tree(root/"demo_repo")
for case in dataset:
    ranked=[c.file_path for c,_ in hybrid_retrieve(case["query"],chunks,5)]
    relevant=set(case["relevant_files"])
    hits=[i for i,p in enumerate(ranked,1) if p in relevant]
    precision=len(set(ranked)&relevant)/max(1,len(ranked))
    recall=len(set(ranked)&relevant)/len(relevant)
    mrr=1/min(hits) if hits else 0
    print(case["id"],{"Precision@5":round(precision,3),"Recall@5":round(recall,3),"MRR":round(mrr,3),"ranked":ranked})
