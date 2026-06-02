import os
import sys

ziel_datei = "datei.txt"


#відкривання файлу по типу ос

if sys.platform == "win32":
    os.startfile(ziel_datei)   # тільки Windows
else:
    os.system("xdg-open " + ziel_datei)  # Linux / Mac


#методи
#.strip() - прибирає пробіли на початку і в кінці рядка