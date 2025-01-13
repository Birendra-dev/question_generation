import nltk
from nltk.tokenize import sent_tokenize
from transformers import BartForConditionalGeneration, BartTokenizer

nltk.data.path.append('D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt', download_dir='D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')
    nltk.download('punkt_tab', download_dir='D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')
model_dir = "apps/bart-large-cnn"
summary_model = BartForConditionalGeneration.from_pretrained(model_dir)
summary_tokenizer = BartTokenizer.from_pretrained(model_dir)

def postprocesstext(content):
    final = ""
    for sent in sent_tokenize(content):
        sent = sent.capitalize()
        final += " " + sent
    return final.strip()

def summarizer(text, model, tokenizer):
    text = text.strip().replace("\n", " ")
    max_len = 512
    encoding = tokenizer.encode_plus(
        text,
        max_length=max_len,
        pad_to_max_length=False,
        truncation=True,
        return_tensors="pt",
    )

    input_ids, attention_mask = encoding["input_ids"], encoding["attention_mask"]

    outs = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        early_stopping=True,
        num_beams=3,
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        min_length=75,
        max_length=300,
    )

    dec = [tokenizer.decode(ids, skip_special_tokens=True) for ids in outs]
    summary = dec[0]
    summary = postprocesstext(summary)

    return summary.strip()
