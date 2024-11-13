import os
# from sense2vec import Sense2Vec
# import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Get the base directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet as wn

def get_distractors(word):
    similarWords = set()  # Using a set to avoid duplicates
    for syn in wn.synsets(word):  # Retrieve synsets for the word
        for lemma in syn.lemmas():  # Get lemmas for each synset
            clean_word = lemma.name().replace('_', ' ')
            # Avoid adding the original word and keep distractors distinct
            if clean_word.lower() != word.lower() and clean_word not in similarWords:
                similarWords.add(clean_word)

    # If no distractors are found, return a message
    if not similarWords:
        return ['No distractors found']

    # Convert the set to a list and return the first 3 distinct distractors
    return list(similarWords)[:3]

# Construct the absolute path to the model directory

# ======================================================================================================================================
# S2V_MODEL_PATH = os.path.join(BASE_DIR, 's2v_old')

# # Load Sense2Vec model using the absolute path
# s2v = Sense2Vec().from_disk(S2V_MODEL_PATH)
# def get_distractors(word, s2v):
#     similarWords = set()  # Using a set to avoid duplicates
#     word = word.lower().replace(' ', '_')
#     try:
#         sense = s2v.get_best_sense(word)
#         most_similar = s2v.most_similar(sense, n=5)  # Get more similar words to ensure enough distinct options
#         for each_word in most_similar:
#             clean_word = each_word[0].split("|")[0].replace("_", " ")
#             similarWords.add(clean_word)  # Add to set, which ensures uniqueness
#     except KeyError:
#         return ['No distractors found']

#     # Remove the original word from the distractors if it's present
#     if word.replace('_', ' ') in similarWords:
#         similarWords.remove(word.replace('_', ' '))

#     # Convert the set back to a list and return the first 3 distinct distractors
#     return list(similarWords)[:3]
# if __name__ == '__main__':
#   print(get_distractors('Nepal', s2v))

# ===========================================================================================================================================/

# def get_distractors(word, s2v, max_retries=3):
#     """
#     Get distractors for a word using sense2vec with memory optimization and error handling.
#     """
#     similarWords = set()
#     word = word.lower().replace(' ', '_')
    
#     # Add memory optimization wrapper
#     try:
#         # Force garbage collection before heavy operations
#         import gc
#         gc.collect()
        
#         # Break if the word is too long or contains invalid characters
#         if len(word) > 100 or not word.replace('_', '').isalnum():
#             return ['No distractors found']
            
#         # Try to get sense with error handling and retry mechanism
#         for attempt in range(max_retries):
#             try:
#                 # Get the sense vector with a timeout
#                 sense = s2v.get_best_sense(word)
#                 if sense is None:
#                     return ['No distractors found']
                
#                 # Get similar words with memory-efficient approach
#                 most_similar = s2v.most_similar(sense, n=5)
                
#                 # Process results immediately to free memory
#                 for each_word in most_similar:
#                     clean_word = each_word[0].split("|")[0].replace("_", " ")
#                     if clean_word and clean_word != word.replace('_', ' '):
#                         similarWords.add(clean_word)
                
#                 # Break the retry loop if successful
#                 break
                
#             except KeyError:
#                 continue
#             except Exception as e:
#                 print(f"Error processing word '{word}': {str(e)}")
#                 return ['No distractors found']
#             finally:
#                 # Force garbage collection after heavy operations
#                 gc.collect()
        
#         # If we still don't have enough distractors
#         if len(similarWords) < 3:
#             return ['No distractors found']
            
#         # Convert set to list and return first 3 items
#         return list(similarWords)[:3]
        
#     except Exception as e:
#         print(f"Unexpected error processing word '{word}': {str(e)}")
#         return ['No distractors found']

# Helper function to batch process words
# def batch_process_distractors(words, s2v, batch_size=100):
#     """
#     Process distractors in batches to manage memory better
#     """
#     results = {}
    
#     for i in range(0, len(words), batch_size):
#         batch = words[i:i + batch_size]
#         for word in batch:
#             results[word] = get_distractors(word, s2v)
        
#         # Force garbage collection after each batch
#         gc.collect()
    
#     return results

# Usage in your view

# ================================================================================================================================================

# ======================================================================================================================================================================================
# Path to your GloVe model (pre-trained embeddings)
# GLOVE_MODEL_PATH = os.path.join(BASE_DIR, 'glove.6B.300d.txt')  # Adjust path if needed

# Load GloVe embeddings into a dictionary
# def load_glove_model(glove_file_path):
#     glove_model = {}
#     with open(glove_file_path, 'r', encoding='utf-8') as f:
#         for line in f:
#             values = line.split()
#             word = values[0]
#             vector = np.asarray(values[1:], dtype='float32')
#             glove_model[word] = vector
#     return glove_model

# # Load GloVe model
# glove_model = load_glove_model(GLOVE_MODEL_PATH)

# # Function to get distractors based on GloVe
# def get_distractors(word, glove_model):
#     similarWords = set()  # Using a set to avoid duplicates
#     word = word.lower()
    
#     if word not in glove_model:
#         return ['No distractors found']  # If word is not in GloVe model
    
#     word_vector = glove_model[word]
    
#     # Calculate cosine similarity between word_vector and all other vectors
#     similarities = []
#     for other_word, vector in glove_model.items():
#         if other_word != word:  # Skip the original word
#             sim = cosine_similarity([word_vector], [vector])[0][0]
#             similarities.append((other_word, sim))
    
#     # Sort by similarity and pick top 3
#     similarities.sort(key=lambda x: x[1], reverse=True)
    
#     # Get the top 3 most similar words (but make sure they are not the same as the original word)
#     for each_word, _ in similarities[:5]:  # Get more than 3 to ensure diversity
#         similarWords.add(each_word)
    
#     # Remove the original word from the distractors if it's present
#     if word in similarWords:
#         similarWords.remove(word)

#     return list(similarWords)[:3]  # Return the first 3 distractors

# # Example usage
# distractors = get_distractors("dog", glove_model)
# print(distractors)

# ===============================================================================================================================================================

    # print(get_distractors('nepal',glove_model))
