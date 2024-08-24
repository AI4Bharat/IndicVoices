import glob, pandas as pd
import matplotlib.pyplot as plt
import tqdm, json
from joblib import Parallel, delayed

path="/home/asr/speech-datasets/indicvoices/artifacts/manifests/internal/"

jsons = glob.glob(f'{path}/**/*.json',recursive=True)

def process_json(j):
    with open(j) as reader:
        lines = reader.read().strip().splitlines()
    
    consider = []
    for l in lines:
        jobj = json.loads(l)
        if len(jobj['text']) <= 800:
            consider.append(l)

    with open(j,'w') as writer:
        print('\n'.join(consider),file=writer)

Parallel(n_jobs=-64,backend='multiprocessing')(
    delayed(process_json)(x) for x in tqdm.tqdm(jsons)
)