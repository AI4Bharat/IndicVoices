SOURCE=/home/asr/speech-datasets/indicvoices/artifacts/manifests/
DEST=/home/asr/speech-datasets/indicvoices/artifacts/manifests/internal/
SCRIPT_PATH=/home/asr/speech-datasets/indicvoices/scripts

rm -r $DEST

mkdir -p ${DEST}/normalized

for lang in assamese bengali bodo dogri gujarati hindi kannada kashmiri konkani maithili malayalam manipuri marathi nepali odia punjabi sanskrit santali sindhi tamil telugu urdu
do
    cat ${SOURCE}/train/normalized/train_${lang}_indicvoices.json > ${DEST}/normalized/train_${lang}_indicvoices.json
    cat ${SOURCE}/test/normalized/test_${lang}_indicvoices.json >> ${DEST}/normalized/train_${lang}_indicvoices.json
done

# copy the joint validation set
cp ${SOURCE}/train/normalized/valid_all_langs_indicvoices.json ${DEST}/normalized/valid_all_langs_indicvoices.json

# verbatim
mkdir -p ${DEST}/verbatim
python ${SCRIPT_PATH}/utils_dataset_create_verbatim_manifest.py $DEST

