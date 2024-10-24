import os
from sense2vec import Sense2Vec

# Get the base directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the model directory
S2V_MODEL_PATH = os.path.join(BASE_DIR, 's2v_old')

# Load Sense2Vec model using the absolute path
s2v = Sense2Vec().from_disk(S2V_MODEL_PATH)

def get_distractors(word, s2v):
    similarWords = []
    word = word.lower().replace(' ', '_')
    try:
        sense = s2v.get_best_sense(word)
        most_similar = s2v.most_similar(sense, n=4)
        for each_word in most_similar:
            similarWords.append(each_word[0].split("|")[0].replace("_", " "))
    except KeyError:
        return ['No distractors found']
    return similarWords


if __name__ == '__main__':
  print(get_distractors('Nepal', s2v))