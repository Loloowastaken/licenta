from wordfreq import zipf_frequency


#testare: cuvant in kanji apoi acelasi cuvant cu hiragana
#1. yakusoku = 'promise'
print(zipf_frequency('約束', 'ja')) #4.67
print(zipf_frequency('やくそく', 'ja')) #3.16

#2. nani = 'what'
print(zipf_frequency('何', 'ja')) #6.15
print(zipf_frequency('なに', 'ja')) #5.32

#3. anata = 'you'
print(zipf_frequency('貴方', 'ja')) #4.58
print(zipf_frequency('あなた', 'ja')) #5.66

#rezultatele sunt cele asteptate, primele doua se scriu de obicei cu kanji,
#se vede mai rar forma aceea pentru pronumele de persoana a II-a


