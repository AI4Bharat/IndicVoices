 
<p style="font-size: 24px;">
  <a href="https://arxiv.org/abs/2403.01926" style="text-decoration:none;">
    <img src="https://img.shields.io/badge/Paper-blue" alt="Paper" style="vertical-align: middle; height: 30px;">
  </a>
  <a href="https://ai4bharat.iitm.ac.in/indicvoices/" style="text-decoration:none;">
    <img src="https://img.shields.io/badge/Data-green" alt="Data" style="vertical-align: middle; height: 30px;">
  </a>
</p>

# IndicVoices

We present INDICVOICES, a dataset of natural and spontaneous speech containing a
total of 12000 hours of read (8%), extempore (76%) and conversational (15%) audio 
from 22563 speakers covering 208 Indian districts and 22 languages. Of these 12000 hours, 
3200 hours have already been transcribed, with a median of 122 hours
per language. Through this paper, we share our journey of capturing the cultural,
linguistic and demographic diversity of India to create a one-of-its-kind inclusive
and representative dataset. More specifically, we share an open-source blueprint
for data collection at scale comprising of standardised protocols, centralised tools,
a repository of engaging questions, prompts and conversation scenarios spanning
multiple domains and topics of interest, quality control mechanisms, comprehensive
transcription guidelines and transcription tools. We hope that this open source
blueprint will serve as a comprehensive starter kit for data collection efforts in
other multilingual regions of the world. Using INDICVOICES, we build IndicASR,
the first ASR model to support all the 22 languages listed in the 8th schedule of the
Constitution of India.

Explore and Download IndicVoices https://ai4bharat.iitm.ac.in/datasets/indicvoices 

IndicVoices paper - https://arxiv.org/abs/2403.01926

### Collection Platform
Kathbath is an open-source, crowdsourcing framework designed to facilitate the large-scale collection of audio data. It includes an Android frontend that allows users to easily complete microtasks on their phones. Kathbath is built on top of Karya, Microsoft's open-source crowdsourcing platform toolkit.
```
https://github.com/AI4Bharat/KathbathXBackend [Backend]
https://github.com/AI4Bharat/KathbathXFrontend [Frontend]
```


### Transcription Platform
Shoonya is an open source platform to annotate and label data at scale, built with a vision to enhance digital presence of under-represented languages in India. Shoonya offers support for multiple data types (Ex : parallel datasets, OCR, ASR, TTS etc) and labeling tasks (Ex : parallel datasets, OCR, ASR, TTS etc).
```
https://github.com/AI4Bharat/Shoonya
```


## IndicASR

### Checkpoint:
[IndicASR](https://indicconformer.objectstore.e2enetworks.net/models/indicvoices-no-ssl-acl.nemo): A multilingual model trained on IndicVoices.

### Data Preparation 
1. After [downloading](https://ai4bharat.iitm.ac.in/datasets/indicvoices) the data, extract the tar files so that TGZ folder and language specific folders are on similar level
    ```
    ROOT_FOLDER
     |- TGZ
     |- Assamese
     |- Nepali
     |- ...
     |- ...
     |- Kashmiri
    ```

3. Run the following command to downsample the audios to 16kHz. (Use $NCPUS to control the parallelism)

    ```bash
    find . -type f \( -name "*.wav" \) -print0 | xargs -0 -I {} -P $NCPUS bash -c 'ffmpeg -y -loglevel warning -hide_banner -stats -i $1 -ar $2 -ac $3 "${1%.*}_${2}.wav" && rm $1 && mv "${1%.*}_${2}.wav" $1' -- {} 16000 1
    ```

4. Run ```create_indicvoices.py``` to build a chunked version of the IndicVoices. 
    ```bash
     python create_indicvoices.py /path/to/input/directory /path/to/output/directory 
    ```
5.  Run ```create_manifest.sh``` to create manifest files from the processed dataset. 
    ```bash
     bash create_manifest.sh /path/to/folder/containing/language/wise/data/folders
    ```

### Model Training
1. Install [Nemo](https://github.com/AI4Bharat/NeMo)

2. Training command
   ```
   python ${RUNNER_PATH}/speech_to_text_hybrid_rnnt_ctc_bpe.py \
    --config-path=${CONFIG_PATH} \
    --config-name=${CONFIG_NAME} \
    trainer.devices=-1 \
    trainer.accelerator="gpu" \
    trainer.strategy="ddp_find_unused_parameters_true" \
    exp_manager.name=<exp_name> \
    exp_manager.wandb_logger_kwargs.name=<exp_name> \
    exp_manager.explicit_log_dir=$LOG_DIR 
   ```

3. Inference
   ```
   OMP_NUM_THREADS=64 python ${RUNNER_PATH}/transcribe_speech.py \
        model_path=$MODEL_PATH \
        dataset_manifest=$MANIFEST_PATH.json \
        output_filename=$SAVE_FILE_NAME \
        langid=$LANGID \
        batch_size=64 \
        compute_timestamps=False \
        compute_langs=False \
        cuda=$GPU_ID \
        amp=True \
        append_pred=False 
   ```


