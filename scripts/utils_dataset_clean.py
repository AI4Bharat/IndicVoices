import re
import pandas as pd
import sys
import json
import tqdm
from utils_dataset_custom_transforms import custom_word_transforms, custom_punct_transforms

DICT_PATH='/home/asr/speech-datasets/indicvoices/artifacts/dictionaries'

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

DICTS = {
    x: set(pd.read_csv(f'{DICT_PATH}/{x}.dict.txt',sep=' ',header=None)[0].to_list()+[' ']) - set('|') for x in lang_codes.values()
}


noise_tags = [
    '<TV>','<animal>','<baby>','<baby_crying>','<baby_talking>','<barking>','<beep>',
    '<bell>','<bird_squawk>','<breathing>','<buzz>','<buzzer>','<child>','<child_crying>',
    '<child_laughing>','<child_talking>','<child_whining>','<child_yelling>','<children>',
    '<children_talking>','<children_yelling>','<chiming>','<clanging>','<clanking>','<click>',
    '<clicking>','<clink>','<clinking>','<cough>','<dishes>','<door>','<footsteps>','<gasp>',
    '<groan>','<hiss>','<hmm>','<horn>','<hum>','<inhaling>','<laughter>','<meow>','<motorcycle>',
    '<music>','<noise>','<nose_blowing>','<Persistent-noise-end>','<Persistent-noise-start>',
    '<phone_ringing>','<phone_vibrating>','<popping>','<pounding>','<printer>','<rattling>',
    '<ringing>','<rustling>','<scratching>','<screeching>','<sigh>','<singing>','<siren>',
    '<smack>','<sneezing>','<sniffing>','<Sniffle>','<snorting>','<squawking>','<squeak>',
    '<stammers>','<static>','<swallowing>','<talking>','<tapping>','<throat_clearing>','<thumping>',
    '<tone>','<tones>','<trill>','<tsk>','<typewriter>','<ugh>','<uhh>','<uh-huh>','<umm>',
    '<unintelligible>','<wheezing>','<whispering>','<whistling>','<yawning>','<yelling>'
]

unbrack_noise_tags = [x.strip('<>') for x in noise_tags]

noise_tags_transform = {
    f'[{k}]':v for k,v in zip(unbrack_noise_tags,noise_tags)
}

noise_tags_removal = dict(zip(noise_tags,['']* len(noise_tags)))

parenthesis_transform = {
        ')':']',
        '}':']',
        '(':'[',
        '{':'[',
        '[[':'[',
        ']]':']',
        '$$$':'',
        ']$':']'
        # ']]':']','))':')','}}':'}',
        # '[[':'[','((':'(','{{':'{',
        # '[': ' [', '(': ' (', '{': ' {',
        # ']': '] ', ')': ') ', '}': '} ',
        # '[ ': '[', '( ': '(', '{ ': '{',
        # ' ]': ']', ' )': ')', ' }': '}',
    }

puct_transform = {
    '-': ' ',
    '?': ' ',
    ',': ' ',
    '’': '\'',
    '‘': '\'',
    '📯': ' ',
    ':': ' ',
    '|': ' ',
    'ʼ': '\'',
    '"': ' ',
    '\\': ' ',
    '/': ' ',
    ';': ' ',
    '!': ' ',
    '–': ' ',
    '“': ' ',
    '`': '\'',
    '”':' ',
    '´':'\'',
    '‑':' ',
    ' ] ': ' ',
    ' [ ': ' ',
    '꫰': ' ' # comma in manipuri
}

end_char_transform = {
    '।': ' ', # devnagari
    '॥': ' ', # devnagari
    '৷': ' ', # bengali
    '᱾': ' ', # santali
    '᱿': ' ', # santali
    '꯫': ' ', # manipuri 
    '௤': ' ', # tamil
    '௥': ' ', # tamil dd
    '.': ' ',
    '۔': ' ',
}

joiner_transform = {
    '\u200b': '',
    '\u200c': '',
    '\u200d': '',
    '\u200e': '',
    '\u200f': ''
}

def get_rex1():
    return r'[\[\]]+[a-zA-Z0-9_+&.,@’`<>\'\-\s]*[\[\]]+'

def get_rex2():
    return r'[\[\]]+[a-zA-Z0-9_+&.,@’`<>\'\-\s]{2,}'

def get_rex3():
    return r'[a-zA-Z0-9_+&.,@’`<>\'\-\s]{2,}[\[\]]+'

def apply_transform_rex1(text):
    return re.sub(get_rex1(),' ',text)
    
def apply_transform_rex2(text):
    return re.sub(get_rex2(),' ',text)

def apply_transform_rex3(text):
    return re.sub(get_rex3(),' ',text)

def apply_transform(text, transform:dict):
    for s, t in transform.items():
        text = text.replace(s,t)
    return re.sub('\s+',' ', text).strip()


def validate_sentence(text, dictionary, custom_punct_transform={}):
    noise_removed_sent = apply_transform(text, noise_tags_removal)
    end_char_sent = apply_transform(noise_removed_sent, end_char_transform)
    punct_removed = apply_transform(end_char_sent, puct_transform)
    punct_removed = apply_transform(punct_removed, custom_punct_transform)

    extras = set(punct_removed) - dictionary
    valid = len(extras) == 0
    return punct_removed, noise_removed_sent, valid, extras

def clean_sentence(source_sent, dictionary, custom_word_transform={}, custom_punct_transform={}, extras=False):
    # Take care of parenthesis by removing extra spaces 
    sent = apply_transform(source_sent,parenthesis_transform)

    # change the joiners
    sent = apply_transform(sent,joiner_transform)

    # Transform the noise tag variations
    sent = apply_transform(sent,noise_tags_transform)

    # remove the noise tags, bracketed variations
    removal_rex1 = re.compile(get_rex1()) if extras else None
    matches1 = removal_rex1.findall(sent) if extras else []
    sent = apply_transform_rex1(sent)

    removal_rex2 = re.compile(get_rex2()) if extras else None
    matches2 = removal_rex2.findall(sent) if extras else []
    sent = apply_transform_rex2(sent)

    removal_rex3 = re.compile(get_rex3()) if extras else None
    matches3 = removal_rex3.findall(sent) if extras else []
    sent = apply_transform_rex3(sent)

    # removing redundant spaces
    sent = re.sub('\s+',' ', sent).strip()
    
    # extra word tranformations
    sent = apply_transform(sent,custom_word_transform)

    # validate and get the final sentence
    final_sent, noise_tags_removed, valid, extra_chars = validate_sentence(sent, dictionary,custom_punct_transform=custom_punct_transform)

    extras_return = (extra_chars, noise_tags_removed, matches1, matches2, matches3)

    return valid, final_sent, extras_return

if __name__ == '__main__':
    manifest_path = sys.argv[1]

    with open(manifest_path) as reader:
        lines = reader.read().strip().splitlines()
    
    refined_manifest = []
    total = 0
    useful = 0
    for line in tqdm.tqdm(lines):
        j_obj = json.loads(line)
        text = j_obj['text']
        lang_id = j_obj['lang']
        total += j_obj['duration']
        valid, text, _ = clean_sentence(text,DICTS[lang_id],custom_word_transform=custom_word_transforms.get(lang_id,{}),custom_punct_transform=custom_punct_transforms.get(lang_id,{}), extras=True)

        if valid:
            j_obj['text'] = text
            refined_manifest.append(json.dumps(j_obj))
            useful += j_obj['duration']
    
    with open(manifest_path.replace('.json','_filtered.json'),'w') as writer:
        print('\n'.join(refined_manifest),file=writer)
    
    print(
        f"{manifest_path.replace('.json','_filtered.json')} retained {round(useful/3600)} out of {round(total/3600)} hours"
        )