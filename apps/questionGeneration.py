import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

trained_model_path = 'apps/t5/model'
trained_tokenizer = 'apps/t5/tokenizer'

device = torch.device('cpu')

# Load the model and tokenizer
question_model = T5ForConditionalGeneration.from_pretrained(trained_model_path).to(device)  # Move model to device
question_tokenizer = T5Tokenizer.from_pretrained(trained_tokenizer)

def get_question(context, answer, model, tokenizer):
    text = "context: {} answer: {}".format(context, answer)
    encoding = tokenizer.encode_plus(text, max_length=384, pad_to_max_length=False, truncation=True, return_tensors="pt").to(device)  # Move input to device
    input_ids, attention_mask = encoding["input_ids"], encoding["attention_mask"]

    outs = model.generate(input_ids=input_ids,
                          attention_mask=attention_mask,
                          early_stopping=True,
                          num_beams=5,
                          num_return_sequences=1,
                          no_repeat_ngram_size=2,
                          max_length=72)

    # Decode generated outputs
    dec = [tokenizer.decode(ids, skip_special_tokens=True) for ids in outs]

    # Clean up the generated question
    Question = dec[0].replace("question:", "").strip()
    return Question
