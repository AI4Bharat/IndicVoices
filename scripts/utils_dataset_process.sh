TGZ_PATH=/home/asr/speech-datasets/indicvoices/intermediate/tgz
EXTRACT_PATH=/home/asr/speech-datasets/indicvoices/intermediate/data

cd $EXTRACT_PATH 

# # setting up the version
version=v4

extract (){
    echo $1 started
    tar -xf $1
    echo $1 done
    echo '--------'
}

resample (){
    find . -type f \( -wholename "*/${1}/*.wav" \) -print0 | xargs -0 -I {} -P 128 bash -c 'ffmpeg -y -loglevel error -hide_banner -i $1 -ar $2 -ac $3 "${1%.*}_${2}.wav" && rm $1 && mv "${1%.*}_${2}.wav" $1' -- {} 16000 1
}

resample_full (){
    find . -type f -name "*.wav" -print0 | xargs -0 -I {} -P 128 bash -c 'ffmpeg -y -loglevel error -hide_banner -i $1 -ar $2 -ac $3 "${1%.*}_${2}.wav" && rm $1 && mv "${1%.*}_${2}.wav" $1' -- {} 16000 1
}

# iterate over the tgz and extract
for f in $(ls ${TGZ_PATH}/*${version}_*.tgz)
do
    sleep 5
    extract $f &
done
wait

# downsample the audio
echo 'resampling started'
resample $version 
# resample_full
echo 'resampling completed'