
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

INPUT_DIR='/home/asr/speech-datasets/indicvoices/intermediate/data'
OUTPUT_DIR=None
SANSKRIT_FIX = ['2251799813701291.wav','2251799813687139.wav','2251799813695281.wav','2251799813704618.wav','2251799813754751.wav','2251799813705100.wav','2251799813705621.wav','2251799813700347.wav','2251799813688849.wav','2251799813687387.wav','2251799813692126.wav','2251799813694067.wav','2251799813688787.wav','2251799813687140.wav','2251799813693904.wav','2251799813692501.wav','2251799813754272.wav','2251799813701729.wav','2251799813686641.wav','2251799813689309.wav','2251799813713054.wav','2251799813703394.wav','2251799813703924.wav','2251799813769405.wav','2251799813721409.wav','2251799813703859.wav','2251799813714326.wav','2251799813719392.wav','2251799813711477.wav','2251799813726449.wav','2251799813728160.wav','2251799813715967.wav','2251799813711166.wav','2251799813753052.wav','2251799813738717.wav','2251799813722635.wav','2251799813748925.wav','2251799813749284.wav','2251799813740695.wav','2251799813754112.wav','2251799813765836.wav','2251799813748855.wav','2251799813742679.wav','2251799813766111.wav','2251799813775563.wav','2251799813767792.wav','2251799813764160.wav','2251799813781817.wav','2251799813778125.wav','2251799813780551.wav','2251799813780039.wav','2251799813782159.wav','2251799813769535.wav','2251799813763171.wav','2251799813764044.wav','2251799813794518.wav','2251799813797565.wav','2251799813797849.wav','2251799813777793.wav','2251799813778244.wav','2251799813801380.wav','2251799813792616.wav','2251799813778379.wav','2251799813779121.wav','2251799813808453.wav','2251799813781070.wav','2251799813782048.wav','2251799813809190.wav','2251799813783153.wav','2251799813812522.wav','2251799813785588.wav','2251799813793750.wav','2251799813820023.wav','2251799813809482.wav','2251799813808704.wav','2251799813808513.wav','2251799813844117.wav','2251799813799195.wav','2251799813819496.wav','2251799813835187.wav','2251799813835729.wav','2251799813811254.wav']

def parse_json(json_path):
    # /home/asr/datasets/indicvoices_raw/Urdu/v1/train/0a1b8a86-11ca-432d-96e3-8fc1e1873bdc_0.json
    language=json_path.split('/')[-4]
    wav_path = json_path.replace('.json','.wav')
    # /home/asr/datasets/indicvoices_raw/Urdu/v1/train/0a1b8a86-11ca-432d-96e3-8fc1e1873bdc_0.wav
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

    err_files = glob.glob(f'{extras_path}/{name.replace(".wav","*")}')
    if os.path.exists(f"{transcript_path}/{name.replace('.wav','.json')}") and len(err_files) == 0:
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
        chunk_path = f'{output_wav_path.replace(".wav",f"_chunk_{e+1}.wav")}'
        err_path = chunk_path.replace('/audios/','/errors/').replace('.wav','.err')
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
        with open(f"{transcript_path}/{name.replace('.wav','.json')}",'w') as writer:
            writer.write('\n'.join(file_jsons))
            writer.write('\n')

    # print(errors)
    for fp, a, b, c, d, e in errors:
        with open(fp,'w') as writer:
            print(a,b,c,d,e,sep='\n',file=writer)
            print(file=writer)
            print(file=writer)


if __name__ == '__main__':
    data_type = sys.argv[1]
    assert data_type in ['train','test']
    if data_type == 'train':
        OUTPUT_DIR='/home/asr/speech-datasets/indicvoices/train-data'
        jsons = glob.glob(f"{INPUT_DIR}/**/train/**/*.json",recursive=True) + glob.glob(f"{INPUT_DIR}/**/valid/**/*.json",recursive=True)
    else:
        OUTPUT_DIR='/home/asr/speech-datasets/indicvoices/eval-data'
        jsons = glob.glob(f"{INPUT_DIR}/**/test/**/*.json",recursive=True)
        # jsons = glob.glob(f"{INPUT_DIR}/Bengali/v1/test/**/*.json",recursive=True)
    Parallel(n_jobs=-64,backend='multiprocessing')(
        delayed(parse_json)(j) for j in tqdm.tqdm(jsons)
    )
