import io
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
STEP = os.path.join(ROOT, "stepik")
STATE = os.path.join(STEP, "state.json")
KEYS = os.path.join(os.path.dirname(ROOT), "Подключение к Stepik.txt")
SITE = "https://samoylenkoanatoly.github.io/pixel-english-a0"
COURSE = 303918
CTX = ssl.create_default_context()
try:
    probe = urllib.request.urlopen("https://stepik.org/api/courses/1", context=CTX)
    probe.close()
except urllib.error.HTTPError:
    pass
except Exception as e:
    if "CERTIFICATE" not in str(e) and "handshake" not in str(e):
        raise
    CTX = ssl._create_unverified_context()


def keys():
    raw = open(KEYS, "rb").read().decode("utf-8", "replace")
    cid = re.search(r"Client\s*id\s+([A-Za-z0-9]+)", raw).group(1)
    sec = re.search(r"Client\s*secret\s+([A-Za-z0-9]+)", raw).group(1)
    return cid, sec


def api_token():
    cid, sec = keys()
    body = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    req = urllib.request.Request(
        "https://stepik.org/oauth2/token/", data=body, method="POST"
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    import base64

    req.add_header(
        "Authorization",
        "Basic "
        + base64.b64encode(("%s:%s" % (cid, sec)).encode()).decode(),
    )
    with urllib.request.urlopen(req, context=CTX) as r:
        tok = json.load(r)
    return tok["access_token"]


class Api:
    def __init__(self):
        self.token = api_token()

    def req(self, method, path, payload=None):
        url = "https://stepik.org/api/" + path.lstrip("/")
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", "Bearer " + self.token)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, context=CTX) as r:
                return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.load(e)
            except Exception:
                return e.code, {}

    def get(self, path):
        return self.req("GET", path)

    def post(self, path, payload):
        code, body = self.req("POST", path, payload)
        if code in (200, 201):
            return body
        raise RuntimeError("POST %s -> %s %s" % (path, code, json.dumps(body)[:500]))


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE, encoding="utf-8"))
    return {"course": COURSE, "modules": {}, "lessons": {}}


def save_state(st):
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def iframe(url, h=680):
    return '<p><iframe src="%s" width="100%%" height="%d" frameborder="0" allow="autoplay"></iframe></p>' % (url, h)


def ids_query(ids):
    return "&".join("ids[]=%d" % i for i in ids)


def cmd_inspect():
    a = Api()
    code, c = a.get("courses/%d" % COURSE)
    cr = c["courses"][0]
    print("course:", cr["id"], cr.get("title"))
    print("summary:", (cr.get("summary") or "")[:100])
    print("is_public:", cr.get("is_public"), "| sections:", cr.get("sections"))
    secs = cr.get("sections") or []
    total_steps = 0
    if secs:
        code, sd = a.get("sections?" + ids_query(secs))
        for s in sd["sections"]:
            print("section", s["id"], "pos", s.get("position"), repr(s.get("title")), "units", len(s.get("units") or []))
            us = s.get("units") or []
            if us:
                code, ud = a.get("units?" + ids_query(us))
                for u in ud["units"]:
                    lid = u.get("lesson")
                    print("  unit", u["id"], "pos", u.get("position"), "lesson", lid)
                    if lid:
                        code, ld = a.get("lessons/%d" % lid)
                        for L in ld["lessons"]:
                            ns = len(L.get("steps") or [])
                            total_steps += ns
                            print("    lesson", L["id"], repr(L.get("title")), "steps", ns)
    print("TOTAL_STEPS:", total_steps)
    print("TOKEN_OK")


def build_steps(api, lesson_id, l, n, mod):
    steps = []
    steps.append({"block": {"name": "text", "text": iframe(SITE + "/hub-%02d.html" % n, 760)}})
    steps.append({"block": {"name": "text", "text": iframe(SITE + "/lesson-%02d-words.html" % n)}})
    steps.append({"block": {"name": "text", "text": iframe(SITE + "/lesson-%02d-grammar.html" % n, 900)}})
    steps.append({"block": {"name": "text", "text": iframe(SITE + "/lesson-%02d-story.html" % n, 900)}})
    t = l.get("test") or {}
    for q in t.get("choice") or []:
        opts = [
            {
                "text": o,
                "is_correct": i == q["correct"],
                "feedback": q["ok"] if i == q["correct"] else q["bad"],
            }
            for i, o in enumerate(q["options"])
        ]
        steps.append(
            {
                "block": {
                    "name": "choice",
                    "source": {
                        "text": q["q"],
                        "options": opts,
                        "is_multiple_choice": False,
                        "is_html_enabled": False,
                        "preserve_order": True,
                        "sample_size": len(opts),
                        "is_always_correct": False,
                        "is_options_feedback": True,
                    },
                }
            }
        )
    m = t.get("matching")
    if m and m.get("pairs"):
        steps.append(
            {
                "block": {
                    "name": "matching",
                    "source": {
                        "text": "Соедините английские слова с переводом",
                        "pairs": [{"first": p[0], "second": p[1]} for p in m["pairs"]],
                        "preserve_firsts_order": False,
                    },
                }
            }
        )
    for q in t.get("string") or []:
        hint = q.get("hint") or ""
        qtext = "<p>%s</p>" % q["q"]
        if hint:
            qtext += "<p><em>Hint: %s</em></p>" % hint
        steps.append({"block": {"name": "text", "text": qtext}})
        steps.append(
            {
                "block": {
                    "name": "string",
                    "source": {
                        "code": q["answer"],
                        "pattern": q["answer"],
                        "case_sensitive": False,
                        "match_substring": False,
                        "use_re": False,
                    },
                }
            }
        )
    code, ld = api.get("lessons/%d" % lesson_id)
    existing = len((ld["lessons"][0].get("steps")) or [])
    for pos, s in enumerate(steps, 1):
        if pos <= existing:
            print("  =step", pos, s["block"]["name"], "exists, skip")
            continue
        payload = {"stepSource": dict({"lesson": lesson_id, "position": pos}, **s)}
        r = api.post("step-sources", payload)
        created = (r.get("step-sources") or r.get("stepSources"))[0]["id"]
        print("  +step", pos, s["block"]["name"], "->", created)
        time.sleep(0.5)


def cmd_populate():
    st = load_state()
    a = Api()
    mods = []
    meta = json.load(open(os.path.join(DATA, "meta.json"), encoding="utf-8"))
    for i in (1, 2, 3, 4):
        m = json.load(open(os.path.join(DATA, "module%d.json" % i), encoding="utf-8"))
        mods.append(m)
    for mi, m in enumerate(mods, 1):
        mkey = str(m["id"])
        st["modules"].setdefault(mkey, {"lessons": {}})
        cur = st["modules"][mkey]
        if not cur.get("section_id"):
            r = a.post(
                "sections",
                {"section": {"course": COURSE, "title": "Модуль %d. %s" % (mi, m["title_ru"])}},
            )
            cur["section_id"] = r["sections"][0]["id"]
            cur["title"] = r["sections"][0].get("title")
            save_state(st)
            time.sleep(1)
        print("module", mkey, "section", cur["section_id"])
        for li, l in enumerate(m["lessons"], 1):
            n = l["n"]
            lk = str(n)
            rec = st["lessons"].get(lk) or {}
            if not rec.get("lesson_id"):
                lr = a.post(
                    "lessons",
                    {"lesson": {"title": "Урок %d. %s" % (n, l["title_ru"])}},
                )
                rec["lesson_id"] = lr["lessons"][0]["id"]
                st["lessons"][lk] = rec
                save_state(st)
                time.sleep(1)
                ur = a.post(
                    "units",
                    {
                        "unit": {
                            "section": cur["section_id"],
                            "lesson": rec["lesson_id"],
                            "position": li,
                        }
                    },
                )
                rec["unit_id"] = ur["units"][0]["id"]
                save_state(st)
                time.sleep(1)
            if not rec.get("steps_done"):
                print("lesson", n, l["title_ru"], "-> lesson_id", rec["lesson_id"])
                build_steps(a, rec["lesson_id"], l, n, m)
                rec["steps_done"] = True
                save_state(st)
                time.sleep(1)
    write_links(st)


def write_links(st):
    links = {
        n: "https://stepik.org/lesson/%d/step/1" % r["lesson_id"]
        for n, r in sorted(st["lessons"].items(), key=lambda kv: int(kv[0]))
    }
    p = os.path.join(DATA, "stepik_links.json")
    json.dump(links, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("links written:", p, len(links), "lessons")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "inspect"
    if cmd == "inspect":
        cmd_inspect()
    elif cmd == "populate":
        cmd_populate()
    elif cmd == "links":
        write_links(load_state())
    else:
        print("usage: api.py [inspect|populate|links]")
