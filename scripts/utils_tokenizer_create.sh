# Usage: bash run_tokenizer.sh <tokenizer_name> <vocab_size>
ROOT_PATH="/home/asr/speech-datasets/indicvoices/artifacts"
DOC_ROOT_PATH="/home/asr/speech-datasets/indicvoices/intermediate/tokenizer_docs"
tokenize (){
        op_path="${ROOT_PATH}/tokenizers/${1}_$2"
        rm -r "$op_path" 
        python /home/asr/model_training/nemo/runners/process_asr_text_tokenizer.py \
                --data_file="${DOC_ROOT_PATH}/${1}_refined.txt" \
                --data_root="$op_path" \
                --vocab_size=$2 \
                --tokenizer="spe" \
                --no_lower_case \
                --spe_type="bpe" \
                --spe_character_coverage=1 \
                --log
}
for lang in as bn brx doi kok gu hi kn ks mai ml mr mni ne or pa sa sat sd ta te ur;
do
tokenize $lang 256 &
done