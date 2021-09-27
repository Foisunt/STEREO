from langdetect import detect
from langdetect import detect_langs

# Single language detection
text = "The level of sadness (t (584.85) =-3.85, P = 0.000) of participants from rural was significantly higher than that of participants from urban, while the anxiety of participants from urban (t (679.52) = 2.55, P = 0.009) and anger (t (802) = 3.04, P = 0.002) were significantly higher than participants in rural"
print("en"==detect("War doesn't show who's right, just who's left."))
print("de"==detect("Ein, zwei, drei, vier"))
print(detect(text))
print(detect("Доброе утро"))
print(detect("voulez vous manger avec moi"))


# language probabilities best match
print(detect_langs(text))