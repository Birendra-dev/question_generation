import nltk
from rake_nltk import Rake

# Set custom NLTK data path
nltk.data.path.append('D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')

# Ensure required nltk resources are available
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', download_dir='D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', download_dir='D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', download_dir='D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')


try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger_eng', download_dir='D:\\Files\\question_answering\\.venv\\Lib\\nltk_data')


def get_keywords_rake(content, num_keywords=4):
    """
    Extract keywords from the content using the RAKE algorithm.
    Returns sorted keywords without scores, prioritizing nouns and pronouns.
    """
    # Initialize Rake with specific parameters for consistency
    r = Rake(min_length=1, max_length=4)
    r.extract_keywords_from_text(content)
    
    # Get ranked phrases
    keywords = list(set(r.get_ranked_phrases()))
    
    # Filter to retain phrases with nouns or pronouns
    filtered_keywords = []
    for phrase in keywords:
        words = nltk.word_tokenize(phrase)
        pos_tags = nltk.pos_tag(words)
        
        # Keep the phrase if it has nouns (NN, NNS, NNP, NNPS) or pronouns (PRP, PRP$)
        if any(tag.startswith('NN') or tag.startswith('PRP') for word, tag in pos_tags):
            filtered_keywords.append(phrase)
    
    # Sort alphabetically for consistency
    filtered_keywords.sort()
    
    # Return top keywords based on num_keywords
    return filtered_keywords[:num_keywords]


# Sample text
texts = """There were two brothers; the older one was always mean to the younger one. 
The older one would chop firewood in the forest and sell it in the market. One day, 
he stumbled across a magical tree. The tree begged him not to cut him down and promised him golden apples in exchange. 
The older brother felt disappointed with the number of apples he received. He decided to cut down the tree anyway,
but the tree showered him with hundreds of needles. The boy was left lying on the forest ground in pain. 
His younger brother finally found him and carefully took out every needle. 
The older brother finally apologised for treating his brother badly. The magical tree saw this exchange. 
It decided to give them more golden apples."""


if __name__ == "__main__":
    # Extract keywords using RAKE
    keywords = get_keywords_rake(texts, num_keywords=5)
    print("Keywords:", keywords)
    print(type(keywords))