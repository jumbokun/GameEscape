"""Build web/index.html: the canvas port of Escape with every asset inlined.

Usage: unzip Escape.zip, then  python web/build.py Escape/src
Needs fontTools (pip install fonttools) to repair Font2.ttf's broken 'M'/'W' widths.
"""
import base64, io, json, sys
from pathlib import Path
from fontTools.ttLib import TTFont

src = Path(sys.argv[1])  # the unzipped Escape/src
here = Path(__file__).parent

def uri(p, mime):
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()

def sound(name):
    for d in (src / "ToolKit", src.parent / "bin" / "ToolKit"):
        if (d / name).exists():
            return d / name
    raise FileNotFoundError(name)

images = {"MainBG": "MainBG", "HelpBG": "HelpBG", "GameBG": "GameBG", "player1": "player1", "player2": "player2",
          "mistake0": "mistake1", "mistake1": "mistake2", "mistake2": "mistake3", "mistake3": "mistake4",
          "bonus0": "bonus", "bonus1": "bonus1", "tip1": "tip1", "tip2": "tip2", "meme": "meme"}
img = {k: uri(src / "res/images" / f"{v}.png", "image/png") for k, v in images.items()}
snd = {k: uri(sound(f"{k}.wav"), "audio/wav") for k in ("ding", "pong")}

ft = TTFont(str(src / "res/fonts/Font2.ttf"))
for name, (adv, lsb) in list(ft["hmtx"].metrics.items()):
    if adv > 5000:  # 'M' and 'W' store -1613 as an unsigned 63923
        ft["hmtx"].metrics[name] = (1280, lsb)
buf = io.BytesIO()
ft.save(buf)
font = base64.b64encode(buf.getvalue()).decode()

body = (here / "template.html").read_text(encoding="utf-8")
body = body.replace("__IMG_JSON__", json.dumps(img)).replace("__SND_JSON__", json.dumps(snd)).replace("__FONT2__", font)
page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '</head>\n<body>\n' + body + '\n</body>\n</html>\n')
(here / "index.html").write_text(page, encoding="utf-8")
print("wrote", here / "index.html", len(page) // 1024, "KB")
