# -*- coding: utf-8 -*-
"""Сборка iframe-страниц курса: хаб + слова/грамматика/история для 12 уроков."""
import os
import json
import glob
import random
import html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
SITE = os.path.join(ROOT, "site")

random.seed(42)

# ───────────────────────── загрузка данных ─────────────────────────
META = json.load(open(os.path.join(DATA, "meta.json"), encoding="utf-8"))
MODULES = [json.load(open(f, encoding="utf-8"))
           for f in sorted(glob.glob(os.path.join(DATA, "module*.json")))]
LESSONS = []
for m in MODULES:
    for l in m["lessons"]:
        l["module"] = m
        LESSONS.append(l)
BY_N = {l["n"]: l for l in LESSONS}

STEPIK_LINKS = {}
sl = os.path.join(DATA, "stepik_links.json")
if os.path.exists(sl):
    STEPIK_LINKS = json.load(open(sl, encoding="utf-8"))

def esc(s):
    return html.escape(str(s), quote=True)

# ───────────────────────── стили и скрипты ─────────────────────────
CSS = """
:root{--bg:#1a1428;--panel:#2a2142;--panel2:#241c3a;--gold:#d4af37;--gold2:#f0d060;
--text:#f0e8d8;--dim:#b8a8c8;--red:#c05050;--green:#5cb870;--blue:#5c8ad4;--cat:#e2943e;--dog:#c86a50;--whale:#5c8ad4}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;font-size:15px;line-height:1.5;padding:14px}
.wrap{max-width:960px;margin:0 auto}
.px{font-family:'Press Start 2P','Segoe UI',monospace}
header.top{display:flex;gap:14px;align-items:center;background:var(--panel);border:3px solid var(--gold);
border-radius:10px;padding:12px 16px;margin-bottom:12px;box-shadow:0 4px 0 rgba(0,0,0,.35)}
header.top img.char{width:84px;height:84px;image-rendering:pixelated;flex-shrink:0}
.bubble{background:var(--panel2);border:2px solid var(--dim);border-radius:10px;padding:10px 14px;position:relative;flex:1}
.bubble:before{content:'';position:absolute;left:-12px;top:50%;transform:translateY(-50%);
border:6px solid transparent;border-right-color:var(--dim)}
.tt{font-size:13px;line-height:1.6;color:var(--gold2);margin-bottom:6px}
.tt .sub{display:block;font-size:9px;color:var(--dim);margin-top:5px}
nav.tabs{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap}
nav.tabs a{color:var(--text);text-decoration:none;background:var(--panel);border:2px solid var(--dim);
border-radius:8px;padding:8px 12px;font-size:9px}
nav.tabs a.on{background:var(--gold);color:#241c3a;border-color:var(--gold2)}
nav.tabs a:hover{border-color:var(--gold)}
.panel{background:var(--panel);border:2px solid #4a3c68;border-radius:10px;padding:14px;margin-bottom:14px}
h2.sec{font-size:11px;color:var(--gold2);margin-bottom:10px;letter-spacing:1px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.card{background:var(--panel2);border:2px solid #4a3c68;border-radius:10px;padding:10px;text-align:center}
.card img{width:96px;height:96px;image-rendering:pixelated;border-radius:6px}
.card .en{font-family:'Press Start 2P',monospace;font-size:11px;color:var(--gold2);margin:8px 0 6px;word-break:break-word}
.card .ipa{color:var(--dim);font-size:12px}
.card .ru{font-size:13px;margin-top:4px}
.btn{cursor:pointer;background:var(--gold);color:#241c3a;border:none;border-radius:8px;padding:8px 14px;
font-family:'Press Start 2P',monospace;font-size:10px;box-shadow:0 3px 0 #8a6d1c}
.btn:active{transform:translateY(2px);box-shadow:none}
.btn.ghost{background:var(--panel2);color:var(--text);box-shadow:0 3px 0 #17112a;border:2px solid var(--dim)}
.snd{cursor:pointer;background:none;border:none;font-size:20px;line-height:1;margin-left:4px}
.rules li{margin:8px 0 8px 18px}
.rules b{color:var(--gold2)}
.ex{background:var(--panel2);border-left:4px solid var(--gold);border-radius:6px;padding:8px 12px;margin:8px 0;
display:flex;justify-content:space-between;gap:10px;align-items:center}
.ex .en{font-family:'Press Start 2P',monospace;font-size:10px;color:#fff}
.ex .ru{color:var(--dim);font-size:13px;text-align:right}
.quiz-q{margin:14px 0;padding:12px;background:var(--panel2);border-radius:8px}
.quiz-q .q{margin-bottom:10px;font-size:14px}
.opt{display:block;width:100%;text-align:left;margin:6px 0;padding:9px 12px;background:var(--panel);
color:var(--text);border:2px solid var(--dim);border-radius:8px;cursor:pointer;font-size:14px}
.opt:hover{border-color:var(--gold)}
.opt.ok{border-color:var(--green);background:#1d3324}
.opt.bad{border-color:var(--red);background:#3a1d22}
.opt:disabled{cursor:default;opacity:.85}
.why{margin-top:8px;color:var(--dim);font-size:13px;display:none}
.why.show{display:block}
.game-score{font-family:'Press Start 2P',monospace;font-size:11px;color:var(--gold2);margin-bottom:10px}
.game-img{width:140px;height:140px;image-rendering:pixelated;display:block;margin:0 auto 12px}
.game-opts{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px;max-width:520px;margin:0 auto}
.scene{margin:16px 0;background:var(--panel2);border:2px solid #4a3c68;border-radius:10px;padding:12px}
.scene img.pic{width:100%;max-width:640px;display:block;margin:0 auto 10px;border-radius:8px;image-rendering:pixelated}
.scene .label{font-size:12px;color:var(--dim);text-align:center;margin-bottom:8px}
.line{background:var(--panel);border-radius:8px;padding:10px 12px;margin:8px 0;display:flex;gap:10px;align-items:flex-start}
.line .entext{font-family:'Press Start 2P',monospace;font-size:10px;line-height:1.8;flex:1}
.line .rutext{color:var(--dim);font-size:13px;display:none;margin-top:6px}
.line.open .rutext{display:block}
.tr{cursor:pointer;background:var(--panel2);color:var(--dim);border:1px solid var(--dim);border-radius:6px;
font-size:10px;padding:5px 8px;white-space:nowrap}
.hub{position:relative;display:inline-block;width:100%}
.hub img{width:100%;image-rendering:pixelated;border-radius:8px;display:block}
.spot{position:absolute;transform:translate(-50%,-50%);width:34px;height:34px;border-radius:50%;
display:flex;align-items:center;justify-content:center;font-family:'Press Start 2P',monospace;font-size:12px;
color:#fff;text-decoration:none;border:3px solid #f5e8b8;box-shadow:0 0 0 2px #241a38,0 3px 6px rgba(0,0,0,.5);transition:transform .15s}
.spot:hover{transform:translate(-50%,-50%) scale(1.25);z-index:5}
.spot.cur{outline:3px solid #fff;animation:pulse 1.2s infinite}
@keyframes pulse{0%,100%{box-shadow:0 0 0 2px #241a38,0 0 0 0 rgba(255,255,255,.7)}50%{box-shadow:0 0 0 2px #241a38,0 0 0 8px rgba(255,255,255,0)}}
.chars3{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin-bottom:14px}
.chars3 .card{display:flex;gap:10px;text-align:left;align-items:center}
.chars3 img{width:72px;height:72px;flex-shrink:0}
.chars3 .nm{font-family:'Press Start 2P',monospace;font-size:10px;color:var(--gold2);margin-bottom:6px}
.chars3 .rl{font-size:12px;color:var(--dim)}
.legend{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}
.legend span{font-size:9px;font-family:'Press Start 2P',monospace;padding:6px 8px;border-radius:6px;color:#fff}
.letters{display:grid;grid-template-columns:repeat(auto-fill,minmax(96px,1fr));gap:8px}
.letters .card img{width:72px;height:72px}
.letters .card .en{font-size:9px}
.final{font-size:13px;color:var(--gold2);margin-top:10px}
.stepik{display:inline-block;margin:4px 6px 0 0;font-size:9px}
@media (max-width:640px){header.top{flex-direction:column;text-align:center}.bubble:before{display:none}
.cards{grid-template-columns:repeat(auto-fill,minmax(120px,1fr))}}
"""

JS = """
function pickVoice(){
  var vs = speechSynthesis.getVoices();
  return vs.filter(function(v){return /^en([-_]|$)/i.test(v.lang) && /US|GB/i.test(v.lang);})[0]
      || vs.filter(function(v){return /^en/i.test(v.lang);})[0] || null;
}
if ('speechSynthesis' in window) { speechSynthesis.onvoiceschanged = function(){}; }
function speak(text, btn, rate){
  if (!('speechSynthesis' in window)) return;
  var u = new SpeechSynthesisUtterance(text);
  u.lang = 'en-US'; u.rate = rate || 0.85;
  var v = pickVoice(); if (v) u.voice = v;
  var chars = document.querySelectorAll('img.char');
  chars.forEach(function(im){ im.src = im.getAttribute('data-talk'); });
  var done = false;
  function idle(){ if (done) return; done = true;
    chars.forEach(function(im){ im.src = im.getAttribute('data-idle'); });
    if (btn) btn.classList.remove('speaking'); }
  u.onend = idle; u.onerror = idle;
  if (btn) btn.classList.add('speaking');
  speechSynthesis.cancel();
  speechSynthesis.speak(u);
  setTimeout(idle, 15000);
}
function toggleRu(el){ el.closest('.line').classList.toggle('open'); }
function speakLine(btn, id){
  var t = document.getElementById(id).getAttribute('data-en');
  speak(t, btn, 0.8);
}
function speakAll(ids, btn){
  var texts = ids.map(function(i){ return document.getElementById(i).getAttribute('data-en'); });
  var i = 0;
  function next(){
    if (i >= texts.length) return;
    speak(texts[i], btn, 0.8);
    i++;
  }
  speak(texts[0], btn, 0.8); i = 1;
  var chk = setInterval(function(){
    if (!speechSynthesis.speaking){ clearInterval(chk); next(); }
  }, 300);
}
"""

GAME_JS = """
var WORDS = __WORDS__;
var order = [], idx = 0, score = 0;
function shuffle(a){ a = a.slice(); for (var i = a.length - 1; i > 0; i--){ var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
function startGame(){
  order = shuffle(WORDS).slice(0, 8); idx = 0; score = 0;
  document.getElementById('final').textContent = '';
  nextQ();
}
function nextQ(){
  if (idx >= order.length){
    var msg = score >= 7 ? 'Великолепно! Кот тобой гордится!' : score >= 5 ? 'Хорошо! Повтори карточки и попробуй ещё.' : 'Загляни в карточки и сыграй снова!';
    document.getElementById('final').textContent = 'Результат: ' + score + ' из ' + order.length + '. ' + msg;
    return;
  }
  var w = order[idx];
  var wrong = shuffle(WORDS.filter(function(x){ return x.en !== w.en; })).slice(0, 3);
  var opts = shuffle([w].concat(wrong));
  var box = document.getElementById('q');
  var h = '<div class="game-score">Слово ' + (idx + 1) + ' из ' + order.length + ' · Очки: ' + score + '</div>';
  h += '<img class="game-img" src="assets/words/' + w.img + '" alt="">';
  h += '<div class="game-opts">' + opts.map(function(o){
        return '<button class="opt" data-en="' + o.en.replace(/"/g, '&quot;') + '">' + o.en + '</button>';
      }).join('') + '</div>';
  box.innerHTML = h;
  box.querySelectorAll('.opt').forEach(function(b){
    b.onclick = function(){
      var ok = b.getAttribute('data-en') === w.en;
      if (ok){ score++; b.classList.add('ok'); } else {
        b.classList.add('bad');
        box.querySelectorAll('.opt').forEach(function(x){ if (x.getAttribute('data-en') === w.en) x.classList.add('ok'); });
      }
      speak(w.en);
      box.querySelectorAll('.opt').forEach(function(x){ x.disabled = true; });
      idx++;
      setTimeout(nextQ, 900);
    };
  });
}
startGame();
"""

QUIZ_JS = """
var QUIZ = __QUIZ__;
function renderQuiz(){
  var box = document.getElementById('quiz');
  var h = '';
  QUIZ.forEach(function(q, qi){
    h += '<div class="quiz-q"><div class="q">' + (qi + 1) + '. ' + q.q + '</div>';
    h += q.options.map(function(o, oi){
      return '<button class="opt" data-q="' + qi + '" data-o="' + oi + '">' + o + '</button>';
    }).join('');
    h += '<div class="why" id="why' + qi + '"></div></div>';
  });
  box.innerHTML = h;
  box.querySelectorAll('.opt').forEach(function(b){
    b.onclick = function(){
      var qi = +b.getAttribute('data-q'), oi = +b.getAttribute('data-o');
      var q = QUIZ[qi];
      var good = oi === q.correct;
      b.classList.add(good ? 'ok' : 'bad');
      if (!good){
        box.querySelector('[data-q="' + qi + '"][data-o="' + q.correct + '"]').classList.add('ok');
      }
      box.querySelectorAll('[data-q="' + qi + '"]').forEach(function(x){ x.disabled = true; });
      var why = document.getElementById('why' + qi);
      why.textContent = (good ? '✅ ' + q.ok + ' ' : '❌ ' + q.bad + ' ') + q.why;
      why.classList.add('show');
    };
  });
}
renderQuiz();
"""


def char_header(char_id, lesson, page_kind, total_ru):
    ch = META["characters"][char_id]
    idle = f"assets/chars/{char_id}_idle.png"
    talk = f"assets/chars/{char_id}_talk.png"
    mod = lesson["module"] if lesson else None
    title = f"Урок {lesson['n']}: {esc(lesson['title_ru'])}" if lesson else esc(META["town_ru"])
    sub = f"{esc(mod['title_ru'])} · {page_kind}" if mod else "Карта волшебного городка"
    link_stepik = ""
    if lesson and str(lesson["n"]) in STEPIK_LINKS:
        link_stepik = (f'<a class="btn ghost stepik" href="{esc(STEPIK_LINKS[str(lesson["n"])])}" target="_blank" rel="noopener">'
                       f"↗ Открыть урок на Stepik</a>")
    return f"""
<header class="top">
  <img class="char" src="{idle}" data-idle="{idle}" data-talk="{talk}" alt="{esc(ch['name'])}">
  <div class="bubble">
    <div class="tt px">{title}<span class="sub">{sub} · {esc(ch['name'])} — {esc(ch['role'])}</span></div>
    <div style="font-size:13px">{total_ru}</div>
    <div>{link_stepik}</div>
  </div>
</header>"""


def lesson_nav(n, active):
    items = [("index.html?lesson=%d" % n, "🏰 Карта"), (f"lesson-{n:02d}-words.html", "📖 Слова"),
             (f"lesson-{n:02d}-grammar.html", "⚔️ Грамматика"), (f"lesson-{n:02d}-story.html", "🐋 История")]
    links = "".join(
        f'<a href="{href}"{" class=on" if key == active else ""}>{label}</a>' for href, label, key in
        [(i[0], i[1], i[0].split("-")[-1].split(".")[0] if "lesson" in i[0] else "hub") for i in items])
    # проще: собираем заново
    links = ""
    for href, label in items:
        key = "hub" if href.startswith("index") else href.split("-")[-1].split(".")[0]
        cls = ' class="on"' if key == active else ""
        links += f'<a href="{href}"{cls}>{label}</a>'
    return f'<nav class="tabs">{links}</nav>'


def page(title, body, extra_js=""):
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
{body}
</div>
<script>{JS}</script>
{extra_js}
</body>
</html>"""


def word_img_url(w):
    if "num" in w:
        return f"assets/words/num_{w['num']}.png"
    return None


def slug(s):
    import re
    s = s.lower().strip().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def build_words_page(l):
    w_cards = []
    js_words = []
    if "letters" in l:
        for lt in l["letters"]:
            img = f"letter_{lt['letter']}.png"
            w_cards.append(f"""<div class="card"><img src="assets/words/{img}" alt="{esc(lt['word'])}">
<div class="en">{esc(lt['letter'])} · {esc(lt['word'])}</div>
<div class="ru">{esc(lt['ru'])}<button class="snd" onclick="speak('{esc(lt['word'])}',this)">🔊</button></div></div>""")
    for w in l.get("words", []):
        if "num" in w:
            img = f"num_{w['num']}.png"
            en = w["en"]
        elif "color" in w:
            img = f"{slug(w['en'])}.png"
            en = w["en"]
        elif "draw" in w:
            img = f"{slug(w['en'])}.png"
            en = w["en"]
        else:
            img = f"{slug(w['en'])}.png"
            en = w["en"]
        ipa = f'<div class="ipa">{esc(w["ipa"])}</div>' if w.get("ipa") else ""
        w_cards.append(f"""<div class="card"><img src="assets/words/{img}" alt="{esc(en)}">
<div class="en">{esc(en)}<button class="snd" onclick="speak('{esc(en)}',this)">🔊</button></div>
{ipa}<div class="ru">{esc(w['ru'])}</div></div>""")
        js_words.append({"en": en, "img": img, "ru": w["ru"]})
    cards = "".join(w_cards)
    game = json.dumps(js_words, ensure_ascii=False)
    gjs = f"<script>{GAME_JS.replace('__WORDS__', game)}</script>"
    bubble = ("Мяу! Я мистер Уискерс, кот-бард! Перед тобой мои волшебные слова. "
              "Нажми 🔊 и повтори за мной вслух, а потом поиграй в игру!")
    body = char_header("cat", l, "Слова", bubble) + lesson_nav(l["n"], "words") + f"""
<div class="panel"><h2 class="sec">📖 ВОЛШЕБНЫЕ КАРТОЧКИ</h2><div class="cards">{cards}</div></div>
<div class="panel"><h2 class="sec">🎮 ИГРА: НАЙДИ СЛОВО</h2>
<p style="font-size:13px;color:var(--dim);margin-bottom:10px">Кот показывает картинку — выбери правильное английское слово!</p>
<div id="q"></div><div class="final" id="final"></div>
<div style="margin-top:12px"><button class="btn ghost" onclick="startGame()">🔄 Играть снова</button></div></div>
"""
    return page(f"Урок {l['n']}: {l['title_ru']} — Слова", body, gjs)


def build_grammar_page(l):
    g = l["grammar"]
    rules = "".join(f"<li>{r}</li>" for r in g["rules"])
    ex = "".join(
        f'<div class="ex"><div class="en">{esc(e["en"])}</div>'
        f'<div><div class="ru">{esc(e["ru"])}</div>'
        f'<button class="btn ghost" style="font-size:8px;padding:5px 8px;margin-top:4px" onclick="speak(\'{esc(e["en"])}\',this)">🔊 послушать</button></div></div>'
        for e in g["examples"])
    quiz = json.dumps([{"q": q["q"], "options": q["options"], "correct": q["correct"],
                        "why": esc(q.get("why", "")), "ok": esc(q.get("ok", "Верно!")), "bad": esc(q.get("bad", "Ошибка."))}
                       for q in g["quiz"]], ensure_ascii=False)
    qjs = f"<script>{QUIZ_JS.replace('__QUIZ__', quiz)}</script>"
    bubble = ("Гм! Я сэр Бруно, хранитель грамматики! Сегодня мы постигаем волшебное правило. "
              "Читай внимательно, послушай примеры и пройди мой рыцарский тест!")
    body = char_header("bulldog", l, "Грамматика", bubble) + lesson_nav(l["n"], "grammar") + f"""
<div class="panel"><h2 class="sec">⚔️ {esc(g['title']).upper()}</h2>
<p style="margin-bottom:10px">{esc(g['intro'])}</p>
<ul class="rules">{rules}</ul></div>
<div class="panel"><h2 class="sec">📜 ПРИМЕРЫ СЭРА БРУНО</h2>{ex}</div>
<div class="panel"><h2 class="sec">🛡️ РЫЦАРСКИЙ ТЕСТ</h2><div id="quiz"></div>
<div class="final">Пройди тест — и грамматика станет твоим щитом!</div></div>
"""
    return page(f"Урок {l['n']}: {l['title_ru']} — Грамматика", body, qjs)


def build_story_page(l):
    st = l["story"]
    parts = []
    all_ids = []
    for i, part in enumerate(st["parts"]):
        sc = part["scene"]
        lines = []
        for j, ln in enumerate(part["lines"]):
            lid = f"l{i}_{j}"
            all_ids.append(lid)
            lines.append(f"""<div class="line" id="{lid}" data-en="{esc(ln['en'])}">
<button class="tr" onclick="speakLine(this,'{lid}')">🔊</button>
<div style="flex:1"><div class="entext">{esc(ln['en'])}</div>
<div class="rutext">{esc(ln['ru'])}</div></div>
<button class="tr" onclick="toggleRu(this)">📖 перевод</button></div>""")
        parts.append(f"""<div class="scene">
<img class="pic" src="assets/scenes/s{l['n']}_{i}.png" alt="">
<div class="label">— {esc(sc.get('label', ''))} —</div>
{''.join(lines)}</div>""")
    story_text = " ".join(ln["en"] for p in st["parts"] for ln in p["lines"])
    ids_js = json.dumps(all_ids)
    bubble = (f"Плеск-плеск! Я мудрый кит Океанус. История «{st['title_en']}» ждёт тебя! "
              "Слушай строки, читай вслух и открывай перевод, когда захочешь проверить себя.")
    body = char_header("whale", l, "История", bubble) + lesson_nav(l["n"], "story") + f"""
<div class="panel" style="text-align:center">
<h2 class="sec">🐋 {esc(st['title_en']).upper()}</h2>
<p style="color:var(--dim);font-size:13px">«{esc(st['title_ru'])}»</p>
<div style="margin-top:10px"><button class="btn" onclick="speakAll({ids_js},this)">🎧 Слушать всю историю</button></div></div>
{''.join(parts)}
<div class="panel" style="text-align:center"><div class="final">✨ Конец истории. Все истории кита хранятся в его памяти — как и новые слова в твоей! ✨</div></div>
"""
    return page(f"Урок {l['n']}: {l['title_ru']} — История", body)


MOD_COLORS = {1: "#c86a50", 2: "#b8862e", 3: "#5c8ad4", 4: "#7c5cb8"}


def build_hub(cur_n=None):
    ms = META["map_spots"]
    spots = []
    legend = []
    for m in MODULES:
        legend.append(f'<span style="background:{MOD_COLORS[m["id"]]}">{esc(m["title_ru"])}</span>')
    for l in LESSONS:
        sp = ms[str(l["n"])]
        x = sp["x"] / 160 * 100
        y = sp["y"] / 96 * 100
        color = MOD_COLORS[l["module"]["id"]]
        cur = ' cur' if cur_n == l["n"] else ''
        title = f"Урок {l['n']}. {l['title_ru']} — {l['module']['title_ru']}"
        href = STEPIK_LINKS.get(str(l["n"]))
        if href:
            href_attr = f'href="{esc(href)}" target="_blank" rel="noopener"'
        else:
            href_attr = f'href="lesson-{l["n"]:02d}-words.html"'
        spots.append(f'<a class="spot{cur}" style="left:{x:.2f}%;top:{y:.2f}%;background:{color}" '
                     f'{href_attr} title="{esc(title)}">{l["n"]}</a>')
    chars_html = ""
    bubble_txt = {
        "bulldog": "Гм! Я сэр Бруно. В моих школах — грамматика: to be, a/an, can и другие рыцарские правила!",
        "cat": "Мяу! Я мистер Уискерс. На рыночной площади я раздаю волшебные слова и учу произношению!",
        "whale": "Плеск! Я кит Океанус. Я парю над городком и рассказываю истории на английском!",
    }
    for cid in ("bulldog", "cat", "whale"):
        ch = META["characters"][cid]
        chars_html += f"""<div class="card"><img src="assets/chars/{cid}_idle.png" alt="{esc(ch['name'])}">
<div><div class="nm">{esc(ch['name'])}</div><div class="rl">{esc(bubble_txt[cid])}</div></div></div>"""
    total_words = sum(len(l.get("words", [])) for l in LESSONS)
    hub_note = ""
    if cur_n:
        l = BY_N[cur_n]
        hub_note = (f'<div class="panel" style="text-align:center"><div class="final">📍 Ты сейчас в локации '
                    f'{cur_n} — «{esc(l["title_ru"])}». Выбирай следующую дорогу на карте!</div></div>')
    body = f"""
<header class="top">
  <img class="char" src="assets/chars/whale_idle.png" data-idle="assets/chars/whale_idle.png" data-talk="assets/chars/whale_talk.png" alt="кит">
  <div class="bubble">
    <div class="tt px">{esc(META['course_title'])}<span class="sub">Добро пожаловать в {esc(META['town'])} — {esc(META['town_ru'])}!</span></div>
    <div style="font-size:13px">Это волшебный городок, где английский учат три наставника: сэр Бруно (грамматика),
    мистер Уискерс (слова и произношение) и мудрый кит Океанус (истории). 12 уроков · {total_words}+ слов · 12 историй.
    Нажимай на места с номерами на карте и отправляйся в приключение!</div>
  </div>
</header>
<div class="chars3">{chars_html}</div>
<div class="panel">
<h2 class="sec">🗺️ КАРТА ВОЛШЕБНОГО ВОРДСБУРГА</h2>
<div class="legend">{''.join(legend)}</div>
<div class="hub"><img src="assets/map.png" alt="Карта городка">{''.join(spots)}</div>
{hub_note}</div>
<div class="panel" style="text-align:center"><div class="final">✨ Выбери локацию на карте — и вперёд, герой! ✨</div></div>
"""
    return page("Английский с нуля: Волшебный Вордсбург", body)


def main():
    for l in LESSONS:
        n = l["n"]
        with open(os.path.join(SITE, f"lesson-{n:02d}-words.html"), "w", encoding="utf-8") as f:
            f.write(build_words_page(l))
        with open(os.path.join(SITE, f"lesson-{n:02d}-grammar.html"), "w", encoding="utf-8") as f:
            f.write(build_grammar_page(l))
        with open(os.path.join(SITE, f"lesson-{n:02d}-story.html"), "w", encoding="utf-8") as f:
            f.write(build_story_page(l))
    for n in range(1, 13):
        with open(os.path.join(SITE, f"hub-{n:02d}.html"), "w", encoding="utf-8") as f:
            f.write(build_hub(cur_n=n))
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_hub(cur_n=None))
    print(f"страниц: {len(os.listdir(SITE)) - 1} (без assets)")


if __name__ == "__main__":
    main()
