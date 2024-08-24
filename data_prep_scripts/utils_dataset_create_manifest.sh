SOURCE=/home/asr/speech-datasets/indicvoices/train-data
DEST=/home/asr/speech-datasets/indicvoices/artifacts/manifests/train/
SCRIPT_PATH=/home/asr/speech-datasets/indicvoices/scripts

rm -r $DEST

mkdir -p ${DEST}/normalized
for l in $(ls ${SOURCE} --ignore 'manifests')
do
    sleep 2
    touch ${DEST}/normalized/train_${l,,}_indicvoices.json
    find ${SOURCE}/${l} -type f -wholename "*/train/*.json" -exec cat {} >> ${DEST}/normalized/train_${l,,}_indicvoices.json \; &

    sleep 2
    touch ${DEST}/normalized/valid_${l,,}_indicvoices.json
    find ${SOURCE}/${l} -type f -wholename "*/valid/*.json" -exec cat {} >> ${DEST}/normalized/valid_${l,,}_indicvoices.json \; &
    
done
wait

# rm -r ${DEST}/normalized/valid_all_langs_indicvoices.json
cat ${DEST}/normalized/valid_* > ${DEST}/normalized/valid_all_langs_indicvoices.json

# verbatim
mkdir -p ${DEST}/verbatim
python ${SCRIPT_PATH}/utils_dataset_create_verbatim_manifest.py $DEST

