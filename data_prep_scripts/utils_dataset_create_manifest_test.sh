SOURCE=/home/asr/speech-datasets/indicvoices/eval-data
DEST=/home/asr/speech-datasets/indicvoices/artifacts/manifests/test/
SCRIPT_PATH=/home/asr/speech-datasets/indicvoices/scripts

rm -r $DEST

mkdir -p ${DEST}/normalized
for l in $(ls ${SOURCE} --ignore 'manifests')
do
    sleep 2
    touch ${DEST}/normalized/test_${l,,}_indicvoices.json
    find ${SOURCE}/${l} -type f -wholename "*/test/*.json" -exec cat {} >> ${DEST}/normalized/test_${l,,}_indicvoices.json \; &

done
wait

# rm -r ${DEST}/normalized/valid_all_langs_indicvoices.json
# cat ${DEST}/normalized/valid_* > ${DEST}/normalized/valid_all_langs_indicvoices.json

# verbatim
mkdir -p ${DEST}/verbatim
python ${SCRIPT_PATH}/utils_dataset_create_verbatim_manifest.py $DEST

