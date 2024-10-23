import torch
import random
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize
from transformers import BartForConditionalGeneration, BartTokenizer

nltk.download('punkt_tab')  # Ensure this is downloaded


# Check if model directory exists, if not, download it from Hugging Face
model_dir = 'apps/bart-large-cnn'

# Check if GPU is available, otherwise use CPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

summary_model = BartForConditionalGeneration.from_pretrained(model_dir)
summary_tokenizer = BartTokenizer.from_pretrained(model_dir)

# Optional: Uncomment if you want reproducible results
# random.seed(42)
# np.random.seed(42)
# torch.manual_seed(42)
# torch.cuda.manual_seed_all(42)


def postprocesstext(content):
    final = ""
    for sent in sent_tokenize(content):
        sent = sent.capitalize()
        final += " " + sent
    return final.strip()

def summarizer(text, model, tokenizer):
    text = text.strip().replace("\n", " ")
    max_len = 512
    encoding = tokenizer.encode_plus(text, max_length=max_len, pad_to_max_length=False, truncation=True, return_tensors="pt").to(device)  # Move input to device

    input_ids, attention_mask = encoding["input_ids"], encoding["attention_mask"]

    outs = model.generate(input_ids=input_ids,
                          attention_mask=attention_mask,
                          early_stopping=True,
                          num_beams=3,
                          num_return_sequences=1,
                          no_repeat_ngram_size=2,
                          min_length=75,
                          max_length=300)

    dec = [tokenizer.decode(ids, skip_special_tokens=True) for ids in outs]
    summary = dec[0]
    summary = postprocesstext(summary)
    
    return summary.strip()
