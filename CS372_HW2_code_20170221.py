import csv
from nltk.corpus import wordnet as wn
from nltk.corpus import brown

manual = ['remarkably','very', 'real','really','quite', 'absolutely', 'rather', 'immensely', 'distinctly', 'greatly', 'unbelievably','completely']
stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]

adverbs = dict() #assume # only modify adjectice
adjectives = dict() #only modify noun
capture_list = []
result = []

class Capture(): #save the compound in this class
    def __init__(self,intensifier,modi,count,score = 0):
        self.intensifier = intensifier
        self.modi = modi
        self.count = count
        self.score = score

"""similarity function"""

def similarity_nouns(a,b): # calculate the similarity of two noun
    similarity = 0
    lemmas_a = wn.synsets(a)
    lemmas_b = wn.synsets(b)
    if a == b:
        return 1
    if len(lemmas_a) == 0 or len(lemmas_b) == 0:
        return 0
    for la in lemmas_a:
        for lb in lemmas_b:
            sim = wn.wup_similarity(la,lb)
            if  sim != None and sim > similarity:
                similarity = wn.wup_similarity(la,lb)
    if similarity == None:
        return 0

    return similarity

"""supplementally functions"""
def is_adj(word): #check whether word has adjective pos
    for w in wn.synsets(word):
        if w.pos() == 'a':
            return True
    return False

def is_adv(word): #check whether word has adverb pos
    for w in wn.synsets(word):
        if w.pos() == 'r':
            return True
    return False

def is_noun(word): #check whether word has adverb pos
    for w in wn.synsets(word):
        if w.pos() == 'n':
            return True
    return False

def adjective_to_noun(word): #change adverb to noun (can make error)
    lemma = []
    if wn.synsets(word) == None: return []

    for syn in wn.synsets(word): #get all the synsets form word which has pos = v
        for lem in syn.lemmas():
            if syn.name().split('.')[1] == 'r':
                lemma.append(lem)
    related_lemma = [(l, l.derivationally_related_forms()) for l in lemma] # get the related nouns with der~() function
    nouns_lemma = []
    for related_lemma in related_lemma:
        for lem in related_lemma[1]:
            if lem.synset().name().split('.')[1] == 'n': #select the nouns from related_lemma
                nouns_lemma.append(lem)

    names = [l.name() for l in nouns_lemma]
    result = [(w, float(names.count(w)) / len(names)) for w in set(names)]
    result.sort(key=lambda w: -w[1])
    if len(result) == 0:
        return None
    else: return result[0]

def is_intensifier(word): #check wheter word is intensifier or not
    sim = 0
    for w in manual:
        if w == word:
            return False
        for aq in wn.synsets(w):
            for bq in wn.synsets(word):
                s = wn.wup_similarity(aq, bq)
                if s != None and s > sim: sim = s
    if sim>0.3: return True
    else: False

def find_compounds(sent): #find the whole componds which compose the sentense
    for i in range(len(sent)-1): # find "adj+noun" or "adv+adj" form in the sentenses
        word =  sent[i]
        next_word = sent[i+1]
        if word in manual:
            continue
        if word in stopwords or next_word in stopwords: #handing stopwords
            continue
        if word[0].isupper() or next_word[0].isupper():
            continue
        if is_adj(word) and is_noun(next_word) and is_intensifier(word):
            if word in adjectives.keys(): #store the compounds in to dict
                dic = adjectives[word]
                if next_word in dic.keys():
                    dic[next_word] = dic[next_word] + 1
                else:
                    dic[next_word] = 1
            else:
                adjectives[word] = {next_word : 1}

        if is_adv(word) and is_adj(next_word) and is_intensifier(word):
            if word in adverbs.keys():  # store the compounds in to dict -
                dic = adverbs[word]
                if next_word in dic.keys():
                    dic[next_word] = dic[next_word] + 1
                else:
                    dic[next_word] = 1
            else:
                adverbs[word] = {next_word: 1}

def scoring(w,dic): #Scoring with only for apperance count -> docs 4번
    len = 0
    capture_list = []
    for word in dic.keys():
        len = len + dic[word] #sum the length of total usage of intensifier
        if dic[word] >1: capture_list.append(Capture(w,word,dic[word]))
    for cap in capture_list: #calculate the score
        cap.score = cap.count/len
    result.extend(capture_list) #concat captured list to result

def scoring_adj(w,dic): #calculate the score for nouns for on adjectives (수식된 명사들의 유사도로 점수를 메김)
    n = 0
    similarity_sum = 0
    word_board = []
    for word in dic.keys():
        n = n + dic[word] #sum the length of total usage of intensifier
        for i in range(dic[word]): word_board.append(word)

    if n ==1 : #one element in
        return None

    for i in range(n):
        for j in range(i+1,n):
            sim = similarity_nouns(word_board[i],word_board[j])
            similarity_sum = similarity_sum + sim
    cal = n*(n-1)/2
    score = similarity_sum/ cal

    for k in dic.keys():
        if dic[k] > 2: result.append(Capture(w,k,dic[k],score))  #concat captured list to result

def scoring_adv(w,dic): #calculate the score for nouns for on adverbs (수식된 형용사들의 유사도로 점수를 메김)
    n = 0
    similarity_sum = 0
    word_board = []
    for word in dic.keys():
        n = n + dic[word] #sum the length of total usage of intensifier
        for i in range(dic[word]):
            adj = adjective_to_noun(word)
            if adj == None:
                adj = ''
            word_board.append(adj)
    if n ==1 : #one element in
        return None

    for i in range(n):
        for j in range(i+1,n):
            sim = similarity_nouns(word_board[i],word_board[j])
            similarity_sum = similarity_sum + sim
    cal = n*(n-1)/2
    score = similarity_sum/ cal

    for k in dic.keys():
        if dic[k] > 1: result.append(Capture(w,k,dic[k],score))  #concat captured list to result

"""main part"""

sents = brown.sents(categories = ['adventure', 'belles_lettres', 'editorial', 'fiction', 'government', 'hobbies',
'humor', 'learned', 'lore', 'mystery', 'news', 'religion', 'reviews', 'romance',
'science_fiction']) #input nltk corpora
for s in sents: #scan and collect the compunds
    if len(s)>1: compounds = find_compounds(s)

for key in adjectives.keys(): #calculate the score for each compounds and store it
    scoring_adj(key,adjectives[key])

for key in adverbs.keys(): #calculate the score for each compounds and store it
    scoring_adv(key,adverbs[key])

result = sorted(result,key = lambda cap : cap.score, reverse = True)
for c in result:
    print(c.intensifier,c.modi,c.count,c.score)
out = []
for c in result:
    out.append((c.intensifier,c.modi))

f = open('CS372_HW2_output_20170221.csv','w',newline='')
wr = csv.writer(f)
wr.writerow(out[:100])
f.close()
