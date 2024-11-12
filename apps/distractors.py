import os
# from sense2vec import Sense2Vec
# import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Get the base directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the model directory
# S2V_MODEL_PATH = os.path.join(BASE_DIR, 's2v_reddit_2019_lg')

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



# Path to your GloVe model (pre-trained embeddings)
GLOVE_MODEL_PATH = os.path.join(BASE_DIR, 'glove.6B.300d.txt')  # Adjust path if needed

# Load GloVe embeddings into a dictionary
def load_glove_model(glove_file_path):
    glove_model = {}
    with open(glove_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            values = line.split()
            word = values[0]
            vector = np.asarray(values[1:], dtype='float32')
            glove_model[word] = vector
    return glove_model

# Load GloVe model
glove_model = load_glove_model(GLOVE_MODEL_PATH)

# Function to get distractors based on GloVe
def get_distractors(word, glove_model):
    similarWords = set()  # Using a set to avoid duplicates
    word = word.lower()
    
    if word not in glove_model:
        return ['No distractors found']  # If word is not in GloVe model
    
    word_vector = glove_model[word]
    
    # Calculate cosine similarity between word_vector and all other vectors
    similarities = []
    for other_word, vector in glove_model.items():
        if other_word != word:  # Skip the original word
            sim = cosine_similarity([word_vector], [vector])[0][0]
            similarities.append((other_word, sim))
    
    # Sort by similarity and pick top 3
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Get the top 3 most similar words (but make sure they are not the same as the original word)
    for each_word, _ in similarities[:5]:  # Get more than 3 to ensure diversity
        similarWords.add(each_word)
    
    # Remove the original word from the distractors if it's present
    if word in similarWords:
        similarWords.remove(word)

    return list(similarWords)[:3]  # Return the first 3 distractors

# Example usage
distractors = get_distractors("dog", glove_model)
print(distractors)


if __name__ == '__main__':
#   print(get_distractors('Nepal', s2v))
    print(get_distractors('nepal',glove_model))
