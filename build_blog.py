#!/usr/bin/env python3
"""
build_blog.py - Zero-dependency Static Site Generator for Aepify Blog
Reads Markdown files with YAML frontmatter from content/blog/
Generates:
  - blog/index.html (Pre-rendered blog index with client-side live search/filtering)
  - blog/<slug>/index.html (Pre-rendered article pages with TOC, JSON-LD schema, share buttons, CTA)
  - sitemap.xml (SEO sitemap of published pages)
  - robots.txt (Robots directives referencing sitemap)
"""

import os
import re
import sys
import json
import math
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content" / "blog"
OUTPUT_BLOG_DIR = BASE_DIR / "blog"
SITE_URL = "https://aepify.com"
BRAND_NAME = "Aepify"

# Categories requested by user
REQUIRED_CATEGORIES = [
    "All",
    "ChatGPT Ads",
    "AI Marketing",
    "Performance Marketing",
    "Growth Marketing",
    "Marketing Strategy",
    "AEO & GEO"
]

# --- HELPER: YAML FRONTMATTER PARSER ---
def parse_frontmatter(content):
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    yaml_block = parts[1].strip()
    body = parts[2].strip()

    meta = {}
    lines = yaml_block.splitlines()
    current_key = None
    in_list = False

    for line in lines:
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue

        list_match = re.match(r"^\s*-\s*[\"']?(.*?)[\"']?\s*$", line)
        if list_match and current_key and in_list:
            meta[current_key].append(list_match.group(1))
            continue

        kv_match = re.match(r"^([a-zA-Z0-9_-]+):\s*(.*)$", line)
        if kv_match:
            key, val = kv_match.group(1).strip(), kv_match.group(2).strip()
            if val == "":
                current_key = key
                meta[key] = []
                in_list = True
            elif val.startswith("[") and val.endswith("]"):
                items = [item.strip().strip("\"'") for item in val[1:-1].split(",") if item.strip()]
                meta[key] = items
                in_list = False
                current_key = None
            elif val.lower() in ("true", "false"):
                meta[key] = (val.lower() == "true")
                in_list = False
                current_key = None
            else:
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                meta[key] = val
                in_list = False
                current_key = None

    return meta, body

# --- HELPER: MARKDOWN TO HTML CONVERTER ---
def slugify(text):
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")

def escape_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def inline_markdown(text):
    text = re.sub(r"!\[(.*?)\]\((.*?)\)", r'<img src="\2" alt="\1" loading="lazy" class="article-inline-img">', text)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"`([^`]+)`", r'<code>\1</code>', text)
    text = re.sub(r"\*\*(.*?)\*\*", r'<strong>\1</strong>', text)
    text = re.sub(r"__(.*?)__", r'<strong>\1</strong>', text)
    text = re.sub(r"\*(.*?)\*", r'<em>\1</em>', text)
    text = re.sub(r"_(.*?)_", r'<em>\1</em>', text)
    return text

def markdown_to_html(md_text):
    toc_items = []
    lines = md_text.splitlines()
    html_lines = []
    in_code_block = False
    code_block_lang = ""
    code_block_lines = []
    in_table = False
    table_lines = []
    in_ul = False
    in_ol = False
    in_blockquote = False
    blockquote_lines = []

    def flush_blockquote():
        nonlocal in_blockquote, blockquote_lines
        if in_blockquote and blockquote_lines:
            bq_text = " ".join(blockquote_lines)
            callout_match = re.match(r"^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*(.*)", bq_text, re.IGNORECASE)
            if callout_match:
                ctype = callout_match.group(1).upper()
                cbody = callout_match.group(2)
                html_lines.append(f'<div class="article-callout article-callout-{ctype.lower()}">')
                html_lines.append(f'  <div class="article-callout-header"><span>{ctype}</span></div>')
                html_lines.append(f'  <div class="article-callout-content">{inline_markdown(cbody)}</div>')
                html_lines.append('</div>')
            else:
                html_lines.append(f'<blockquote><p>{inline_markdown(bq_text)}</p></blockquote>')
            blockquote_lines = []
            in_blockquote = False

    def flush_list():
        nonlocal in_ul, in_ol
        if in_ul:
            html_lines.append("</ul>")
            in_ul = False
        if in_ol:
            html_lines.append("</ol>")
            in_ol = False

    def render_table(tbl_lines):
        if len(tbl_lines) < 2:
            return ""
        html = ['<div class="article-table-wrapper">', '<table>']
        header_cells = [c.strip() for c in tbl_lines[0].strip("|").split("|")]
        html.append("<thead><tr>")
        for cell in header_cells:
            html.append(f"<th>{inline_markdown(cell)}</th>")
        html.append("</tr></thead>")
        html.append("<tbody>")
        for row in tbl_lines[2:]:
            cells = [c.strip() for c in row.strip("|").split("|")]
            html.append("<tr>")
            for cell in cells:
                html.append(f"<td>{inline_markdown(cell)}</td>")
            html.append("</tr>")
        html.append("</tbody></table></div>")
        return "\n".join(html)

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code_block:
                code_content = "\n".join(code_block_lines)
                html_lines.append(f'<pre><code class="language-{code_block_lang}">{escape_html(code_content)}</code></pre>')
                code_block_lines = []
                in_code_block = False
            else:
                flush_list()
                flush_blockquote()
                code_block_lang = stripped[3:].strip()
                in_code_block = True
            continue

        if in_code_block:
            code_block_lines.append(line)
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                flush_list()
                flush_blockquote()
                in_table = True
            table_lines.append(stripped)
            continue
        elif in_table:
            html_lines.append(render_table(table_lines))
            table_lines = []
            in_table = False

        if re.match(r"^---+$", stripped):
            flush_list()
            flush_blockquote()
            html_lines.append('<hr class="article-divider">')
            continue

        if stripped.startswith(">"):
            flush_list()
            in_blockquote = True
            b_content = stripped.lstrip(">").strip()
            blockquote_lines.append(b_content)
            continue
        elif in_blockquote:
            flush_blockquote()

        heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading_match:
            flush_list()
            flush_blockquote()
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            clean_text = re.sub(r"[*_`\[\]]", "", heading_text)
            heading_slug = slugify(clean_text)

            if level in (2, 3):
                toc_items.append({
                    "level": level,
                    "id": heading_slug,
                    "text": clean_text
                })

            html_lines.append(f'<h{level} id="{heading_slug}">{inline_markdown(heading_text)}</h{level}>')
            continue

        ul_match = re.match(r"^[-*+]\s+(.*)$", stripped)
        if ul_match:
            flush_blockquote()
            if in_ol:
                html_lines.append("</ol>")
                in_ol = False
            if not in_ul:
                html_lines.append("<ul>")
                in_ul = True
            html_lines.append(f"<li>{inline_markdown(ul_match.group(1))}</li>")
            continue

        ol_match = re.match(r"^\d+\.\s+(.*)$", stripped)
        if ol_match:
            flush_blockquote()
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            if not in_ol:
                html_lines.append("<ol>")
                in_ol = True
            html_lines.append(f"<li>{inline_markdown(ol_match.group(1))}</li>")
            continue

        if not stripped:
            flush_list()
            flush_blockquote()
            continue

        flush_list()
        flush_blockquote()
        html_lines.append(f"<p>{inline_markdown(stripped)}</p>")

    flush_list()
    flush_blockquote()
    if in_table and table_lines:
        html_lines.append(render_table(table_lines))

    return "\n".join(html_lines), toc_items

def calculate_reading_time(text):
    words = len(re.findall(r"\w+", text))
    minutes = max(1, math.ceil(words / 200))
    return f"{minutes} min read"

def format_date(date_str):
    try:
        dt = datetime.strptime(str(date_str).strip(), "%Y-%m-%d")
        return dt.strftime("%B %d, %Y")
    except Exception:
        return str(date_str)

# --- TEMPLATES ---

def get_site_header(active_nav="blog"):
    return f'''  <!-- STICKY COMPACTING NAVIGATION -->
  <header class="navbar" id="navbar">
    <div class="container nav-container">
      <a href="/" class="brand-link" aria-label="Aepify Home">
        <img src="/logo-cropped.png" alt="Aepify" class="brand-logo" width="132" height="52">
      </a>

      <nav class="nav-links" id="navLinks" aria-label="Main Navigation">
        <a href="/#who-its-for" class="nav-link">Who It's For</a>
        <a href="/#how-it-works" class="nav-link">How It Works</a>
        <a href="/#opportunity-engine" class="nav-link">Opportunity Score</a>
        <a href="/#pricing" class="nav-link">Pricing</a>
        <a href="/#faq" class="nav-link">FAQ</a>
        <a href="/blog/" class="nav-link{' active' if active_nav == 'blog' else ''}">Blog</a>
      </nav>

      <div class="nav-actions">
        <a href="https://tally.so/r/GxZpre" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm nav-cta">
          <span class="nav-cta-desktop">Get Your FREE Opportunity Report →</span>
          <span class="nav-cta-mobile">Report →</span>
        </a>
        <button class="mobile-toggle" id="mobileToggle" aria-label="Toggle navigation menu" aria-expanded="false" type="button">
          <span class="bar"></span>
          <span class="bar"></span>
        </button>
      </div>
    </div>

    <!-- Mobile Drawer Menu -->
    <div class="mobile-menu" id="mobileMenu" aria-hidden="true">
      <div class="mobile-menu-inner">
        <a href="/#who-its-for" class="mobile-nav-link">Who It's For</a>
        <a href="/#how-it-works" class="mobile-nav-link">How It Works</a>
        <a href="/#opportunity-engine" class="mobile-nav-link">Opportunity Score</a>
        <a href="/#pricing" class="mobile-nav-link">Pricing</a>
        <a href="/#faq" class="mobile-nav-link">FAQ</a>
        <a href="/blog/" class="mobile-nav-link{' active' if active_nav == 'blog' else ''}">Blog</a>
        <div class="mobile-menu-cta">
          <a href="https://tally.so/r/GxZpre" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-full mobile-cta-btn">
            Get Your FREE Opportunity Report →
          </a>
        </div>
      </div>
    </div>
  </header>'''

def get_site_footer():
    return '''  <!-- FOOTER -->
  <footer class="site-footer">
    <div class="container footer-container">
      <div class="footer-top-grid">
        
        <!-- Brand & Social Column -->
        <div class="footer-brand-column">
          <a href="/" class="footer-logo-link" aria-label="Aepify Home">
            <img src="/logo-cropped.png" alt="Aepify" class="footer-logo" width="118" height="46">
          </a>
          <p class="footer-desc">
            ChatGPT Ads readiness, strategy and management for businesses.
          </p>
          <div class="footer-social-links">
            <a href="https://www.instagram.com/aepify.ai/" target="_blank" rel="noopener noreferrer" class="footer-social-btn" aria-label="Follow Aepify on Instagram">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
                <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
                <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
              </svg>
              <span>Instagram</span>
            </a>
            <a href="https://www.linkedin.com/company/aepify/" target="_blank" rel="noopener noreferrer" class="footer-social-btn" aria-label="Follow Aepify on LinkedIn">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 10.9v8.37H9.2V10.9H6.46M7.83 6.45a1.64 1.64 0 1 0 0 3.28 1.64 1.64 0 0 0 0-3.28z"/>
              </svg>
              <span>LinkedIn</span>
            </a>
          </div>
        </div>

        <!-- Navigation Column: Blog comes after FAQ -->
        <div class="footer-nav-column">
          <h4 class="footer-column-heading">Navigation</h4>
          <nav class="footer-nav-list" aria-label="Footer navigation">
            <a href="/#who-its-for" class="footer-link">Who It's For</a>
            <a href="/#how-it-works" class="footer-link">How It Works</a>
            <a href="/#opportunity-engine" class="footer-link">Opportunity Score</a>
            <a href="/#pricing" class="footer-link">Pricing</a>
            <a href="/#faq" class="footer-link">FAQ</a>
            <a href="/blog/" class="footer-link">Blog</a>
          </nav>
        </div>

        <!-- Contact Us Column with Explicit Email -->
        <div class="footer-contact-column">
          <h4 class="footer-column-heading">Contact Us</h4>
          <p class="footer-contact-text">
            Have questions or want to discuss your ChatGPT Ads campaign? Reach our team directly:
          </p>
          <a href="mailto:contact@aepify.com" class="footer-contact-email-card" aria-label="Email Aepify directly at contact@aepify.com">
            <span class="email-icon-box">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                <polyline points="22,6 12,13 2,6"></polyline>
              </svg>
            </span>
            <div class="email-details">
              <span class="email-label">EMAIL US DIRECTLY</span>
              <strong class="email-address">contact@aepify.com</strong>
            </div>
            <span class="email-action-arrow">→</span>
          </a>
          <div class="footer-contact-badge">
            <span class="badge-dot"></span>
            <span>We typically respond within 24 hours</span>
          </div>
        </div>

      </div>

      <div class="footer-bottom-row">
        <div class="footer-legal-links">
          <a href="/#faq" class="legal-link">Privacy Policy</a>
          <span class="legal-separator">·</span>
          <a href="/#faq" class="legal-link">Terms</a>
        </div>
        <p class="footer-disclaimer">
          Aepify is an independent ChatGPT Ads management service and is not affiliated with or endorsed by OpenAI.
        </p>
      </div>
    </div>
  </footer>

  <!-- FLOATING WHATSAPP BUTTON -->
  <a 
    href="https://wa.me/919000271367?text=Hi%20Aepify%2C%20I%27d%20like%20to%20learn%20more%20about%20ChatGPT%20Ads%20management." 
    target="_blank" 
    rel="noopener noreferrer" 
    class="whatsapp-floating-btn whatsapp-link" 
    id="whatsappFloatingBtn" 
    aria-label="Chat with Aepify on WhatsApp"
  >
    <svg width="30" height="30" viewBox="0 0 24 24" fill="#FFFFFF" aria-hidden="true">
      <path d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.816 9.816 0 0 0 12.04 2zm0 18.15c-1.48 0-2.93-.4-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.216 8.216 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.24-8.24 2.2 0 4.27.86 5.82 2.42a8.18 8.18 0 0 1 2.41 5.83c.01 4.54-3.69 8.23-8.22 8.23zm4.52-6.16c-.25-.12-1.47-.72-1.69-.81-.23-.09-.39-.12-.56.12-.17.25-.64.81-.79.97-.14.17-.29.18-.54.06-.25-.12-1.05-.39-1.99-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.02-.38.11-.51.11-.11.25-.29.37-.43.12-.15.17-.25.25-.42.08-.17.04-.31-.02-.44-.06-.12-.56-1.34-.76-1.84-.2-.48-.41-.42-.56-.43h-.48c-.17 0-.44.06-.66.31-.23.25-.87.85-.87 2.07 0 1.22.89 2.4 1.01 2.56.12.17 1.75 2.67 4.23 3.74.59.26 1.05.41 1.41.53.6.19 1.14.16 1.57.1.48-.07 1.47-.6 1.68-1.18.21-.58.21-1.07.14-1.18-.06-.12-.22-.18-.47-.3z"/>
    </svg>
  </a>'''

def render_blog_card(article):
    img_src = article.get("featured_image", "/assets/blog/what-are-chatgpt-ads.png")
    img_alt = article.get("featured_image_alt", article.get("title", ""))
    slug = article["slug"]
    url = f"/blog/{slug}/"
    tags_attr = " ".join(article.get("tags", []))

    return f'''      <article class="blog-card" data-title="{escape_html(article['title'].lower())}" data-category="{escape_html(article['category'].lower())}" data-tags="{escape_html(tags_attr.lower())}">
        <a href="{url}" class="blog-card-thumb-wrap" aria-label="{escape_html(article['title'])}">
          <img src="{img_src}" alt="{escape_html(img_alt)}" class="blog-card-thumb" loading="lazy">
        </a>
        <div class="blog-card-content">
          <div class="blog-card-meta-top">
            <span class="blog-card-cat-badge">{escape_html(article['category'])}</span>
            <span class="blog-card-read-time">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
              {article['reading_time']}
            </span>
          </div>
          <h2 class="blog-card-title">
            <a href="{url}">{escape_html(article['title'])}</a>
          </h2>
          <p class="blog-card-excerpt">{escape_html(article['excerpt'])}</p>
          <div class="blog-card-footer">
            <time datetime="{article['date']}">{article['formatted_date']}</time>
            <a href="{url}" class="blog-card-link-action" aria-label="Read article: {escape_html(article['title'])}">Read article →</a>
          </div>
        </div>
      </article>'''

def build_index_page(articles):
    cards_html = "\n".join([render_blog_card(art) for art in articles])
    cat_buttons = ['<button class="blog-cat-btn active" data-category="all">All</button>']
    for cat in REQUIRED_CATEGORIES:
        if cat.lower() == "all":
            continue
        cat_buttons.append(f'<button class="blog-cat-btn" data-category="{escape_html(cat.lower())}">{escape_html(cat)}</button>')
    cat_buttons_html = "\n            ".join(cat_buttons)

    header = get_site_header(active_nav="blog")
    footer = get_site_footer()

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>ChatGPT Ads Blog, Insights & Strategy | Aepify</title>
  <meta name="description" content="Explore expert insights, practical guides, and performance strategies for ChatGPT Ads, conversational AI marketing, and customer intent targeting from Aepify.">
  <link rel="canonical" href="{SITE_URL}/blog/">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="ChatGPT Ads Blog, Insights & Strategy | Aepify">
  <meta property="og:description" content="Explore expert insights, practical guides, and performance strategies for ChatGPT Ads, conversational AI marketing, and customer intent targeting from Aepify.">
  <meta property="og:url" content="{SITE_URL}/blog/">
  <meta property="og:image" content="{SITE_URL}/assets/blog/what-are-chatgpt-ads.png">
  <meta property="og:site_name" content="Aepify">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="ChatGPT Ads Blog, Insights & Strategy | Aepify">
  <meta name="twitter:description" content="Explore expert insights, practical guides, and performance strategies for ChatGPT Ads, conversational AI marketing, and customer intent targeting from Aepify.">
  <meta name="twitter:image" content="{SITE_URL}/assets/blog/what-are-chatgpt-ads.png">

  <!-- Favicon -->
  <link rel="icon" type="image/png" href="/favicon.png?v=2">
  <link rel="apple-touch-icon" href="/favicon.png?v=2">

  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">

  <link rel="stylesheet" href="/styles.css?v=3.3">
</head>
<body class="blog-page">
  <div class="site-ambient-grid" aria-hidden="true"></div>

{header}

  <main>
    <section class="blog-hero-section">
      <div class="container">
        <div class="blog-header-box">
          <span class="blog-eyebrow-badge">AEPIFY KNOWLEDGE &amp; STRATEGY</span>
          <h1 class="blog-title">Insights on ChatGPT Ads &amp; AI Marketing</h1>
          <p class="blog-subtitle">
            Practical guides, buyer intent frameworks, and strategic benchmarks<br class="desktop-br">to help businesses capture high-consideration customers in conversational AI.
          </p>
        </div>

        <div class="blog-controls-wrapper">
          <div class="blog-search-box">
            <svg class="blog-search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input type="text" id="blogSearchInput" class="blog-search-input" placeholder="Search guides by keyword, topic, or industry..." aria-label="Search blog articles">
            <button type="button" id="blogSearchClear" class="blog-search-clear" aria-label="Clear search">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          <div class="blog-categories-bar" id="categoryFilterBar">
            {cat_buttons_html}
          </div>
        </div>

        <div class="blog-grid" id="blogCardsGrid">
{cards_html}
        </div>

        <div class="blog-empty-state" id="blogEmptyState">
          <svg class="blog-empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            <line x1="8" y1="11" x2="14" y2="11"></line>
          </svg>
          <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 8px;">No matching articles found</h3>
          <p style="color: var(--color-muted); font-size: 0.95rem; margin-bottom: 18px;">Try adjusting your search terms or selecting another category.</p>
          <button type="button" class="btn btn-secondary btn-sm" id="btnResetFilters">Reset all filters</button>
        </div>
      </div>
    </section>
  </main>

{footer}

  <script src="/js/blog.js?v=1.1"></script>
</body>
</html>'''
    return html

def build_article_page(article, all_articles):
    slug = article["slug"]
    title = article["title"]
    category = article.get("category", "ChatGPT Ads")
    date_str = article.get("date", "")
    formatted_date = article.get("formatted_date", date_str)
    modified_date = article.get("modified_date", date_str)
    reading_time = article.get("reading_time", "5 min read")
    author = article.get("author", "Aepify Team")
    author_role = article.get("author_role", "ChatGPT Ads Strategists")
    excerpt = article.get("excerpt", "")
    featured_img = article.get("featured_image", "/assets/blog/what-are-chatgpt-ads.png")
    featured_img_alt = article.get("featured_image_alt", title)
    meta_title = article.get("meta_title", f"{title} | Aepify")
    meta_desc = article.get("meta_description", excerpt)
    canonical_url = f"{SITE_URL}/blog/{slug}/"
    full_img_url = f"{SITE_URL}{featured_img}" if featured_img.startswith("/") else featured_img

    toc_items = article.get("toc_items", [])
    toc_links = []
    mobile_toc_links = []
    for item in toc_items:
        cls = "toc-h3" if item["level"] == 3 else "toc-h2"
        toc_links.append(f'<li class="{cls}"><a href="#{item["id"]}">{escape_html(item["text"])}</a></li>')
        mobile_toc_links.append(f'<a href="#{item["id"]}">{escape_html(item["text"])}</a>')

    toc_nav_html = "\n            ".join(toc_links)
    mobile_toc_nav_html = "\n          ".join(mobile_toc_links)

    related = [a for a in all_articles if a["slug"] != slug][:2]
    related_cards_html = "\n".join([render_blog_card(r) for r in related]) if related else ""
    related_section_html = f'''    <section class="article-related-section">
      <h3 class="article-related-title">Related Reading</h3>
      <div class="blog-grid" style="margin-bottom: 0;">
{related_cards_html}
      </div>
    </section>''' if related else ""

    json_ld_article = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": canonical_url
        },
        "headline": title,
        "description": meta_desc,
        "image": full_img_url,
        "author": {
            "@type": "Organization",
            "name": author,
            "url": SITE_URL
        },
        "publisher": {
            "@type": "Organization",
            "name": BRAND_NAME,
            "url": SITE_URL,
            "logo": {
                "@type": "ImageObject",
                "url": f"{SITE_URL}/logo-cropped.png"
            }
        },
        "datePublished": str(date_str),
        "dateModified": str(modified_date)
    }

    json_ld_breadcrumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": f"{SITE_URL}/"
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Blog",
                "item": f"{SITE_URL}/blog/"
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": title,
                "item": canonical_url
            }
        ]
    }

    encoded_url = canonical_url.replace(":", "%3A").replace("/", "%2F")
    encoded_title = title.replace(" ", "%20").replace("?", "%3F")

    header = get_site_header(active_nav="blog")
    footer = get_site_footer()
    json_article_str = json.dumps(json_ld_article, indent=2)
    json_breadcrumbs_str = json.dumps(json_ld_breadcrumbs, indent=2)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{escape_html(meta_title)}</title>
  <meta name="description" content="{escape_html(meta_desc)}">
  <link rel="canonical" href="{canonical_url}">

  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:title" content="{escape_html(meta_title)}">
  <meta property="og:description" content="{escape_html(meta_desc)}">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:image" content="{full_img_url}">
  <meta property="og:site_name" content="Aepify">
  <meta property="article:published_time" content="{date_str}">
  <meta property="article:modified_time" content="{modified_date}">
  <meta property="article:section" content="{escape_html(category)}">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape_html(meta_title)}">
  <meta name="twitter:description" content="{escape_html(meta_desc)}">
  <meta name="twitter:image" content="{full_img_url}">

  <!-- Favicon -->
  <link rel="icon" type="image/png" href="/favicon.png?v=2">
  <link rel="apple-touch-icon" href="/favicon.png?v=2">

  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">

  <link rel="stylesheet" href="/styles.css?v=3.3">

  <!-- Structured Data (JSON-LD) -->
  <script type="application/ld+json">
{json_article_str}
  </script>
  <script type="application/ld+json">
{json_breadcrumbs_str}
  </script>
</head>
<body class="article-page">
  <div class="site-ambient-grid" aria-hidden="true"></div>

{header}

  <main class="article-main-container">
    <!-- Breadcrumbs -->
    <nav class="article-breadcrumbs" aria-label="Breadcrumb">
      <a href="/">Home</a>
      <span class="article-breadcrumb-sep">/</span>
      <a href="/blog/">Blog</a>
      <span class="article-breadcrumb-sep">/</span>
      <span class="current" aria-current="page">{escape_html(title)}</span>
    </nav>

    <!-- Article Header -->
    <header class="article-header">
      <span class="article-category-badge">{escape_html(category)}</span>
      <h1 class="article-h1">{escape_html(title)}</h1>

      <div class="article-meta-row">
        <div class="article-author-info">
          <div class="article-author-avatar" aria-hidden="true">A</div>
          <div class="article-author-details">
            <span class="article-author-name">{escape_html(author)}</span>
            <span class="article-author-role">{escape_html(author_role)}</span>
          </div>
        </div>

        <div class="article-dates-read">
          <div class="article-date-item">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
            <time datetime="{date_str}">{formatted_date}</time>
          </div>
          <span>•</span>
          <div class="article-date-item">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
            <span>{reading_time}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Featured Image -->
    <div class="article-featured-hero">
      <img src="{featured_img}" alt="{escape_html(featured_img_alt)}" width="1024" height="564">
    </div>

    <!-- Mobile Table of Contents Accordion -->
    <details class="article-toc-mobile">
      <summary>
        <span>Table of Contents</span>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
      </summary>
      <div class="article-toc-mobile-list">
        {mobile_toc_nav_html}
      </div>
    </details>

    <!-- Two-column Layout: TOC Sidebar + Article Body -->
    <div class="article-layout">
      <aside class="article-toc-aside" aria-label="Table of contents">
        <div class="article-toc-box">
          <div class="article-toc-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>
            Table of Contents
          </div>
          <nav class="article-toc-nav">
            <ul>
              {toc_nav_html}
            </ul>
          </nav>
        </div>
      </aside>

      <article class="article-content">
{article['body_html']}

        <!-- Social Share Bar -->
        <div class="article-share-section">
          <span class="article-share-label">Share this guide</span>
          <div class="article-share-buttons">
            <a href="https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}" target="_blank" rel="noopener noreferrer" class="article-share-btn" aria-label="Share on LinkedIn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 10.9v8.37H9.2V10.9H6.46M7.83 6.45a1.64 1.64 0 1 0 0 3.28 1.64 1.64 0 0 0 0-3.28z"/></svg>
              <span>LinkedIn</span>
            </a>
            <a href="https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_title}" target="_blank" rel="noopener noreferrer" class="article-share-btn" aria-label="Share on X">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
              <span>X (Twitter)</span>
            </a>
            <a href="https://www.facebook.com/sharer/sharer.php?u={encoded_url}" target="_blank" rel="noopener noreferrer" class="article-share-btn" aria-label="Share on Facebook">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
              <span>Facebook</span>
            </a>
            <button type="button" class="article-share-btn" id="btnCopyArticleLink" aria-label="Copy article link">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
              <span>Copy Link</span>
            </button>
          </div>
        </div>

        <!-- End of Article Conversion CTA Card with Explicit High-Contrast Colors -->
        <div class="article-cta-box">
          <span class="article-cta-eyebrow">FOUNDING 10 LAUNCH · CHATGPT ADS STRATEGY</span>
          <h3 class="article-cta-title">Ready to turn buying conversations into high-converting campaigns?</h3>
          <p class="article-cta-desc">
            Discover what ChatGPT Ads can do for your business. We map your commercial conversations, build context-native campaigns, and manage performance for a flat $99/month.
          </p>
          <div class="article-cta-actions">
            <a href="https://tally.so/r/GxZpre" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-lg">
              <span>Get Your FREE Opportunity Report →</span>
            </a>
            <a href="mailto:contact@aepify.com" class="btn btn-secondary btn-lg">
              <span>Contact Us →</span>
            </a>
          </div>
        </div>
      </article>
    </div>

{related_section_html}
  </main>

  <div class="copy-toast" id="copyToast">Link copied to clipboard!</div>

{footer}

  <script src="/js/blog.js?v=1.1"></script>
</body>
</html>'''
    return html

def build_sitemap(articles):
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url>',
        f'    <loc>{SITE_URL}/</loc>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
        '  <url>',
        f'    <loc>{SITE_URL}/blog/</loc>',
        '    <changefreq>daily</changefreq>',
        '    <priority>0.9</priority>',
        '  </url>'
    ]

    for art in articles:
        slug = art["slug"]
        lastmod = art.get("modified_date") or art.get("date")
        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{SITE_URL}/blog/{slug}/</loc>')
        if lastmod:
            xml_lines.append(f'    <lastmod>{lastmod}</lastmod>')
        xml_lines.append('    <changefreq>monthly</changefreq>')
        xml_lines.append('    <priority>0.8</priority>')
        xml_lines.append('  </url>')

    xml_lines.append('</urlset>')
    return "\n".join(xml_lines)

def build_robots():
    return f"""User-agent: *
Allow: /
Disallow: /admin/

Sitemap: {SITE_URL}/sitemap.xml
"""

def main():
    print("Starting Aepify Blog Build...")
    if not CONTENT_DIR.exists():
        print(f"Content directory not found: {CONTENT_DIR}")
        return 1

    OUTPUT_BLOG_DIR.mkdir(parents=True, exist_ok=True)

    articles = []

    for md_file in sorted(CONTENT_DIR.glob("*.md")):
        with open(md_file, "r", encoding="utf-8") as f:
            raw_text = f.read()

        meta, body = parse_frontmatter(raw_text)
        if not meta.get("published", True):
            print(f"Skipping unpublished draft: {md_file.name}")
            continue

        slug = meta.get("slug") or md_file.stem
        meta["slug"] = slug
        meta["reading_time"] = calculate_reading_time(body)
        meta["formatted_date"] = format_date(meta.get("date", ""))

        body_html, toc_items = markdown_to_html(body)
        meta["body_html"] = body_html
        meta["toc_items"] = toc_items

        articles.append(meta)

    articles.sort(key=lambda x: str(x.get("date", "")), reverse=True)

    # 1. Build blog index
    index_html = build_index_page(articles)
    with open(OUTPUT_BLOG_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"✓ Generated: blog/index.html ({len(articles)} articles)")

    # 2. Build individual article pages
    for art in articles:
        art_dir = OUTPUT_BLOG_DIR / art["slug"]
        art_dir.mkdir(parents=True, exist_ok=True)
        art_html = build_article_page(art, articles)
        with open(art_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(art_html)
        print(f"✓ Generated: blog/{art['slug']}/index.html")

    # 3. Generate sitemap.xml
    sitemap_xml = build_sitemap(articles)
    with open(BASE_DIR / "sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_xml)
    print("✓ Generated: sitemap.xml")

    # 4. Generate robots.txt
    robots_txt = build_robots()
    with open(BASE_DIR / "robots.txt", "w", encoding="utf-8") as f:
        f.write(robots_txt)
    print("✓ Generated: robots.txt")

    print("\nBlog build complete successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
