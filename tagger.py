POS_TAGS = ("NOUN", "VERB", "ADJ", "ADV", "PRON", "DET", "ADP", "NUM", "CONJ", "PRT", ".", "X")


def load_corpus(path):
    taggedWords = {pt: list() for pt in POS_TAGS}  # dict of POS: list of words
    templates = []
    f = open(path)
    s = f.readline().replace("\n", "")
    while len(s) > 0:
        temp = []
        for d in s.split(" "):
            word, tag = d.split("=")
            taggedWords[tag].append(word)
            temp.append(tag)
        templates.append(temp)
        s = f.readline().replace("\n", "")

    f.close()
    return taggedWords, templates


TAGGED_WORDS, SENTENCE_TEMPLATES = load_corpus("src/brown_corpus.txt")