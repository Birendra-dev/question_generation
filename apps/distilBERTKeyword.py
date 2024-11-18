import os
import numpy as np
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers.pipelines import TokenClassificationPipeline, AggregationStrategy
from peft import PeftConfig, PeftModel

base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of `t5distractors.py`
base_tokenizer_path = os.path.join(base_dir, "base-distilBERT", "tokenizer")
base_model_path = os.path.join(base_dir,"base-distilBERT", "model")
adapter_model_path = os.path.join(base_dir,"base-distilBERT", "adapter_model")

# Load PEFT configuration and base model
peft_config = PeftConfig.from_pretrained(adapter_model_path)
base_model = AutoModelForTokenClassification.from_pretrained(base_model_path)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_tokenizer_path)
tokenizer.pad_token = tokenizer.eos_token

# Load the fine-tuned adapter model and merge with the base model
peft_model = PeftModel.from_pretrained(base_model, adapter_model_path)
merged_model = peft_model.merge_and_unload()

# Custom pipeline for keyphrase extraction
class KeyphraseExtractionPipeline(TokenClassificationPipeline):
    def __init__(self, model, tokenizer, max_keywords=None, *args, **kwargs):
        super().__init__(model=model, tokenizer=tokenizer, *args, **kwargs)
        self.max_keywords = max_keywords

    def postprocess(self, model_outputs):
        # Process model outputs to extract unique keywords
        results = super().postprocess(model_outputs, aggregation_strategy=AggregationStrategy.FIRST)
        keywords = np.unique([result.get("word").strip() for result in results])

        # Sort by score if available
        if results and "score" in results[0]:
            keyword_scores = {result["word"].strip(): result["score"] for result in results}
            sorted_keywords = sorted(keyword_scores, key=keyword_scores.get, reverse=True)
        else:
            sorted_keywords = keywords

        # Limit keywords if max_keywords is specified
        if self.max_keywords is not None:
            sorted_keywords = sorted_keywords[:self.max_keywords]

        return sorted_keywords

# Function to extract keywords
def extract_keywords(text, num_keywords=None, device='cpu'):
    extractor = KeyphraseExtractionPipeline(
        model=merged_model,
        tokenizer=tokenizer,
        max_keywords=num_keywords,
        device=device
    )
    keyphrases = extractor(text)
    return keyphrases

if __name__ == "__main__":
    # Example text for extraction
    text = """
    Nepal is a landlocked country in South Asia, nestled between China to the north and India to the south, east, and west.
    Known for its stunning natural beauty, Nepal is home to eight of the world's ten highest mountains, including Mount Everest.
    """
    
    # Extract keywords
    keywords = extract_keywords(text, num_keywords=5)
    print("Keywords:", keywords)
    print(type(keywords))