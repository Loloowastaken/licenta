from fugashi import Tagger
from jreadability import compute_readability

tagger = Tagger()
print(compute_readability("おはようございます!今日は天気がいいですね。", tagger))