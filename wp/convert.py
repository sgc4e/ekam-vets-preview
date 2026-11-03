#!/usr/bin/env python3
"""Convert the static ekam vets pages into WordPress block markup.

Reads the English pages in the repo root and the Hindi pages in hi/, takes the
content between </header> and <footer>, and writes serialized core blocks to
wp/content/<lang>/<slug>.html plus wp/content/manifest.json.

Stdlib only.  Run from anywhere:  python3 wp/convert.py

Slug scheme: <file>.html -> /<file>/ , index.html -> / . Blog posts keep their
file name as slug (/blog-heat-stroke/). Hindi pages link to /hi/<slug>/ and
/hi/ for the home page.
"""
import ast
import json
import re
import sys
from html import escape
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent
OUT = HERE / "content"
THEME = "{{theme}}"  # import.php replaces this with get_theme_file_uri()

VOID = {"img", "br", "hr", "input", "meta", "link", "source", "wbr"}
INLINE = {"a", "b", "strong", "em", "i", "span", "small", "br", "code", "sup", "sub", "u", "s", "mark"}

# Inline style declarations -> utility classes defined in wp-compat.css.
# Unknown declarations stop the build rather than being dropped silently.
UTIL = {
    "margin-top:16px": "u-mt-16",
    "margin-top:26px": "u-mt-26",
    "margin-top:30px": "u-mt-30",
    "margin-top:32px": "u-mt-32",
    "margin-top:34px": "u-mt-34",
    "margin-top:40px": "u-mt-40",
    "margin-bottom:24px": "u-mb-24",
    "margin-bottom:26px": "u-mb-26",
    "margin:0": "u-m-0",
    "margin-left:auto": "u-mx-auto",
    "margin-right:auto": "u-mx-auto",
    "text-align:center": "u-center",
    "padding-top:34px": "u-pt-34",
    "align-items:start": "u-items-start",
    "color:#D9B48F": "u-clay",
    "color:rgba(239,230,217,.82)": "u-sand-82",
    "font-family:var(--serif)": "u-serif",
    "font-size:1.5rem": "u-fs-150",
    "color:var(--neem)": "u-neem",
}

# Paragraphs that must not be removed or moved (CLAUDE.md section 8).
LOCKS = {
    "homeopathy never-used-for": lambda t: all(w in t.lower() for w in ("infection", "trauma", "poisoning"))
    or all(w in t for w in ("संक्रमण", "चोट", "ज़हर")),
    "indicative pricing": lambda t: ("indicative" in t.lower() and "reception" in t.lower())
    or ("अनुमानित" in t and "रिसेप्शन" in t),
}


# ---------------------------------------------------------------- DOM
class Node:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs), parent, []

    @property
    def elements(self):
        return [c for c in self.children if isinstance(c, Node)]

    def classes(self):
        return (self.attrs.get("class") or "").split()

    def find_all(self, tag):
        for c in self.elements:
            if c.tag == tag:
                yield c
            yield from c.find_all(tag)

    def text(self):
        return "".join(c if isinstance(c, str) else c.text() for c in self.children)


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = self.cur = Node("root")

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        self.cur.children.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def parse(html):
    t = Tree()
    t.feed(html)
    t.close()
    return t.root


def is_ws(n):
    return isinstance(n, str) and not n.strip()


def has_svg(n):
    return n.tag == "svg" or any(True for _ in n.find_all("svg"))


# ---------------------------------------------------------------- serialization
def attr_str(attrs):
    out = []
    for k, v in attrs.items():
        out.append(k if v is None else f'{k}="{escape(v, quote=True)}"')
    return (" " + " ".join(out)) if out else ""


def block(name, attrs=None, html=None):
    a = ""
    if attrs:
        s = json.dumps(attrs, ensure_ascii=False, separators=(",", ":"))
        s = s.replace("--", "\\u002d\\u002d").replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        a = " " + s
    if html is None:
        return f"<!-- wp:{name}{a} /-->"
    return f"<!-- wp:{name}{a} -->\n{html}\n<!-- /wp:{name} -->"


class Converter:
    def __init__(self, lang, slug):
        self.lang, self.slug, self.locked = lang, slug, []

    # links and assets ------------------------------------------------
    def href(self, h):
        if re.match(r"^(https?:|mailto:|tel:|#|/)", h):
            return h
        m = re.match(r"^(\.\./)?([\w-]+)\.html(#[\w-]+)?$", h)
        if not m:
            sys.exit(f"{self.lang}/{self.slug}: cannot map link {h!r}")
        up, slug, frag = m.groups()
        base = "/hi" if self.lang == "hi" and not up else ""
        return (base + "/" if slug == "index" else f"{base}/{slug}/") + (frag or "")

    def src(self, s):
        m = re.match(r"^(?:\.\./)?img/(.+)$", s)
        return f"{THEME}/assets/img/{m.group(1)}" if m else s

    def util(self, n):
        out = []
        for decl in filter(None, (d.strip() for d in (n.attrs.get("style") or "").split(";"))):
            key = re.sub(r"\s*:\s*", ":", decl)
            if key not in UTIL:
                sys.exit(f"{self.lang}/{self.slug}: no utility class for style {decl!r} on <{n.tag}>")
            if UTIL[key] not in out:
                out.append(UTIL[key])
        return out

    # raw html (core/html and rich text) ----------------------------------
    def raw(self, n):
        if isinstance(n, str):
            return escape(n, quote=False)
        a = dict(n.attrs)
        if "href" in a:
            a["href"] = self.href(a["href"])
        if "src" in a:
            a["src"] = self.src(a["src"])
        if n.tag in VOID:
            return f"<{n.tag}{attr_str(a)}>"
        return f"<{n.tag}{attr_str(a)}>{''.join(self.raw(c) for c in n.children)}</{n.tag}>"

    def rich(self, nodes):
        """Inline content for RichText: collapse whitespace, drop empty formats."""
        def ser(n):
            if isinstance(n, str):
                return escape(re.sub(r"\s+", " ", n), quote=False)
            if n.tag == "br":
                return "<br>"
            inner = "".join(ser(c) for c in n.children)
            if not inner.strip():
                return inner
            a = {k: v for k, v in n.attrs.items() if not (n.tag == "a" and k == "class")}
            if "href" in a:
                a["href"] = self.href(a["href"])
            return f"<{n.tag}{attr_str(a)}>{inner}</{n.tag}>"
        html = "".join(ser(c) for c in nodes)
        return re.sub(r"\s*<br>\s*", "<br>", html).strip()

    # blocks ------------------------------------------------------------
    def paragraph(self, classes, content, text=None):
        attrs = {}
        if classes:
            attrs["className"] = " ".join(classes)
        text = text if text is not None else re.sub(r"<[^>]+>", "", content)
        for label, test in LOCKS.items():
            if test(text):
                attrs["lock"] = {"move": True, "remove": True}
                self.locked.append(label)
        cls = f' class="{" ".join(classes)}"' if classes else ""
        return block("paragraph", attrs, f"<p{cls}>{content}</p>")

    def group(self, tag, classes, anchor, inner):
        attrs = {}
        if tag != "div":
            attrs["tagName"] = tag
        if classes:
            attrs["className"] = " ".join(classes)
        if anchor:
            attrs["anchor"] = anchor
        idattr = f' id="{anchor}"' if anchor else ""
        cls = " ".join(["wp-block-group"] + classes)
        body = "\n\n".join(inner)
        return block("group", attrs, f'<{tag}{idattr} class="{cls}">\n{body}\n</{tag}>')

    def image(self, img, classes):
        attrs = {"className": " ".join(classes)} if classes else {}
        cls = " ".join(["wp-block-image"] + classes)
        src = escape(self.src(img.attrs["src"]), quote=True)
        alt = escape(img.attrs.get("alt") or "", quote=True)
        return block("image", attrs, f'<figure class="{cls}"><img src="{src}" alt="{alt}"/></figure>')

    def buttons(self, links, classes, center):
        classes = [c for c in classes if c != "u-center"]
        attrs = {}
        if classes:
            attrs["className"] = " ".join(classes)
        if center:
            attrs["layout"] = {"type": "flex", "justifyContent": "center"}
        inner = []
        for a in links:
            styles = [f"is-style-{c}" for c in a.classes() if c in ("dark", "line", "ghost")]
            battrs = {"className": " ".join(styles)} if styles else {}
            bcls = " ".join(["wp-block-button"] + styles)
            href = escape(self.href(a.attrs["href"]), quote=True)
            inner.append(block("button", battrs,
                f'<div class="{bcls}"><a class="wp-block-button__link wp-element-button" href="{href}">{self.rich(a.children)}</a></div>'))
        cls = " ".join(["wp-block-buttons"] + classes)
        return block("buttons", attrs, f'<div class="{cls}">\n' + "\n\n".join(inner) + "\n</div>")

    def heading(self, n, classes):
        level = int(n.tag[1])
        attrs = {"level": level} if level != 2 else {}
        if classes:
            attrs["className"] = " ".join(classes)
        cls = " ".join(["wp-block-heading"] + classes)
        return block("heading", attrs, f'<h{level} class="{cls}">{self.rich(n.children)}</h{level}>')

    def list(self, n, classes):
        attrs = {"ordered": True} if n.tag == "ol" else {}
        if classes:
            attrs["className"] = " ".join(classes)
        items = [block("list-item", None, f"<li>{self.rich(li.children)}</li>") for li in n.elements if li.tag == "li"]
        cls = " ".join(["wp-block-list"] + classes)
        return block("list", attrs, f'<{n.tag} class="{cls}">' + "".join(items) + f"</{n.tag}>")

    def table(self, n, classes):
        caption = next(n.find_all("caption"), None)
        head, body = [], []
        for tr in n.find_all("tr"):
            cells = [c for c in tr.elements if c.tag in ("th", "td")]
            (head if all(c.tag == "th" for c in cells) and not body else body).append(cells)

        def cell(c):
            right = "text-align:right" in (c.attrs.get("style") or "").replace(" ", "") or "price" in c.classes()
            a = ' class="has-text-align-right" data-align="right"' if right else ""
            return f"<{c.tag}{a}>{self.rich(c.children)}</{c.tag}>"

        def section(tag, rows):
            return f"<{tag}>" + "".join("<tr>" + "".join(cell(c) for c in r) + "</tr>" for r in rows) + f"</{tag}>" if rows else ""

        attrs = {"hasFixedLayout": False, "className": " ".join(classes)}
        cap = f'<figcaption class="wp-element-caption">{self.rich(caption.children)}</figcaption>' if caption else ""
        cls = " ".join(["wp-block-table"] + classes)
        return block("table", attrs, f'<figure class="{cls}"><table>{section("thead", head)}{section("tbody", body)}</table>{cap}</figure>')

    def faq(self, n, classes):
        items, q = [], ""
        for c in n.elements:
            if c.tag == "dt":
                q = self.rich(c.children)
            elif c.tag == "dd":
                p = self.paragraph([], self.rich(c.children))
                items.append(block("details", {"showContent": True},
                                   f'<details class="wp-block-details" open><summary>{q}</summary>{p}</details>'))
        return self.group("div", classes, None, items)

    def html(self, n):
        return block("html", None, self.raw(n))

    # tree walk ---------------------------------------------------------
    def is_inline(self, n):
        return isinstance(n, str) or (n.tag in INLINE and not has_svg(n))

    def children(self, nodes, center=False):
        out, run = [], []

        def flush():
            if any(not is_ws(x) for x in run):
                out.append(self.inline_run(run, center))
            run.clear()

        for n in nodes:
            if self.is_inline(n):
                run.append(n)
            else:
                flush()
                b = self.convert(n, center)
                if b:
                    out.append(b)
        flush()
        return out

    def inline_run(self, run, center, classes=()):
        els = [x for x in run if isinstance(x, Node)]
        texts = [x for x in run if isinstance(x, str) and x.strip()]
        if els and not texts and all(e.tag == "a" and "btn" in e.classes() for e in els):
            return self.buttons(els, list(classes), center)
        if len(els) == 1 and not texts and els[0].classes() and not classes:
            el = els[0]
            if el.tag == "a":  # a.more -> <p class="more"><a>..</a></p>
                return self.paragraph(el.classes() + self.util(el),
                                      f'<a href="{escape(self.href(el.attrs["href"]), quote=True)}">{self.rich(el.children)}</a>')
            return self.paragraph(el.classes() + self.util(el), self.rich(el.children))
        return self.paragraph(list(classes), self.rich(run))

    def convert(self, n, center=False):
        t, classes = n.tag, n.classes() + self.util(n)
        center = center or "u-center" in classes
        if t in ("form", "svg") or (t in INLINE and has_svg(n)) or (t == "a" and "postcard" in classes):
            return self.html(n)
        if t in ("section", "div"):
            els = n.elements
            if len(els) == 1 and els[0].tag == "img" and not n.text().strip():
                img = els[0]
                return self.image(img, classes + img.classes() + self.util(img))
            if "btnrow" in classes:
                return self.buttons(els, classes, center)
            return self.group(t, classes, n.attrs.get("id"), self.children(n.children, center))
        if t == "p":
            return self.inline_run(n.children, center, classes) if n.elements or n.text().strip() else ""
        if t in ("h1", "h2", "h3", "h4"):
            return self.heading(n, classes)
        if t in ("ul", "ol"):
            return self.list(n, classes)
        if t == "img":
            return self.image(n, classes)
        if t == "table":
            return self.table(n, classes)
        if t == "hr":
            cls = " ".join(["wp-block-separator", "has-alpha-channel-opacity"] + classes)
            return block("separator", {"className": " ".join(classes)} if classes else None, f'<hr class="{cls}"/>')
        if t == "dl":
            return self.faq(n, classes)
        sys.exit(f"{self.lang}/{self.slug}: no mapping for <{t} class={classes}>")


# ---------------------------------------------------------------- pages
def page_parts(path):
    s = path.read_text(encoding="utf-8")
    title = re.search(r"<title>(.*?)</title>", s, re.S).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)"', s)
    body = s[s.index("</header>") + len("</header>"): s.index("<footer")]
    return title, desc.group(1) if desc else "", body


def blog_cards(lang_dir):
    root = parse(page_parts(lang_dir / "blog.html")[2])
    cards = {}
    for i, a in enumerate(n for n in root.find_all("a") if "postcard" in n.classes()):
        img = next(a.find_all("img"))
        slug = re.match(r"(?:\.\./)?([\w-]+)\.html", a.attrs["href"]).group(1)
        cards[slug] = {
            "order": i,
            "category": next(x for x in a.find_all("span") if "cat" in x.classes()).text().strip(),
            "excerpt": " ".join(next(a.find_all("p")).text().split()),
            "image": {"url": img.attrs["src"], "alt": img.attrs.get("alt", "")},
        }
    return cards


def hidden_slugs():
    """Pages build.py keeps off the live static site stay out of WordPress too. One list, two sites."""
    m = re.search(r"^HIDDEN\s*=\s*(\{.*?\})", (SRC / "build.py").read_text(encoding="utf-8"), re.M)
    return {Path(n).stem for n in ast.literal_eval(m.group(1))} if m else set()


def convert_lang(lang):
    src_dir = SRC if lang == "en" else SRC / "hi"
    (OUT / lang).mkdir(parents=True, exist_ok=True)
    cards = blog_cards(src_dir)
    entries, found = [], {}
    hidden = hidden_slugs()
    for stale in hidden:
        (OUT / lang / f"{stale}.html").unlink(missing_ok=True)
    for path in sorted(src_dir.glob("*.html")):
        slug = path.stem
        if slug in hidden:
            continue
        title, desc, body = page_parts(path)
        root = parse(body)
        if slug == "blog":  # the Query Loop in templates/home.html replaces the static card grid
            root.children = [c for c in root.children
                             if not (isinstance(c, Node) and any("postgrid" in x.classes() for x in c.find_all("div")))]
        conv = Converter(lang, slug)
        blocks = conv.children(root.children)
        (OUT / lang / f"{slug}.html").write_text("\n\n".join(b for b in blocks if b) + "\n", encoding="utf-8")
        is_post = slug.startswith("blog-")
        entry = {
            "slug": slug,
            "type": "post" if is_post else "page",
            "title": "Home" if slug == "index" and lang == "en" else title.split(" · ")[0].strip(),
            "document_title": re.sub(r"\s+", " ", title).strip(),
            "description": desc,
            "template": "single" if is_post else {"index": "front-page", "blog": "home"}.get(slug, "page"),
        }
        if slug == "index" and lang == "hi":
            entry["title"] = "होम"
        if is_post:
            entry.update(cards[slug])
        entries.append(entry)
        if conv.locked:
            found[slug] = conv.locked
    for slug, labels in found.items():
        print(f"  locked [{lang}] {slug}: {', '.join(labels)}")
    return entries, found


def main():
    manifest = {}
    for lang in ("en", "hi"):
        print(f"{lang}:")
        manifest[lang], found = convert_lang(lang)
        # rates dropped 18 Oct 2026: Parry removed the "indicative, confirmed at reception" line.
        want = {"services", "blog-homeopathy-for-pets"}
        if set(found) != want:
            sys.exit(f"lock check failed for {lang}: expected {sorted(want)}, got {sorted(found)}")
        print(f"  wrote {len(manifest[lang])} files to content/{lang}/")
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("manifest.json written")


if __name__ == "__main__":
    main()
