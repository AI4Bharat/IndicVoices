1. Extract the tar files so that TGZ folder and language specific folders are on similar level

2. Run the following command to downsample the audios to 16kHz

    ```find . -type f \( -name "*.wav" \) -print0 | xargs -0 -I {} -P 128 bash -c 'ffmpeg -y -loglevel warning -hide_banner -stats -i $1 -ar $2 -ac $3 "${1%.*}_${2}.wav" && rm $1 && mv "${1%.*}_${2}.wav" $1' -- {} 16000 1```

    You can alternatively run the following command if you want to downsample only files inside v3 directory

    ```find . -type f \( -wholename "*/v3/*.wav" \) -print0 | xargs -0 -I {} -P 128 bash -c 'ffmpeg -y -loglevel warning -hide_banner -stats -i $1 -ar $2 -ac $3 "${1%.*}_${2}.wav" && rm $1 && mv "${1%.*}_${2}.wav" $1' -- {} 16000 1```
    
3. Run ```create_indicvoices.py``` to build a chunked version of the IndicVoices. Please make sure to change the input and output paths in the script.

4. Run ```create_manifest.sh``` to create manifest files from the processed dataset. Please make sure to change the source and destination paths in the script.