import glob
import sys
import os
import soundfile as sf
import json
import re
import tqdm
import string
from joblib import Parallel, delayed
import argparse

parser = argparse.ArgumentParser(description="create chunked version of indicvoices")

parser.add_argument('INPUT_DIR', type=str, help='input directory containing all the wav files')
parser.add_argument('OUTPUT_DIR', type=str, help='output directory where chunked wavs and transcripts will be saved')

args = parser.parse_args()

INPUT_DIR=args.INPUT_DIR
OUTPUT_DIR=args.OUTPUT_DIR

SANSKRIT_FIX = ['2251799813688787.wav','2251799813703859.wav','2251799813692126.wav','2251799813686641.wav','2251799813689309.wav','2251799813687387.wav','2251799813688849.wav','2251799813695281.wav','2251799813700347.wav','2251799813693904.wav','2251799813694067.wav','2251799813692501.wav','2251799813687140.wav','2251799813687139.wav','2251799813701729.wav','2251799813703394.wav','2251799813704618.wav','2251799813701291.wav','2251799813713054.wav','2251799813721409.wav','2251799813703924.wav','2251799813711477.wav','2251799813711166.wav','2251799813719392.wav','2251799813705621.wav','2251799813705100.wav','2251799813742679.wav','2251799813775563.wav','2251799813715967.wav','2251799813722635.wav','2251799813714326.wav','2251799813778244.wav','2251799813728160.wav','2251799813754112.wav','2251799813754751.wav','2251799813748855.wav','2251799813748925.wav','2251799813738717.wav','2251799813726449.wav','2251799813749284.wav','2251799813767792.wav','2251799813778379.wav','2251799813740695.wav','2251799813779121.wav','2251799813782048.wav','2251799813764160.wav','2251799813765836.wav','2251799813754272.wav','2251799813764044.wav','2251799813753052.wav','2251799813766111.wav','2251799813763171.wav','2251799813769405.wav','2251799813769535.wav','2251799813797565.wav','2251799813797849.wav','2251799813777793.wav','2251799813785588.wav','2251799813799195.wav','2251799813801380.wav','2251799813778125.wav','2251799813809190.wav','2251799813781817.wav','2251799813808453.wav','2251799813780039.wav','2251799813780551.wav','2251799813781070.wav','2251799813808513.wav','2251799813808704.wav','2251799813792616.wav','2251799813809482.wav','2251799813782159.wav','2251799813783153.wav','2251799813811254.wav','2251799813812522.wav','2251799813793750.wav','2251799813794518.wav']

lang_codes = {
    'assamese' :'as',
    'bengali' :'bn',
    'bodo' :'brx',
    'dogri' :'doi',
    'gujarati' :'gu',
    'hindi' :'hi',
    'kannada' :'kn',
    'kashmiri' :'ks',
    'konkani' :'kok',
    'maithili' :'mai',
    'malayalam' :'ml',
    'manipuri' :'mni',
    'marathi' :'mr',
    'nepali' :'ne',
    'odia' :'or',
    'punjabi' :'pa',
    'sanskrit' :'sa',
    'santali' :'sat',
    'sindhi' :'sd',
    'tamil' :'ta',
    'telugu' :'te',
    'urdu' :'ur'
}

def refine_sentence(sentence):
    translator = {
        '॥' : ' ',
        '۔' : ' ',
        '।' : ' ',
        '‘' : '',
        '–' : ' ',
        '’' : ' ',
        'ʼ' : '',
        '°' : ' ',
        '¬' : ' ',
        'ۭ': ' ',
        '۪': ' ',
        '‑': ' ',
        '—': ' ',
        '\u200b' : '',
        '\u200c' : '',
        '\u200d' : '',
        '´': '',
        "," : '',
        '\u200e': '',
        '\u200f': '',
        '“': '',
        '”': '',
    } | {x:" " for x in (set(string.punctuation)-set(','))}
    # print(sentence)
    # ref_sent = sentence.translate(str.maketrans('', '', string.punctuation))
    ref_sent = str.translate(sentence,str.maketrans(translator))
    ref_sent = re.sub(r'[\s+]|[a-zA-Z]',' ',ref_sent) #Only for Indic Voices
    ref_sent = re.sub('\s+',' ',ref_sent)
    return ref_sent.strip()

def clean_text(text):
    cleaned_text = re.sub(r'\[[^\]]*\]|\([^)]*\)|\[[a-zA-Z]*\]|\([a-zA-Z]*\)|\[[^\]]*\]|\([^)]*\)|\[|\]', ' ', text)
    cleaned_text = refine_sentence(cleaned_text)
    return cleaned_text

def parse_json(json_path):
    # /home/asr/datasets/indicvoices_raw/Urdu/v1/train/0a1b8a86-11ca-432d-96e3-8fc1e1873bdc_0.json
    language=json_path.split('/')[-4]
    wav_path = json_path.replace('.json','.wav')
    # /home/asr/datasets/indicvoices_raw/Urdu/v1/train/0a1b8a86-11ca-432d-96e3-8fc1e1873bdc_0.wav
    with open(json_path) as reader:
        try:
            json_obj = json.load(reader)
        except:
            print(json_path)
            return
    output_root, name = os.path.split(wav_path.replace(INPUT_DIR,OUTPUT_DIR))
    if name in SANSKRIT_FIX:
        json_obj['task_name'] = 'Digital Payment Commands'
    output_wavs = f"{output_root}/audios"

    os.makedirs(output_wavs,exist_ok=True)
    output_wav_path=f'{output_wavs}/{name}'

    transcript_path=f"{output_root}/transcripts"
    os.makedirs(transcript_path,exist_ok=True)
    if os.path.exists(f"{transcript_path}/{name.replace('.wav','.json')}"):
        return

    wav, sr = sf.read(wav_path)
    assert sr == 16000, 'Looks like audios are not sampled at 16Khz'
    file_jsons = []
    for e,(verbatim, normalized) in enumerate(zip(json_obj['verbatim'],json_obj['normalized'])):
        start, end = int(max(verbatim['start'],0) * sr), int(verbatim['end']*sr)
        wav_patch = wav[start:end]
        vtext = clean_text(verbatim['text'])
        ntext = clean_text(normalized['text'])
        if end - start == 0 or verbatim['speaker_id'] == 1 or len(vtext) == 0 or len(ntext) == 0 or end - start > 30 * sr or end - start < 0.05 * sr: 
            continue
        chunk_path=f'{output_wav_path.replace(".wav",f"_chunk_{e+1}.wav")}'
        sf.write(chunk_path,wav_patch,sr)
        file_jsons.append(json.dumps({
            'audio_filepath': chunk_path,
            'text': ntext,
            'duration': len(wav_patch)/sr,
            'lang': lang_codes[language.lower()],
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
            'verification_report' : json_obj['verification_report']
        }))
        
    if len(file_jsons) > 0:
        with open(f"{transcript_path}/{name.replace('.wav','.json')}",'w') as writer:
            writer.write('\n'.join(file_jsons))
            writer.write('\n')



jsons=glob.glob(f"{INPUT_DIR}/*/**/*.json",recursive=True)
Parallel(n_jobs=-16,backend='multiprocessing')(
    delayed(parse_json)(j) for j in tqdm.tqdm(jsons)
)
