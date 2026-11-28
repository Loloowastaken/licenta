from fugashi import Tagger
from jreadability import compute_readability
from wordfreq import zipf_frequency
import re

#functii auxiliare

#fc care verifica daca e kanji 
# unicode intre 0x4E00 si 0x9FFF pt caractere chinezesti comune
# unicode intre 0x3400 si 0x4DBF pt caractere chinezesti mai rare
# pentru kanji japoneze conditia ramane aceeasi

def is_kanji(ch):
    ch_ord = ord(ch)
    return 0x4E00 <= ch_ord <= 0x9FFF or 0x3400 <= ch_ord <= 0x4DBF

#fc care da split la prop
# destul de self-explanatory, dau split cu un regex de punctuatii
def splitter(text):
    parts = re.split(r"[。！？!?\n]+",text) 
    return [p.strip() for p in parts if p.strip()]

#fc care curata campurile unidic
# folosim fugashi, deci ne intereseaza
# transformam campurile "*" in None, si am observat o chestie enervanta ca la anumite pronume pune un sufix
# e.g: 私-代名詞  君-代名詞 (代名詞/daimeishi = pronume); testat cu text3 in test.py

def clean(val):
    if not val or val == "*":
        return None
    return val.split("-")[0] 

#lista de leme 'irelevante'
# aici punem simboluri auxiliare/neauxiliare, spatii
# au fost identificate in test.py cu text3
punct_list = {"補助記号", "記号", "空白"}


#facem primul estimator
#acesta va lua un text, il va tokeniza si va identifica lungimea medie a propozitiilor
#si proportia kanji-urilor la caractere hiragana/katakana
def est_1(text,tagger):
    props = splitter(text)
    if not props:
        return {}
    ch_pe_prop = []
    tok_pe_prop = []
    total_ch = total_kanji = 0

    for p in props:
        chs = [c for c in p if not c.isspace()]
        ch_pe_prop.append(len(chs))
        total_ch+=len(chs)
        total_kanji+=sum(is_kanji(c) for c in chs)
        tok_pe_prop.append(sum(1 for word in tagger(p) if word.feature.pos1 not in punct_list))
    n = len(props)
    return{
        "nr_prop": n,
        "medie_ch_pe_prop": f"{(sum(ch_pe_prop)/n):.4f}",
        "medie_tok_pe_prop": f"{(sum(tok_pe_prop)/n):.4f}",
        "proportie_kanji": f"{(total_kanji/total_ch):.4f}" if total_ch else 0.0
    }

#al doilea estimator cu zipf_frequency
#conteaza sa eliminam si cuvinte auxiliare acum,
#si cand avem verburi vom lua forma din dictionar
#dar in loc de lemma, care converteste ce a fost scris in kanji automat
#folosim orthbase care pastreaza exact cum a fost scris in mod original
#de obicei se scrie あなた, nu 貴方
#vrem a doua forma DOAR daca asa scrie in text, dar lemma va face asta indiferent de text

#mai exista si cuv care nu apar in zipf_freq, astea trebuie tratate separat

aux_list = {"助動詞", "助詞"} #prep si verbe auxiliare
nume_nr_list = {"固有名詞", "数詞"} # nume proprii, numere

exclusion_list = punct_list | aux_list | nume_nr_list

def est_2(text, tagger, low_freq = 3.0):
    freqs = []
    for word in tagger(text):
        if word.feature.pos1 not in exclusion_list and word.feature.pos2 not in exclusion_list:
            extract_word = clean(word.feature.orthBase) or word.surface
            freq = zipf_frequency(extract_word,"ja")
            if freq == 0.0: #acum nu mai e necesar, dar las partea asta daca mai apar probleme din astea
                print("lipsa din wordfreq: ", repr(extract_word), word.feature.pos1, word.feature.pos2) 
            freqs.append(freq)
    n = len(freqs)
    existing_words = [f for f in freqs if f>0]
    return{
        "nr_cuv": n,
        "medie_frecv": f"{(sum(existing_words)/len(existing_words)):.4f}",
        "min_frecv": min(freqs),
        "propr_frecv_mica": f"{(sum(f<low_freq for f in freqs)/n):.4f}"
    }

            


tagger=Tagger()
#luam cinci texte, N5-N1 de pe Bunpro
# note: n4-n2 vin ca dialoguri, am decis sa scot cuvintele care indica cine vb (ca ar afecta proportia de kanji)
# am scos si ghilimele ca sunt mai greu de tratat momentan
text_N5 = "これは私の本です。これも私の本です。これは田中先生の本です。これも田中先生の本です。これは山田先生の本ですか。これはあなたの本です。これもあなたの本ですか。これはいい本です。これもいい本です。これもいい本ですか。"
text_N4 = "だんだん晴れてきたから散歩に行きましょう。どこでもいいです。外に出るだけで、気分が良くなります。みんなで行く？りさは私は眠い。って言ったよ。ソファは寝にくいからベッドに行ったよ。２人で行ってね。お母さんも行かないということだね。おやつを食べて行きましょう。お母さん、今度おやつの作り方を教えてください。自転車で行く？自転車で公園に行きましょう。ですが、公園の中では自転車に乗らないで押して行きましょう。子供らがいるから危険です。は〜い！"
text_N3 = "孝志、またゲームをしているの？ゲームをする前に時間を決めておくべきよ。分かった、決めとけばいいんだろ。二時間でやめるよ。もう…一日中しているんだから。全くやめる気配がないのよ！この一ヶ月は毎日ゲームばかりしてる。一日中ゲームをするべきではないわ。うるさい！なかなか集中できない。もう子供じゃないからほっといて！こらっ！！親の言うことに口答え？そんな息子に育てた覚えはありません。あなたのために言っているのよ。はいはい。分かった分かった。友達によると外でもゲームをしているそうだね。うん。家は集中できないから。ゲームってそんなにおもしろい？うん。ゲームは最高！人によるけどね。そっか。ゲームみたいに勉強にも関心を持つといいな。全く勉強しないからなかなか成績が上がらないわ。"
text_N2 = "もうすぐ選挙だけど、お父さんもう決めた？うん。決めたよ。お前も１８歳だから投票出来るけど、友達とそのような話はするのか？どうやら皆あまり興味がないんだ。選挙があることを知らない子もいるし…。その話題は諦めるよりほかないんだ。そうだよなー、高校を出てすぐに選挙って難しいよなー。まっ、きちんと調べてから投票するのがいいと思うよ。万が一質問があれば、聞いてくれ。でも、投票先の決定を僕に任せるのはダメだぞ。今の政党のままでもいいのかな？でも、コロナ対策も完璧に出来なければ意味がないし、オリンピックの不手際も多々あったし。今日本はコロナの感染者数が大変なことになっているよね。うんうん。もっと危機感を持って、ニュージーランドのように早めにロックダウンをするべきだったと思うよ。最近のニュースで見たけど、ニュージーランドは一人が新型コロナウイルス陽性と判定された時点で、全土で緊急ロックダウンを実施すると発表したよ。アーダーン首相は記者会見でこうした事態への対応は計画していた。断固とした早期の対策は、以前もうまく機能した。抑え込まないとどうなるか、私たちは他の国の例を見てきた。チャンスは１回しかない。と言っていたよ。今回もニュージーランドが日本のように感染拡大するのはあり得ないだろう。感染拡大を防ぐに相違ない。万が一感染が拡大したら、びっくりするよ。ニュージーランドを見習わざるを得ないよね。どうせ、日本の政府は見習わないだろうけど。ロックダウンをしたら経済が大変なことになるかもしれないけど、これ以上感染者数を増やさないためには必要なことだね。市民全員がきっちり守ると、ニュージーランドのように半年間誰も感染しない日々が続くなんてことにもなり得るよね！！これはニュージーランド政府の努力にほかならないよね。政治家は、しっかりと国民の声に耳を傾け、国民のために尽くしえる人、実行力があって国民にちゃんと目を向けてくれる人がふさわしい。でもさ、どうせ日本は選挙の時は一応そう言っておいて、終わると自分の保身のことばかり考えたり他人任せにしたりする政治家もいる…。そんな人は信頼し得ないよね。せめて正直でいてほしいよ。期待しようがないんだもの。本当に、期待できっこない。この気持ちは彼らのせいにほかならないさ。僕らに期待させられるものなら、そうしてほしいよ！確かに目先の利益に目がくらんで私腹を肥やすことばかり考えている政治家が多いな。でも、若者も、将来のためにちゃんと考えて選挙をするよりほかないのさ。僕は政治を若者に任せたいさ。年寄りが中心にいたら現実は変わるまい。そうだね。一応投票をするよ。もしできるものなら、この現実を変えたいんだ。公民の授業の知識を活かして、投票先を決めるよ。"
text_N1 = "先月９４歳で亡くなった社会人類学者、中根千枝さんの若き日の冒険物語は映画の人気シリーズ「インディー・ジョーンズ」を彷彿とさせるようなスリルに満ちている。津田塾で英語を勉強中に終戦を迎え、その後、共学になった東大へ入学する。東洋文化研究所の助手をしていた１９５３年（昭和２８年）から３年間インドに滞在、１９５９年（昭和３４年）から１９６２年（昭和３７年）にかけてはイギリス、イタリア、その他シカゴ大学、ロンドン大学で研究を積む。研究テーマは未開民族の社会構造である。インドではゾウに乗り、トラやヒョウには何回も遭遇した。小さなヘビならまだしも、人間を丸呑みにするほど大きいヘビもいた。そのようなヘビには特に警戒し、目的の村では住み込みで調査を行った。つい最近まで首狩り族だった村にも行った。それは過去のことで今は行われていないといえども、村長の家には壁いっぱいの頭蓋骨があり、これにはさすがに驚いた。過去に何が行われていたのか、身を以て知ったのだ。数個ならまだしも、こんなに多いとは。まさに、インディー・ジョーンズ如きである。この研究は欧州の学会で高く評価され、各地で講演や研究発表を行った。日本の農村の調査に入ると、各地の共通性に目が向くようになった。寄り合いに代表されるタテの序列を基調とする集団行動である。大学の教授会で話を聞くにあって、その行動が寄り合いと同じだと気づく。つまり日本社会の特質ではないか。そんなアイディアから生まれたのが１００万部を超えるベストセラーになったタテ社会の人間関係である。高度成長期の謎を解く文献として、刊行から現在に至るまで多くの人に読まれている。タテ社会であるだけでなくヨコの関係が弱いために、日本では下層において孤独が深まるだろうとか、その本では格差社会の到来をも予言していた。"
texts = [text_N5, text_N4, text_N3, text_N2, text_N1]
i=0
for text in texts:
    i+=1
    print("Text nr: ", i, '\n',
          "JReadability: ", f"{compute_readability(text, tagger):.4f}",'\n', 
          "Estimator 1: ", est_1(text,tagger), '\n',
          "Estimator 2: ", est_2(text,tagger,3.0), '\n',
          sep='\t')

"""Text nr:        1
        JReadability:   5.1618
        Estimator 1:    {'nr_prop': 10, 'medie_ch_pe_prop': '9.6000', 'medie_tok_pe_prop': '6.3000', 'proportie_kanji': '0.2500'}
        Estimator 2:    {'nr_cuv': 30, 'medie_frecv': '5.9590', 'min_frecv': 5.3, 'propr_frecv_mica': '0.0000'}

Text nr:        2
        JReadability:   4.5642
        Estimator 1:    {'nr_prop': 16, 'medie_ch_pe_prop': '12.6250', 'medie_tok_pe_prop': '7.3125', 'proportie_kanji': '0.2475'}
        Estimator 2:    {'nr_cuv': 61, 'medie_frecv': '5.2166', 'min_frecv': 2.89, 'propr_frecv_mica': '0.0492'}

Text nr:        3
        JReadability:   4.8883
        Estimator 1:    {'nr_prop': 27, 'medie_ch_pe_prop': '11.3704', 'medie_tok_pe_prop': '6.5185', 'proportie_kanji': '0.1922'}
        Estimator 2:    {'nr_cuv': 92, 'medie_frecv': '5.5115', 'min_frecv': 2.45, 'propr_frecv_mica': '0.0217'}

Text nr:        4
        JReadability:   3.8987
        Estimator 1:    {'nr_prop': 46, 'medie_ch_pe_prop': '23.8043', 'medie_tok_pe_prop': '13.7609', 'proportie_kanji': '0.2740'}
        Estimator 2:    {'nr_cuv': 329, 'medie_frecv': '5.3086', 'min_frecv': 1.48, 'propr_frecv_mica': '0.0243'}

Text nr:        5
        JReadability:   3.1130
        Estimator 1:    {'nr_prop': 20, 'medie_ch_pe_prop': '36.9500', 'medie_tok_pe_prop': '21.5000', 'proportie_kanji': '0.3396'}
        Estimator 2:    {'nr_cuv': 218, 'medie_frecv': '5.0635', 'min_frecv': 1.21, 'propr_frecv_mica': '0.0367'}"""

#Observatii legate de est1:
#observatie interesanta este ca textul N3 cumva a iesit mai usor decat N4. posibil sa fie o problema cu resursa
#defapt, estimatorul 1 zice ca N3 este cel mai usor text de aici daca ne luam dupa proportia de kanji
#de asemenea observam slabiciune din prima, textele scurte precum N5 au un avantaj disproportionat (la proportia de kanji)
#daca ne luam dupa media de caractere si tokenuri, N4 si N3 ies peste N5, N3 tot ramane sub N4
#totusi, fiind atat de mic sample sizeul momentan e normal sa apara chestii din astea
#jreadability si el marcheaza textul N3 ca fiind mai usor = asta macar e un mic sanity check

#Observatii legate de est2:
#textul N4 a iesit mai greu decat N3 si N2. la asta nu ma asteptam
#posibil motiv este ca sunt dialoguri, se folosesc cuvinte conversationale mult mai frecvente
#dar N4 este disproportionat de greu chiar si asa, are cea mai mare proportie de cuv cu frecv mica
#alt motiv este ca nu luam gramatica in considerare
#pentru a confirma daca este o problema cu masura sau nu va trebui sa imi aleg textele mai bine, cred

#cum ordoneaza fiecare estimator (<< indica o diferenta mare, ce e 'mare' e un pic subiectiv)
#ordine jreadability: N5 < N3 < N4 << N2 << N1
#ordine estimator_1 (prop kanji): N3 << N4 < N5 < N2 < << N1
#ordine estimator_1 (medie caractere): N5 < N3 < N4 << N2 << N1
#ordine estimator_2 (medie frecventa): N5 < N3 < N2 < N4 < N1
#ordine estimator_2 (prop cuv cu frecv mica i.e. <3.0.): N5 < N3 < N2 < N1 < N4

#to-do: estimator 3 (cursant simulat wanikani)
#to-do: sa gasesc o baza de texte mai buna pt testare