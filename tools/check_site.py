# -*- coding: utf-8 -*-
import os
import re
import json

site = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site")
htmls = [f for f in os.listdir(site) if f.endswith(".html")]
problems = []
for f in htmls:
    t = open(os.path.join(site, f), encoding="utf-8").read()
    for m in re.findall(r'(?:src|href)="([^"]+)"', t):
        if m.startswith(("http", "index", "lesson", "#", "mailto")):
            continue
        if not os.path.exists(os.path.join(site, m)):
            problems.append((f, m))
print("html-страниц:", len(htmls))
print("битых ссылок:", len(problems))
for p in problems[:20]:
    print("  ", p)
for f in htmls:
    t = open(os.path.join(site, f), encoding="utf-8").read()
    for mm in re.findall(r"var (?:WORDS|QUIZ) = (\[.*?\]);\n", t, re.S):
        json.loads(mm)
print("json в скриптах: OK")
