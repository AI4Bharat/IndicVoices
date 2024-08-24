
import glob
import sys
import os
import soundfile as sf
import json
import re
import tqdm
import string
import random
import shutil
import pandas as pd
from utils_dataset_clean import lang_codes, clean_sentence, DICTS
from utils_dataset_custom_transforms import custom_word_transforms, custom_punct_transforms
from joblib import Parallel, delayed

INPUT_DIR = sys.argv[1]
OUTPUT_DIR = sys.argv[2]

SANSKRIT_FIX = ['2251799813688787.flac','2251799813703859.flac','2251799813692126.flac','2251799813686641.flac','2251799813689309.flac','2251799813687387.flac','2251799813688849.flac','2251799813695281.flac','2251799813700347.flac','2251799813693904.flac','2251799813694067.flac','2251799813692501.flac','2251799813687140.flac','2251799813687139.flac','2251799813701729.flac','2251799813703394.flac','2251799813704618.flac','2251799813701291.flac','2251799813713054.flac','2251799813721409.flac','2251799813703924.flac','2251799813711477.flac','2251799813711166.flac','2251799813719392.flac','2251799813705621.flac','2251799813705100.flac','2251799813742679.flac','2251799813775563.flac','2251799813715967.flac','2251799813722635.flac','2251799813714326.flac','2251799813778244.flac','2251799813728160.flac','2251799813754112.flac','2251799813754751.flac','2251799813748855.flac','2251799813748925.flac','2251799813738717.flac','2251799813726449.flac','2251799813749284.flac','2251799813767792.flac','2251799813778379.flac','2251799813740695.flac','2251799813779121.flac','2251799813782048.flac','2251799813764160.flac','2251799813765836.flac','2251799813754272.flac','2251799813764044.flac','2251799813753052.flac','2251799813766111.flac','2251799813763171.flac','2251799813769405.flac','2251799813769535.flac','2251799813797565.flac','2251799813797849.flac','2251799813777793.flac','2251799813785588.flac','2251799813799195.flac','2251799813801380.flac','2251799813778125.flac','2251799813809190.flac','2251799813781817.flac','2251799813808453.flac','2251799813780039.flac','2251799813780551.flac','2251799813781070.flac','2251799813808513.flac','2251799813808704.flac','2251799813792616.flac','2251799813809482.flac','2251799813782159.flac','2251799813783153.flac','2251799813811254.flac','2251799813812522.flac','2251799813793750.flac','2251799813794518.flac']

def parse_json(json_path):
    # /home/asr/datasets/indicvoices_raw/Urdu/v1/train/0a1b8a86-11ca-432d-96e3-8fc1e1873bdc_0.json
    language=json_path.split('/')[-4]
    wav_path = json_path.replace('.json','.flac')
    # /home/asr/datasets/indicvoices_raw/Urdu/v1/train/0a1b8a86-11ca-432d-96e3-8fc1e1873bdc_0.flac
    with open(json_path) as reader:
        json_obj = json.load(reader)

    output_root, name = os.path.split(wav_path.replace(INPUT_DIR,OUTPUT_DIR))
    if name in SANSKRIT_FIX:
        json_obj['task_name'] = 'Digital Payment Commands'
    
    if json_obj['task_name'] == 'DOI - Fish Farming':
        json_obj['task_name'] = 'DOI - Animal Husbandry'

    output_wavs = f"{output_root}/audios"

    os.makedirs(output_wavs,exist_ok=True)
    output_wav_path=f'{output_wavs}/{name}'

    transcript_path=f"{output_root}/transcripts"
    extras_path=f"{output_root}/errors"
    # shutil.rmtree(extras_path,ignore_errors='*')
    os.makedirs(transcript_path,exist_ok=True)
    os.makedirs(extras_path,exist_ok=True)

    err_files = glob.glob(f'{extras_path}/{name.replace(".flac","*")}')
    if os.path.exists(f"{transcript_path}/{name.replace('.flac','.json')}") and len(err_files) == 0:
        return

    wav, sr = sf.read(wav_path)
    assert sr == 16000, 'Looks like audios are not sampled at 16Khz'
    file_jsons = []
    errors = []
    for e,(verbatim, normalized) in enumerate(zip(json_obj['verbatim'],json_obj['normalized'])):
        lang_id = lang_codes[language.lower()]
        start, end = int(max(verbatim['start'],0) * sr), int(verbatim['end']*sr)
        wav_patch = wav[start:end]

        vvalid, vtext, vextras = clean_sentence(verbatim['text'],DICTS[lang_id],custom_word_transform=custom_word_transforms.get(lang_id,{}),custom_punct_transform=custom_punct_transforms.get(lang_id,{}), extras=True)
        nvalid, ntext, nextras = clean_sentence(normalized['text'],DICTS[lang_id],custom_word_transform=custom_word_transforms.get(lang_id,{}),custom_punct_transform=custom_punct_transforms.get(lang_id,{}), extras=True)
        
        # get the chunk path ready and then decide whether to write a wav file or an error analysis
        chunk_path = f'{output_wav_path.replace(".flac",f"_chunk_{e+1}.flac")}'
        err_path = chunk_path.replace('/audios/','/errors/').replace('.flac','.err')
        if not (vvalid and nvalid):
            # if the segment has issues in the transcript, lets write it
            errors.append(
                (
                    err_path, 
                    vextras[0]|nextras[0],
                    f'VerbatimRefined: {vtext}', 
                    f'VerbatimSource: {verbatim["text"]}', 
                    f'NormalizedRefined: {ntext}',
                    f'NormalizedSource: {normalized["text"]}', 
                )
            )
            continue
        elif os.path.exists(err_path):
            print(err_path)
            os.remove(err_path)

        if end - start == 0 or verbatim['speaker_id'] == 1 or len(vtext) == 0 or len(ntext) == 0 or end - start > 30 * sr or end - start < 0.05 * sr: 
            continue
        sf.write(chunk_path,wav_patch,sr)
        file_jsons.append(json.dumps({
            'audio_filepath': chunk_path,
            'text': ntext,
            'duration': len(wav_patch)/sr,
            'lang': lang_id,
            'samples': len(wav_patch),
            'verbatim': vtext,
            'normalized': ntext,
            'speaker_id': json_obj['speaker_id'],
            'scenario' : json_obj['scenario'],
            'task_name' : json_obj['task_name'],
            'gender' : json_obj['gender'],
            'age_group' : json_obj['age_group'],
            'job_type' : json_obj['job_type'],
            'qualification' : json_obj['qualification'],
            'area' : json_obj['area'],
            'district' : json_obj['district'],
            'state' : json_obj['state'],
            'occupation' : json_obj['occupation'],
            'verification_report' : json_obj['verification_report'],
            'unsanitized_verbatim': verbatim['text'],
            'unsanitized_normalized': normalized['text'],
        }))
        
    if len(file_jsons) > 0:
        with open(f"{transcript_path}/{name.replace('.flac','.json')}",'w') as writer:
            writer.write('\n'.join(file_jsons))
            writer.write('\n')

    # print(errors)
    for fp, a, b, c, d, e in errors:
        with open(fp,'w') as writer:
            print(a,b,c,d,e,sep='\n',file=writer)
            print(file=writer)
            print(file=writer)


if __name__ == '__main__':
    data_type = sys.argv[3]
    assert data_type in ['train','test']
    if data_type == 'train':
        # OUTPUT_DIR='/home/asr/speech-datasets/indicvoices/train-data'
        jsons = glob.glob(f"{INPUT_DIR}/**/train/**/*.json",recursive=True) + glob.glob(f"{INPUT_DIR}/**/valid/**/*.json",recursive=True)
    else:
        # OUTPUT_DIR='/home/asr/speech-datasets/indicvoices/eval-data'
        jsons = glob.glob(f"{INPUT_DIR}/**/test/**/*.json",recursive=True)
        # jsons = glob.glob(f"{INPUT_DIR}/Bengali/v1/test/**/*.json",recursive=True)
    Parallel(n_jobs=-64,backend='multiprocessing')(
        delayed(parse_json)(j) for j in tqdm.tqdm(jsons)
    )
