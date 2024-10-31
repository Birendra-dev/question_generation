import os
import string
import traceback

import nltk
import pke
import spacy
from flashtext import KeywordProcessor
from nltk.corpus import stopwords

# Check if NLTK stopwords are already downloaded
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    print("Stopwords not found. Downloading...")
    nltk.download("stopwords")

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
