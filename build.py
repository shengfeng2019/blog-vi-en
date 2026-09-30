#!/usr/bin/env python3
"""Build the Vietnamese-English bilingual static blog from translated posts.

- Source: translations/<pid>.json (metadata) + translations/<pid>.en.html / .vi.html (bodies).
- Output: site/index.html (English home), site/vi/index.html (Vietnamese home),
  site/<pid>.html + site/vi/<pid>.html (articles), site/style.css, README.md.
- Articles carry <link rel="canonical"> pointing at the Blogger original.
Idempotent: regenerates everything from translations/ each run.
"""
import glob
import html as htmlmod
import json
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "site")
TRANS_DIR = os.path.join(BASE, "translations")
PERSONAL_INDEX = os.path.expanduser("~/workspace/personal-site/index.html")
BJ = ZoneInfo("Asia/Shanghai")

SITE_NAME_EN = "Daily News Digest"
SITE_NAME_VI = "Điểm Tin Hằng Ngày"
SITE_DESC_EN = ("Daily digest of global and China finance and current-affairs headlines, "
                "translated into English and Vietnamese.")
SITE_DESC_VI = ("Điểm tin hằng ngày về tài chính và thời sự toàn cầu cùng Trung Quốc, "
                "bằng tiếng Anh và tiếng Việt.")


def fmt_date(pub, lang):
    try:
        dt = datetime.fromisoformat(pub).astimezone(BJ)
        if lang == "vi":
            return f"Ngày {dt.day} tháng {dt.month} năm {dt.year}"
        return dt.strftime("%B %d, %Y")
    except Exception:
        return pub[:10]


def fmt_date_short(pub):
    try:
        dt = datetime.fromisoformat(pub).astimezone(BJ)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return pub[:10]


def sanitize(content):
    s = re.sub(r"<script\b[^>]*>.*?</script\s*>", "", content, flags=re.I | re.S)
    s = re.sub(r"\son\w+\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)", "", s, flags=re.I)
    s = re.sub(r"href\s*=\s*(\"|')\s*javascript:[^\"']*\1", 'href="#"', s, flags=re.I)
    return s


def shared_css():
    with open(PERSONAL_INDEX, encoding="utf-8") as f:
        page = f.read()
    m = re.search(r"<style>(.*?)</style>", page, flags=re.S)
    base = m.group(1) if m else ""
    extra = """
  .article{padding:clamp(40px,7vw,72px) 0}
  .article .kicker{font-size:13px;letter-spacing:.28em;color:var(--muted);margin-bottom:18px}
  .article h1{font-size:clamp(26px,5vw,38px);line-height:1.35;font-weight:800;letter-spacing:.01em}
  .article .meta{margin-top:14px;font-size:13px;color:var(--muted)}
  .article .meta a{color:var(--muted)}
  .post-body{margin-top:34px;font-size:16px;color:var(--fg);overflow-wrap:break-word}
  .post-body p{margin:1em 0}
  .post-body img{max-width:100%;height:auto;border-radius:10px;margin:1.2em 0}
  .post-body a{color:var(--fg);text-underline-offset:4px}
  .post-body blockquote{border-left:3px solid var(--hair);margin:1.2em 0;padding:.4em 0 .4em 1em;color:var(--muted)}
  .post-body table{border-collapse:collapse;width:100%;margin:1.2em 0;font-size:14px}
  .post-body th,.post-body td{border:1px solid var(--hair);padding:8px 10px;text-align:left}
  .post-body h2,.post-body h3{margin:1.4em 0 .6em;line-height:1.4}
  .back{margin-top:44px;font-size:14px}
  .back a{color:var(--muted);text-decoration:none}
  .back a:hover{color:var(--fg)}
  .hero{padding:clamp(48px,8vw,84px) 0 8px}
  .hero h1{font-size:clamp(30px,6vw,44px);font-weight:800;letter-spacing:.02em}
  .hero p{margin-top:12px;color:var(--muted);font-size:15px;max-width:38em;line-height:1.8}
  .lang-sw{display:flex;gap:10px;align-items:center;font-size:14px}
  .lang-sw a{color:var(--muted);text-decoration:none}
  .lang-sw a.active{color:var(--fg);font-weight:700}
"""
    return base + extra


def nav_html(lang, prefix):
    if lang == "en":
        brand, home = SITE_NAME_EN, "Home"
        sw = (f'<span class="lang-sw"><a class="active" href="{prefix}index.html">EN</a>'
              f'<a href="{prefix}vi/index.html">VI</a></span>')
        home_href = f"{prefix}index.html"
    else:
        brand, home = SITE_NAME_VI, "Trang chủ"
        sw = (f'<span class="lang-sw"><a href="{prefix}index.html">EN</a>'
              f'<a class="active" href="{prefix}vi/index.html">VI</a></span>')
        home_href = f"{prefix}vi/index.html"
    return f"""<nav>
  <div class="wrap">
    <a class="brand" href="{home_href}">{brand}</a>
    <div class="links">
      <a href="{home_href}">{home}</a>
      {sw}
      <button id="themeBtn" aria-label="toggle theme" title="toggle theme">◐</button>
    </div>
  </div>
</nav>"""


FOOTER_HTML = """<footer>
  <div class="wrap">
    <span>© 2026 Shengfeng Wang · Daily News Digest</span>
    <span>Translated from <a href="https://blog.ltshijie.dpdns.org" target="_blank" rel="noopener">每日要闻综述</a></span>
  </div>
</footer>"""

THEME_JS = """<script>
(function(){
  var root=document.documentElement, btn=document.getElementById('themeBtn');
  try{
    var saved=localStorage.getItem('theme');
    if(saved==='light'||saved==='dark') root.setAttribute('data-theme',saved);
  }catch(e){}
  function syncIcon(){
    var t=root.getAttribute('data-theme');
    var dark = t==='dark' || (t==='auto' && matchMedia('(prefers-color-scheme: dark)').matches);
    btn.textContent = dark ? '◑' : '◐';
  }
  btn.addEventListener('click',function(){
    var t=root.getAttribute('data-theme');
    var dark = t==='dark' || (t==='auto' && matchMedia('(prefers-color-scheme: dark)').matches);
    var next = dark ? 'light' : 'dark';
    root.setAttribute('data-theme',next);
    try{localStorage.setItem('theme',next);}catch(e){}
    syncIcon();
  });
  syncIcon();
})();
</script>"""


def page_shell(lang, title, desc, body_html, canonical="", prefix="", html_lang="en"):
    canon = (f'<link rel="canonical" href="{htmlmod.escape(canonical, quote=True)}">'
             if canonical else "")
    return f"""<!DOCTYPE html>
<html lang="{html_lang}" data-theme="auto">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{htmlmod.escape(title)}</title>
<meta name="description" content="{htmlmod.escape(desc)}">
{canon}
<link rel="stylesheet" href="{prefix}style.css">
</head>
<body>
{nav_html(lang, prefix)}
<main class="wrap">
{body_html}
</main>
{FOOTER_HTML}
{THEME_JS}
</body>
</html>
"""


def load_posts():
    posts = []
    for jf in glob.glob(os.path.join(TRANS_DIR, "*.json")):
        with open(jf, encoding="utf-8") as f:
            meta = json.load(f)
        pid = meta["pid"]
        bodies = {}
        for lang in ("en", "vi"):
            bf = os.path.join(TRANS_DIR, f"{pid}.{lang}.html")
            if os.path.exists(bf):
                with open(bf, encoding="utf-8") as f:
                    bodies[lang] = f.read()
        meta["bodies"] = bodies
        posts.append(meta)
    posts.sort(key=lambda p: p["published"], reverse=True)
    return posts


def write_article(post, lang, out_path, prefix, html_lang):
    title = post[f"title_{lang}"]
    kicker = "FINANCE HEADLINES｜GLOBAL ECONOMY" if lang == "en" else "TIN TÀI CHÍNH｜KINH TẾ TOÀN CẦU"
    back = "← Back to home" if lang == "en" else "← Về trang chủ"
    read_orig = ("Read the original (Chinese)" if lang == "en"
                 else "Đọc bản gốc (tiếng Trung)")
    body = f"""<article class="article">
  <div class="kicker">{kicker}</div>
  <h1>{htmlmod.escape(title)}</h1>
  <div class="meta">{fmt_date(post['published'], lang)} · <a href="{htmlmod.escape(post['link'])}" target="_blank" rel="noopener">{read_orig}</a></div>
  <div class="post-body">
{sanitize(post['bodies'][lang])}
  </div>
  <p class="back"><a href="index.html">{back}</a></p>
</article>"""
    site_name = SITE_NAME_EN if lang == "en" else SITE_NAME_VI
    out = page_shell(lang, title + " · " + site_name, post[f"desc_{lang}"],
                     body, canonical=post["link"], prefix=prefix,
                     html_lang=html_lang)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)


def write_home(posts, lang, out_path, prefix, html_lang):
    if lang == "en":
        site_name, site_desc = SITE_NAME_EN, SITE_DESC_EN
        latest_k, all_k = "Latest articles", "All articles"
        empty = "No translated articles yet — check back soon."
    else:
        site_name, site_desc = SITE_NAME_VI, SITE_DESC_VI
        latest_k, all_k = "Bài mới nhất", "Tất cả bài viết"
        empty = "Chưa có bài dịch nào — vui lòng quay lại sau."
    parts = [f"""<div class="hero">
  <h1>{site_name}</h1>
  <p>{site_desc}</p>
</div>
<div class="article" style="padding-top:24px">"""]
    if posts:
        parts.append(f'  <div class="kicker">{latest_k}</div>\n  <div class="blog-list">')
        for p in posts:
            parts.append(
                '    <a class="post-item" href="{}.html">'
                '<span class="post-date">{}</span>'
                '<span class="post-title">{}</span></a>'.format(
                    p["pid"], fmt_date_short(p["published"]),
                    htmlmod.escape(p[f"title_{lang}"])))
        parts.append("  </div>")
        parts.append(f'  <div class="kicker" style="margin-top:40px">{all_k} · {len(posts)}</div>')
    else:
        parts.append(f"  <p>{empty}</p>")
    parts.append("</div>")
    out = page_shell(lang, site_name, site_desc, "\n".join(parts),
                     prefix=prefix, html_lang=html_lang)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)


def write_readme(n):
    readme = f"""# Daily News Digest · 越英双语博客

{SITE_DESC_EN}

{SITE_DESC_VI}

- 内容来源：Blogger「每日要闻综述」(https://blog.ltshijie.dpdns.org)，仅收录 2026-09-30 之后的新文章（历史 65 篇不翻译）
- 英文首页：`site/index.html` ｜ 越南语首页：`site/vi/index.html`
- 构建脚本：`build.py`（本地运行，输出到 `site/` 后推送）
- 部署：Vercel（连接本仓库后自动部署）

文章页均带有 canonical 指向 Blogger 原文。
"""
    with open(os.path.join(BASE, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)


def main():
    posts = load_posts()
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "style.css"), "w", encoding="utf-8") as f:
        f.write(shared_css())
    write_home(posts, "en", os.path.join(OUT_DIR, "index.html"), "", "en")
    write_home(posts, "vi", os.path.join(OUT_DIR, "vi", "index.html"), "../", "vi")
    for p in posts:
        if "en" in p["bodies"]:
            write_article(p, "en", os.path.join(OUT_DIR, f"{p['pid']}.html"), "", "en")
        if "vi" in p["bodies"]:
            write_article(p, "vi", os.path.join(OUT_DIR, "vi", f"{p['pid']}.html"), "../", "vi")
    write_readme(len(posts))
    print(f"BUILD_OK posts={len(posts)}")


if __name__ == "__main__":
    main()
