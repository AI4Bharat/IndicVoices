import glob, json, sys, os

MANIFEST_ROOT=sys.argv[1]

assert os.path.exists(MANIFEST_ROOT), f'{MANIFEST_ROOT} does not exist'

normalized_manifests = glob.glob(f'{MANIFEST_ROOT}/**/normalized/**/*.json',recursive=True)

for manifest in normalized_manifests:
    with open(manifest) as reader:
        json_lines = [json.loads(x) for x in reader.read().strip().splitlines()]
    with open(manifest.replace('/normalized/','/verbatim/'),'w') as writer:
        for j in json_lines:
            j['text'] = j['verbatim']
            print(json.dumps(j),file=writer)
