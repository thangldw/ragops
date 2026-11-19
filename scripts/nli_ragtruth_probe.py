"""Probe: off-the-shelf NLI models vs lexical grounding on RAGTruth (needs torch, transformers).

    python scripts/nli_ragtruth_probe.py MODEL N QA|Summary   (data layout as in ragtruth_benchmark.py)
"""
import json
import random
import sys
import time

import torch

sys.path.insert(0,'scripts'); sys.path.insert(0,'src')
from ragtruth_benchmark import auroc
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from ragops.evaluators import lexical_groundedness, split_sentences
from ragops.models import EvalCase, RecordedResponse

name=sys.argv[1]; n=int(sys.argv[2]); task=sys.argv[3]
tok=AutoTokenizer.from_pretrained(name); model=AutoModelForSequenceClassification.from_pretrained(name).eval()
ent=[i for i,l in model.config.id2label.items() if l.lower().startswith('entail')][0]
D=sys.argv[4]+'/' if len(sys.argv)>4 else 'ragtruth/'
src={}
for l in open(D+'source_info.jsonl'):
    r=json.loads(l)
    if r['task_type']==task: src[r['source_id']]=r['source_info'] if task=='Summary' else r['source_info'].get('passages','')
rows=[json.loads(l) for l in open(D+'response.jsonl')]
rows=[r for r in rows if r['split']=='test' and r['source_id'] in src and r.get('quality')=='good']
random.Random(1).shuffle(rows); rows=rows[:n]
def chunks(text, size=180, stride=120):
    w=text.split() 
    return [' '.join(w[i:i+size]) for i in range(0,max(len(w)-size+stride,1),stride)] or ['']
def entail(prem_list, hyp):
    best=0.0
    for i in range(0,len(prem_list),8):
        enc=tok(prem_list[i:i+8],[hyp]*len(prem_list[i:i+8]),truncation=True,max_length=400,padding=True,return_tensors='pt')
        with torch.no_grad(): p=model(**enc).logits.softmax(-1)[:,ent]
        best=max(best,float(p.max()))
    return best
t=time.time(); nli=[]; lex=[]; lab=[]
for r in rows:
    ch=chunks(src[r['source_id']]); sents=split_sentences(r['response'])[:12]
    s=min((entail(ch,x) for x in sents), default=0.0)
    nli.append(s); lab.append(int(not r['labels']))
    lex.append(lexical_groundedness(EvalCase('x','',(src[r['source_id']],),()),RecordedResponse('x',r['response'],(),0,0)))
print(task,'n',len(rows),'halluc',len(rows)-sum(lab),'secs',round(time.time()-t))
print('AUROC nli(min-sentence)',round(auroc(nli,lab),4),'lexical',round(auroc(lex,lab),4))
