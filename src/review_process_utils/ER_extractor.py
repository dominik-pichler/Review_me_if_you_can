import nltk
import spacy

# Ensure you have downloaded the necessary resources
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nlp = spacy.load("en_core_web_sm")

# Define keywords related to household or cleaning
household_keywords = {"broom", "vacuum", "mold", "dust", "bathroom", "detergent", "sponge", "cloth", "bucket"}


def extract_nouns(text):
    # Tokenize the text into sentences
    sentences = nltk.sent_tokenize(text)

    # Initialize a list to hold all nouns
    nouns = []

    # Iterate over each sentence
    for sentence in sentences:
        # Tokenize the sentence into words and tag them with part of speech
        words = nltk.word_tokenize(sentence)
        pos_tags = nltk.pos_tag(words)

        # Extract words that are tagged as nouns
        for word, pos in pos_tags:
            if pos.startswith('NN'):  # NN, NNS, NNP, NNPS are noun tags
                nouns.append(word)

    return nouns


def extract_nouns_and_adjectives(text):
    # Process the text with SpaCy
    doc = nlp(text)

    # Initialize a dictionary to hold nouns and their adjectives
    noun_adj_pairs = {}

    # Iterate over tokens in the document
    for token in doc:
        # Check if the token is a noun and in the household keywords
        if token.pos_ == "NOUN" and token.text.lower() in household_keywords:
            # Find adjectives modifying this noun
            adjectives = [child.text for child in token.lefts if child.dep_ == "amod"]
            noun_adj_pairs[token.text] = adjectives

    return noun_adj_pairs

# Example usage
text = "The quick brown fox jumps over the lazy dog."
nouns = extract_nouns(text)
print(nouns)