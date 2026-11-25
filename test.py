from fugashi import Tagger
import nagisa
import os
from dotenv import load_dotenv
load_dotenv()

#nagisa testing
text='Pythonで簡単に使えるツールです'
words = nagisa.tagging(text) # ia cuvantul si rolul in propozitie (POS tag)
print(words)
print(words.words) #doar cuvant 
print(words.postags) #doar POS tag

#filtram prepozitii si cuv auxiliare
filter_words = nagisa.filter(text, filter_postags=['助詞', '助動詞'])
print(filter_words)

#luam doar substantive
extract_words = nagisa.extract(text, extract_postags=['名詞'])
print(extract_words)

#lista de stopwords
print(nagisa.stopwords)

#fugashi testing

tagger = Tagger('-Owakati')
text2 = "麩菓子は、麩を主材料とした日本の菓子"
text3 = "私、貴方、君、彼、彼女。! ?! ? @ - +　　　　ああああ" # pt a identifica lemele simbolurilor auxiliare, simbolurilor, spatiilor
tagger.parse(text2) # 麩 菓子 は 、麩 を 主材 料 と し た 日本 の 菓子
for word in tagger(text2):
    print(word, word.feature.lemma, word.pos, sep='\t')
tagger.parse(text3)
for word in tagger(text3):
    print(word, word.feature.lemma, word.pos, sep='\t') 




#testare ca vede tokenul wanikani
token = os.getenv("WANIKANI_TOKEN")
print(token is not None)
