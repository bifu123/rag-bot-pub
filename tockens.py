import nltk


def count_tokens(text):
    try:
        tokens = nltk.word_tokenize(text)
    except:
        nltk.download('punkt')
        tokens = nltk.word_tokenize(text)
    return len(tokens)