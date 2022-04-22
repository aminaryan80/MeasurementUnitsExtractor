from hazm import *

tagger = POSTagger(model='resources/postagger.model')

chunker = Chunker(model='resources/chunker.model')
tagged = tagger.tag(word_tokenize('علی کتاب را برداشت.'))
# print([x[1] for x in tagged if 'آمپر' in x[0]][0])
print(tagged)
a = tree2brackets(chunker.parse(tagged))

print(a)
