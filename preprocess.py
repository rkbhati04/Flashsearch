import spacy

# Load the small English model
# We disable 'parser' and 'ner' to make it much faster since we only need tokenization
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

def preprocess(text):
    # 1. Create a spaCy 'Doc' object
    doc = nlp(text)
    
    # 2. Process tokens: 
    # - convert to lowercase (token.lower_)
    # - skip if it's punctuation (token.is_punct)
    # - skip if it's just whitespace (token.is_space)
    list_of_words = [
        token.lemma_.lower()      # Get the base form (lemma) and lowercase it
        for token in doc 
        if not token.is_punct     # Skip punctuation
        and not token.is_space    # Skip extra whitespace/newlines
        and not token.is_stop
    ]
    
    return list_of_words

