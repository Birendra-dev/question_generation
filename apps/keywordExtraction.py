import os
import string
import traceback

import nltk
import pke
import spacy
from flashtext import KeywordProcessor
from nltk.corpus import stopwords

# Set custom NLTK data path
nltk.data.path.append('D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')

# Ensure required nltk resources are available
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', download_dir='D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')

# Check if spaCy model is downloaded
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("spaCy model 'en_core_web_sm' not found. Downloading...")
    # Download spaCy model if not found
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


def get_nouns_multipartite(content):
    """
    Extract top-ranked noun phrases from the content using the MultipartiteRank algorithm.
    """
    out = []
    try:
        extractor = pke.unsupervised.MultipartiteRank()
        extractor.load_document(input=content, language="en", spacy_model=nlp)

        # Define parts of speech to include in candidates
        pos = {"PROPN", "NOUN"}

        # Build stoplist
        stoplist = list(string.punctuation)
        stoplist += ["-lrb-", "-rrb-", "-lcb-", "-rcb-", "-lsb-", "-rsb-"]
        stoplist += stopwords.words("english")

        # Candidate selection (the stoplist is not passed, could be added)
        extractor.candidate_selection(pos=pos)

        # Weighting candidates using random walk (MultipartiteRank)
        extractor.candidate_weighting(alpha=1.1, threshold=0.75, method="average")

        # Extract top 15 keyphrases
        keyphrases = extractor.get_n_best(n=15)

        # Append the phrases to the output list
        out = [val[0] for val in keyphrases]
    except Exception:
        traceback.print_exc()
        out = []

    return out


def get_keywords(originaltext, summarytext, num_keywords=4):
    """
    Extract keywords from original text and match them with the summary text.
    """
    # Extract keywords using the get_nouns_multipartite function
    keywords = get_nouns_multipartite(originaltext)
    print("Keywords (unsummarized):", keywords)

    # Use flashtext KeywordProcessor to search keywords in the summary text
    keyword_processor = KeywordProcessor()
    for keyword in keywords:
        keyword_processor.add_keyword(keyword)

    # Extract keywords found in the summary
    keywords_found = keyword_processor.extract_keywords(summarytext)
    keywords_found = list(set(keywords_found))  # Remove duplicates
    print("Keywords found in summary:", keywords_found)

    # Select important keywords that appear in both original and summarized text
    important_keywords = [keyword for keyword in keywords if keyword in keywords_found]

    # Return the top 4 important keywords
    return important_keywords[:num_keywords]

if __name__ == "__main__":
    # Sample text
    original_text = """There were two brothers; the older one was always mean to the younger one. 
    The older one would chop firewood in the forest and sell it in the market. One day, 
    he stumbled across a magical tree. The tree begged him not to cut him down and promised him golden apples in exchange. 
    The older brother felt disappointed with the number of apples he received. He decided to cut down the tree anyway,
    but the tree showered him with hundreds of needles"""
    summary_text = "Two brothers, older mean to younger. Older chops firewood, finds magical tree with golden apples. Disappointed, cuts tree, gets needles."

    # Extract keywords from the original text and summary
    keywords = get_keywords(original_text, summary_text, num_keywords=5)
    print("Keywords:", keywords)
    print(type(keywords))