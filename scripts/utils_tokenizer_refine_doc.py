import tqdm
from joblib import Parallel, delayed
from utils_dataset_clean import clean_sentence, end_char_transform, apply_transform, lang_codes, DICTS
from utils_dataset_custom_transforms import custom_word_transforms, custom_punct_transforms

path = '/home/asr/speech-datasets/indicvoices/intermediate/tokenizer_docs'

splitter_transform = {
    x:'\n' for x in end_char_transform.keys()
}

def clean_doc(lcode):
    doc_path = f'{path}/{lcode}.txt'
    with open(doc_path,'r') as reader:
        text = reader.read()
        text = str.translate(text,str.maketrans(splitter_transform)).splitlines()
    i = 0
    cleaned = []
    error = []
    for line in tqdm.tqdm(text):
        valid, final_sent, extras_return = clean_sentence(line,DICTS[lcode],custom_word_transforms.get(lcode,{}),custom_punct_transforms.get(lcode,{}),True)
        if valid and len(final_sent.split(' ')) > 2:
            i += 1
            cleaned.append(final_sent)
        else:
            error.append((extras_return[0],final_sent,line))
    with open(f'{doc_path.replace(".txt","_refined.txt")}','w') as writer:
        writer.write('\n'.join(cleaned))
    
    with open(f'{doc_path.replace(".txt","_errors.txt")}','w') as writer:
        for c, r, s in error:
            print(c,r,s,sep='\n',file=writer)
            print(file=writer)
            print(file=writer)
    
    
    print(lcode, len(cleaned), (i/len(text)) * 100)

if __name__ == '__main__':
    Parallel(n_jobs=-128)(
        delayed(clean_doc)(lcode) for lcode in lang_codes.values()
    )