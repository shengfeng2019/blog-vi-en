**TL;DR**

- I run a small bilingual (English/Vietnamese) daily news site. I wanted AI assistants — ChatGPT, Perplexity, Gemini, Claude — to be able to find, read, and quote it.
- I did not buy links or hire anyone. I changed how the site publishes its own pages: a root-level `/llms.txt`, a clean Markdown twin for every page, an FAQ written for machines as much as for people, and a fully open robots.txt.
- One thing I deliberately did *not* do: I kept the Markdown files out of my sitemap. The reason is below.
- Everything described here is live and checkable. What I cannot show you yet is a citation count — that measurement is running, and I will update this page with the numbers, good or bad.

## Why I cared

My site publishes a full news digest every morning — global and China finance and current-affairs headlines, translated into English and Vietnamese. News has a short life. If an AI assistant answers a reader's question using somebody else's summary, my work is invisible, even if the facts originally came from reporting I translated and checked.

More readers now meet the news inside an AI answer first. So the practical question for a small publisher is not "how do I rank for this keyword?" It is: **when the machine writes the answer, can it read my page well enough to quote it — and does it know it is allowed to?**

This page is my working answer, written as a record of what I actually changed, in the order I changed it.

## What I changed

### 1. A `/llms.txt` file at the root

The `llms.txt` proposal is simple: put a plain-text map of your site at `/llms.txt`, written for language models — what the site is, and links to the cleanest version of every important page.

Mine lists all 52 articles currently on the site, in both languages (104 links), and every link points to the Markdown version of the page, not the HTML one. At the end of the file there is a short FAQ, including the question "Can AI assistants quote or summarize this site?" — answered with a plain yes, plus where the Markdown files live.

You can read it here: https://vien.wangshengfeng.dpdns.org/llms.txt

### 2. A Markdown twin for every page

Every HTML page on the site also exists as Markdown at the same URL plus `.md`. An article at `/8093631785370763939.html` is also at `/8093631785370763939.md` — same words, no styling, no navigation, no scripts. The two homepages have twins too (`/index.md` and `/vi/index.md`).

The reasoning is plain: a model that wants to quote a passage has an easier job with clean Markdown than with a styled HTML page. I cannot control whether I get cited. I can control whether citing me is easy.

### 3. An FAQ that answers the machine's questions

The FAQ in `llms.txt` and in the homepage Markdown covers five questions: what the site is, how often it updates, where the Chinese original is published, which languages are available, and whether AI assistants may quote it. None of this is clever. It simply removes ambiguity — the site says, in so many words, who publishes it and that quoting is welcome.

### 4. A fully open robots.txt

My robots.txt is three lines: every crawler is allowed everywhere, plus a pointer to the sitemap. No AI crawler is blocked. This sounds obvious, but it is the step most often failed silently: a site that blocks a retrieval crawler has decided, in advance, never to be cited by that system.

### 5. The supporting basics

Every article carries a self-referential canonical URL, hreflang alternates for English, Vietnamese, and x-default, Open Graph tags, and NewsArticle structured data. One site, one entity, two languages — stated the same way on every page.

### The full list

| Change | Why | Status on this site |
|---|---|---|
| `/llms.txt` at the root, listing every article's Markdown version, with an FAQ at the end | Give AI systems one clean map of the site | Live — 104 article links (52 articles × English/Vietnamese) |
| A Markdown twin for every page (same URL + `.md`) | Plain Markdown is easier for models to parse and quote than styled HTML | Live — every article and both homepages |
| FAQ block inside `llms.txt` and the homepage `.md` | Answer "can AI quote this site?" before it is asked | Live — 5 questions |
| robots.txt fully open (`Allow: /` for all agents) | A blocked crawler cannot cite you | Live — no AI crawler blocked |
| Sitemap with HTML pages only, no `.md` URLs | Keep the sitemap a list of canonical pages, not file formats | Live — deliberate choice, explained below |
| Canonical + hreflang (en/vi/x-default) + NewsArticle JSON-LD on every article | One unambiguous entity in two languages | Live |

## What I deliberately did not do

**I did not put the Markdown files in my sitemap.** Most guides tell you to submit everything. My sitemap lists canonical pages — the HTML articles a human reader should land on. The `.md` files are an alternate format of those same pages, and they are already discoverable through `llms.txt`, which is the file actually written for machines. A sitemap full of duplicate-format URLs tells a search engine less, not more.

**I did not write content "for AI" that humans would not want.** The digest is written for readers first, in full, every day. The machine-facing work is all in the packaging: formats, files, and metadata. If a change would make the site worse for a person reading it, I did not make it.

**I did not buy links, and this page is not a promise.** Nothing here guarantees a citation. Anyone who sells you a guarantee on AI citations is selling you a story.

## What happened so far — and what I cannot claim yet

What I can state as fact today:

- Every file described above is deployed and returns HTTP 200, including `/llms.txt`, both homepage Markdown twins, and the article twins.
- The setup survives a daily rebuild: the whole site is regenerated from source every day, and the Markdown twins and `llms.txt` are produced by the same build, not maintained by hand.

What I cannot claim yet:

- I do not have a trustworthy before/after citation count. AI answers are not a stable page you can screenshot once; the same prompt can cite different sources on different days.

So I am measuring it the slow way: a fixed panel of prompts about topics my site covers, asked to the major answer engines on a schedule, with citations recorded. Two weeks of that gives a baseline worth printing.

> [PLACEHOLDER — Table 2: prompt panel results. Columns: prompt / engines asked / cited before changes (baseline) / cited after two weeks / notes. To be filled from the measurement log, not from memory.]

When the table is filled in, this page gets an update date and the numbers stay — including if the honest number is "no change yet."

## How I check whether it is working

If you run a site and want to copy the method, copy the measurement too:

1. **Pick 10–20 real questions** your readers would ask an AI assistant about your topics. Write them down before you change anything.
2. **Ask each engine the same questions** (ChatGPT, Perplexity, Gemini, Claude) and record which sources get cited. Repeat on a fixed schedule — weekly is enough.
3. **Watch referral traffic** from AI surfaces in your analytics, separately from search.
4. **Check the basics in Search Console**: is the sitemap being read, are the canonical pages indexed, are any pages "discovered but not indexed" in bulk? A citation strategy on top of an indexing problem is decoration.
5. **Give it weeks, not days.** You are measuring a habit of machines, not a ranking position.
