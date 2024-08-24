INTERMEDIATE_ROOT=/home/asr/speech-datasets/indicvoices/intermediate/tokenizer_docs/

wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/asm_Beng.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/ben_Beng.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/brx_Deva.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/doi_Deva.txt
# wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/eng_Latn.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/gom_Deva.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/guj_Gujr.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/hin_Deva.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/kan_Knda.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/kas_Arab.txt
# wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/kas_Deva.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/mai_Deva.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/mal_Mlym.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/mar_Deva.txt
# wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/mni_Beng.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/mni_Mtei.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/npi_Deva.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/ory_Orya.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/pan_Guru.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/san_Deva.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/sat_Olck.txt
# wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/snd_Arab.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/snd_Deva.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/tam_Taml.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/tel_Telu.txt
wget https://indic-trans.objectstore.e2enetworks.net/tok_data/sampled/urd_Arab.txt


mkdir -p $INTERMEDIATE_ROOT

mv asm_Beng.txt $INTERMEDIATE_ROOT/as.txt
mv ben_Beng.txt $INTERMEDIATE_ROOT/bn.txt
mv brx_Deva.txt $INTERMEDIATE_ROOT/brx.txt
mv doi_Deva.txt $INTERMEDIATE_ROOT/doi.txt
mv gom_Deva.txt $INTERMEDIATE_ROOT/kok.txt
mv guj_Gujr.txt $INTERMEDIATE_ROOT/gu.txt
mv hin_Deva.txt $INTERMEDIATE_ROOT/hi.txt
mv kan_Knda.txt $INTERMEDIATE_ROOT/kn.txt
mv kas_Arab.txt $INTERMEDIATE_ROOT/ks.txt
mv mai_Deva.txt $INTERMEDIATE_ROOT/mai.txt
mv mal_Mlym.txt $INTERMEDIATE_ROOT/ml.txt
mv mar_Deva.txt $INTERMEDIATE_ROOT/mr.txt
mv mni_Mtei.txt $INTERMEDIATE_ROOT/mni.txt
mv npi_Deva.txt $INTERMEDIATE_ROOT/ne.txt
mv ory_Orya.txt $INTERMEDIATE_ROOT/or.txt
mv pan_Guru.txt $INTERMEDIATE_ROOT/pa.txt
mv san_Deva.txt $INTERMEDIATE_ROOT/sa.txt
mv sat_Olck.txt $INTERMEDIATE_ROOT/sat.txt
mv snd_Deva.txt $INTERMEDIATE_ROOT/sd.txt
mv tam_Taml.txt $INTERMEDIATE_ROOT/ta.txt
mv tel_Telu.txt $INTERMEDIATE_ROOT/te.txt
mv urd_Arab.txt $INTERMEDIATE_ROOT/ur.txt