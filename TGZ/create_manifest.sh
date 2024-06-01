SOURCE=$1
DEST=${SOURCE}/manifests

rm -r $DEST

mkdir -p $DEST
for l in $(ls ${SOURCE} --ignore 'manifests')
do
    sleep 2
    touch ${DEST}/train_${l,,}_indicvoices.json
    find ${SOURCE}/${l} -type f -wholename "*/train/*.json" -exec cat {} >> ${DEST}/train_${l,,}_indicvoices.json \; &

    sleep 2
    touch ${DEST}/valid_${l,,}_indicvoices.json
    find ${SOURCE}/${l} -type f -wholename "*/valid/*.json" -exec cat {} >> ${DEST}/valid_${l,,}_indicvoices.json \; &
    
done
wait
