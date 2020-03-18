import csv
import pandas as pd
from googletrans import Translator

translator = Translator()

with open('res/outages_20200317054006.csv') as f:
    all_lines = f.readlines()

translated_lines = []
while len(all_lines) > 0:
    original_chunk = all_lines[:20]
    translated_chunk = translator.translate(original_chunk)
    translated_lines.extend([t.text for t in translated_chunk])
    print(translated_lines[-20:])
    all_lines = all_lines[20:]

# print(translated_lines)

