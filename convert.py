#!/usr/bin/env python3
"""Build a standalone SVG document from Vektor Systems' HTML, CSS, and JS."""

from base64 import b64encode
from html.parser import HTMLParser
from mimetypes import guess_type
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, quoteattr

ROOT = Path(__file__).resolve().parent
VOID_TAGS = set("area base br col embed hr img input link meta param source track wbr".split())
CSS_URL = re.compile(r"url\(\s*(?:\"([^\"]*)\"|'([^']*)'|([^)]*?))\s*\)", re.I)


class XHTMLParser(HTMLParser):
    """Normalize HTML void tags, entities, and attributes for the XML parser."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        self.emit_tag(tag, attrs, tag in VOID_TAGS)

    def handle_startendtag(self, tag, attrs):
        self.emit_tag(tag, attrs, True)

    def emit_tag(self, tag, attrs, closed):
        attributes = "".join(f" {name}={quoteattr(value if value is not None else name)}"
                             for name, value in attrs)
        self.parts.append(f"<{tag}{attributes}{'/' if closed else ''}>")

    def handle_endtag(self, tag):
        if tag not in VOID_TAGS:
            self.parts.append(f"</{tag}>")

    def handle_data(self, data):
        self.parts.append(escape(data))


def data_url(value):
    if value.startswith(("data:", "#")):
        return value
    url = urlsplit(value)
    if url.scheme or url.netloc or not url.path:
        raise ValueError(f"Expected a local asset, got {value!r}")
    path = (ROOT / unquote(url.path)).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"Asset must be inside the project folder: {value}")
    mime = guess_type(path.name)[0]
    if not mime:
        raise ValueError(f"Could not determine the asset type: {value}")
    encoded = b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def embed_css(css):
    if re.search(r"@import\b", css, re.I):
        raise ValueError("Put imported styles directly in style.css before building.")
    return CSS_URL.sub(lambda match: 'url("' + data_url(next(
        value for value in match.groups() if value is not None
    )) + '")', css)


def cdata(source):
    return "<![CDATA[" + source.replace("]]>", "]]]]><![CDATA[>") + "]]>"


def build():
    parser = XHTMLParser()
    parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
    parser.close()
    html = ET.fromstring("".join(parser.parts))
    body = html.find("body")
    if body is None:
        raise ValueError("index.html must have a body.")
    css = embed_css((ROOT / "style.css").read_text(encoding="utf-8"))
    script = (ROOT / "script.js").read_text(encoding="utf-8")
    title = html.findtext("head/title") or "Vektor Systems"
    language = html.get("lang", "en")

    for node in body.iter():
        if node.tag in {"script", "iframe", "link"} or "srcset" in node.attrib:
            raise ValueError(f"Unsupported body markup on <{node.tag}>. Use script.js, style.css, and local src assets.")
        for attr in ("src", "poster"):
            if attr in node.attrib:
                node.set(attr, data_url(node.get(attr)))
        if "style" in node.attrib:
            node.set("style", embed_css(node.get("style")))
        if node.tag == "style" and node.text:
            node.text = embed_css(node.text)

    markup = escape(body.text or "") + "".join(ET.tostring(node, encoding="unicode") for node in body)
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" xml:lang={quoteattr(language)}>
  <title>{escape(title)}</title>
  <style>{cdata("svg { display:block; width:100%; height:100%; }")}</style>
  <foreignObject width="100%" height="100%">
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%">
      <style>{cdata(css)}</style>
{markup}    </div>
  </foreignObject>
  <script>{cdata(script)}</script>
</svg>
'''
    ET.fromstring(svg)
    output = ROOT / "dist" / "index.svg"
    output.parent.mkdir(exist_ok=True)
    output.write_text(svg, encoding="utf-8")
    print(f"Built {output.relative_to(ROOT)} ({output.stat().st_size:,} bytes).")


if __name__ == "__main__":
    try:
        build()
    except (OSError, ValueError, ET.ParseError) as error:
        sys.exit(f"Conversion failed: {error}")
