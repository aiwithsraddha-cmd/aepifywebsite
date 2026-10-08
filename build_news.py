#!/usr/bin/env python3
"""
build_news.py - Static Site Generator for Aepify News Intelligence Hub
Reads structured news items from data/news.json and status from data/news_status.json.
Generates:
  - news/index.html (News Intelligence Hub with live search & multi-tier filters)
  - news/<slug>/index.html (Individual News Article Pages with NewsArticle JSON-LD)
  - news-sitemap.xml (Google News XML sitemap)
  - Updates sitemap.xml
"""

import os
import sys
import json
import re
import html
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
NEWS_FILE = DATA_DIR / "news.json"
STATUS_FILE = DATA_DIR / "news_status.json"
OUTPUT_NEWS_DIR = BASE_DIR / "news"
SITE_URL = "https://aepify.com"
BRAND_NAME = "Aepify"

def get_google_tag():
    return '''<!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-6SPZVXL7F1"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-6SPZVXL7F1');
  </script>'''

def get_site_header(active_nav="news"):
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
        <a href="/blog/" class="nav-link{' active' if active_nav == 'blog' else ''}">Blog</a>
        <a href="/news/" class="nav-link{' active' if active_nav == 'news' else ''}">News</a>
        <a href="/#pricing" class="nav-link">Pricing</a>
        <a href="/#faq" class="nav-link">FAQ</a>
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
        <a href="/blog/" class="mobile-nav-link{' active' if active_nav == 'blog' else ''}">Blog</a>
        <a href="/news/" class="mobile-nav-link{' active' if active_nav == 'news' else ''}">News</a>
        <a href="/#pricing" class="mobile-nav-link">Pricing</a>
        <a href="/#faq" class="mobile-nav-link">FAQ</a>
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

        <!-- Navigation Column -->
        <div class="footer-nav-column">
          <h4 class="footer-column-heading">Navigation</h4>
          <nav class="footer-nav-list" aria-label="Footer navigation">
            <a href="/#who-its-for" class="footer-link">Who It's For</a>
            <a href="/#how-it-works" class="footer-link">How It Works</a>
            <a href="/#opportunity-engine" class="footer-link">Opportunity Score</a>
            <a href="/blog/" class="footer-link">Blog</a>
            <a href="/news/" class="footer-link">News</a>
            <a href="/#pricing" class="footer-link">Pricing</a>
            <a href="/#faq" class="footer-link">FAQ</a>
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
            <div class="email-content">
              <span class="email-label">Official Inquiries</span>
              <span class="email-address">contact@aepify.com</span>
            </div>
          </a>
        </div>

      </div>

      <div class="footer-bottom">
        <p class="footer-copyright">
          &copy; 2026 Aepify. All rights reserved. ChatGPT Ads is an emerging advertising placement by OpenAI. Aepify is an independent strategic service and is not affiliated with OpenAI.
        </p>
      </div>
    </div>
  </footer>'''

def format_date(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y")
    except Exception:
        return iso_str[:10]

def load_news():
    if not NEWS_FILE.exists():
        return []
    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_status():
    if not STATUS_FILE.exists():
        return {}
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def render_badge_importance(imp):
    imp_upper = imp.upper()
    if imp_upper == "BREAKING":
        return '<span class="badge-breaking">BREAKING</span>'
    elif imp_upper == "HIGH":
        return '<span class="badge-high">HIGH IMPACT</span>'
    return '<span class="badge-medium">UPDATE</span>'

def render_badge_verification(status):
    status_upper = status.upper()
    if status_upper == "CONFIRMED":
        return '<span class="badge-confirmed"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> CONFIRMED</span>'
    elif status_upper == "REPORTED":
        return '<span class="badge-reported"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg> REPORTED</span>'
    return f'<span class="badge-medium">{html.escape(status)}</span>'

def build_index_page(news_items, status):
    featured = news_items[0] if news_items else None
    regular_items = news_items[1:] if len(news_items) > 1 else []

    featured_html = ""
    if featured:
        also_reported_html = ""
        if featured.get("alsoReportedBy"):
            pills = "".join(f'<a href="{html.escape(ar["sourceUrl"])}" target="_blank" rel="noopener noreferrer" class="news-also-reported-pill">{html.escape(ar["sourceName"])}</a>' for ar in featured["alsoReportedBy"])
            also_reported_html = f'''<div class="news-also-reported-pills">
              <span>Also reported by:</span>
              {pills}
            </div>'''

        featured_html = f'''    <!-- FEATURED / BREAKING STORY -->
    <div class="news-featured-container">
      <article class="news-featured-card" data-slug="{html.escape(featured['slug'])}" data-region="{html.escape(featured.get('region','Global'))}" data-topics="{html.escape(','.join(featured.get('topics',[])))}" data-importance="{html.escape(featured.get('importance','HIGH'))}" data-date="{html.escape(featured.get('sourcePublishedAt',''))[:10]}">
        <div class="news-badge-row">
          {render_badge_importance(featured.get('importance','HIGH'))}
          {render_badge_verification(featured.get('verificationStatus','CONFIRMED'))}
          <span class="badge-region">{html.escape(featured.get('region','Global'))}</span>
        </div>

        <h2 class="news-featured-title">
          <a href="/news/{featured['slug']}/">{html.escape(featured['title'])}</a>
        </h2>

        <p class="news-featured-sub">{html.escape(featured['subhead'])}</p>

        <!-- Clean Source Preview Card -->
        <div class="news-source-card">
          <div class="news-source-left">
            <div class="news-source-avatar">{html.escape(featured.get('sourceLogo', featured['sourceName'][:2].upper()))}</div>
            <div class="news-source-info">
              <span class="news-source-name">{html.escape(featured['sourceName'])}</span>
              <span class="news-source-meta">Published {format_date(featured['sourcePublishedAt'])}</span>
            </div>
          </div>
          <a href="{html.escape(featured['sourceUrl'])}" target="_blank" rel="noopener noreferrer" class="news-source-link">
            Read the original →
          </a>
        </div>

        {also_reported_html}

        <div class="news-action-row">
          <a href="/news/{featured['slug']}/" class="btn btn-primary btn-sm">Read Full Intelligence Brief →</a>
          <a href="{html.escape(featured['sourceUrl'])}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-sm">Original Source ↗</a>
        </div>
      </article>
    </div>'''

    # Grid items
    grid_html_list = []
    for item in regular_items:
        also_rep = ""
        if item.get("alsoReportedBy"):
            pills = "".join(f'<a href="{html.escape(ar["sourceUrl"])}" target="_blank" rel="noopener noreferrer" class="news-also-reported-pill">{html.escape(ar["sourceName"])}</a>' for ar in item["alsoReportedBy"])
            also_rep = f'''<div class="news-also-reported-pills">
              <span>Also reported by:</span>
              {pills}
            </div>'''

        grid_html_list.append(f'''      <article class="news-card" data-slug="{html.escape(item['slug'])}" data-region="{html.escape(item.get('region','Global'))}" data-topics="{html.escape(','.join(item.get('topics',[])))}" data-importance="{html.escape(item.get('importance','MEDIUM'))}" data-date="{html.escape(item.get('sourcePublishedAt',''))[:10]}" data-title="{html.escape(item['title'].lower())}" data-summary="{html.escape(item['subhead'].lower())}">
        <div class="news-badge-row">
          {render_badge_importance(item.get('importance','MEDIUM'))}
          {render_badge_verification(item.get('verificationStatus','REPORTED'))}
          <span class="badge-region">{html.escape(item.get('region','Global'))}</span>
        </div>

        <h3 class="news-card-title">
          <a href="/news/{item['slug']}/">{html.escape(item['title'])}</a>
        </h3>

        <p class="news-card-sub">{html.escape(item['subhead'])}</p>

        <!-- Clean Source Card -->
        <div class="news-source-card">
          <div class="news-source-left">
            <div class="news-source-avatar">{html.escape(item.get('sourceLogo', item['sourceName'][:2].upper()))}</div>
            <div class="news-source-info">
              <span class="news-source-name">{html.escape(item['sourceName'])}</span>
              <span class="news-source-meta">{format_date(item['sourcePublishedAt'])}</span>
            </div>
          </div>
          <a href="{html.escape(item['sourceUrl'])}" target="_blank" rel="noopener noreferrer" class="news-source-link" aria-label="Read original on {html.escape(item['sourceName'])}">
            Read original →
          </a>
        </div>

        {also_rep}

        <div class="news-card-footer">
          <span>{format_date(item['sourcePublishedAt'])}</span>
          <a href="/news/{item['slug']}/" class="news-card-readmore">Read full brief →</a>
        </div>
      </article>''')

    cards_grid_html = "\n".join(grid_html_list)

    total_published = len(news_items)
    last_scan_str = "Verified Today, 6:00 PM IST"
    if status.get("last_successful_scan"):
        try:
            dt = datetime.fromisoformat(status["last_successful_scan"].replace("Z", "+00:00"))
            last_scan_str = dt.strftime("%b %d, %Y at %I:%M %p UTC")
        except Exception:
            pass

    page_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ChatGPT Ads News: Global OpenAI Advertising Updates | Aepify</title>
  <meta name="description" content="Everything changing in ChatGPT advertising, in one place. Real-time verified updates, Ads Manager features, country rollouts, ad formats, and policy changes.">
  <link rel="canonical" href="https://aepify.com/news/">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="ChatGPT Ads News: Global OpenAI Advertising Updates | Aepify">
  <meta property="og:description" content="Everything changing in ChatGPT advertising, in one place. Real-time verified updates, ad formats, and advertiser intelligence.">
  <meta property="og:url" content="https://aepify.com/news/">
  <meta property="og:site_name" content="Aepify">
  <meta property="og:image" content="https://aepify.com/assets/blog/chatgpt-ads-context-hints-explained.png">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="ChatGPT Ads News | Aepify">
  <meta name="twitter:description" content="Everything changing in ChatGPT advertising, in one place. Real-time verified updates.">
  <meta name="twitter:image" content="https://aepify.com/assets/blog/chatgpt-ads-context-hints-explained.png">

  <!-- Fonts & Styles -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css?v=5.0">
  <link rel="icon" type="image/png" href="/favicon.png">

  {get_google_tag()}

  <!-- Schema.org CollectionPage -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "name": "ChatGPT Ads News",
    "description": "Everything changing in ChatGPT advertising, in one place.",
    "url": "https://aepify.com/news/",
    "publisher": {{
      "@type": "Organization",
      "name": "Aepify",
      "url": "https://aepify.com"
    }}
  }}
  </script>
</head>
<body>

  {get_site_header(active_nav="news")}

  <main class="news-main-container">
    
    <!-- HERO -->
    <header class="news-hero">
      <div class="news-eyebrow">
        <span class="pulse-dot"></span> LIVE INTELLIGENCE FEED
      </div>
      <h1 class="news-hero-title">ChatGPT Ads News</h1>
      <p class="news-hero-subtitle">Everything changing in ChatGPT advertising, in one place.</p>
    </header>

    <!-- INTELLIGENCE STATUS BAR -->
    <div class="news-status-bar">
      <div class="news-status-left">
        <div class="news-status-pill">
          <span class="pulse-dot"></span> Live Monitoring Active
        </div>
        <span class="news-status-divider">•</span>
        <div class="news-status-meta">Last Verified Scan: <strong>{html.escape(last_scan_str)}</strong></div>
        <span class="news-status-divider">•</span>
        <div class="news-status-meta">Sources: <strong>Tier 1 &amp; Tier 2 Global Publications</strong></div>
      </div>
      <div class="news-status-count">
        <span id="newsCountDisplay">{total_published}</span> Verified Briefs
      </div>
    </div>

    <!-- CONTROLS & MULTI-FILTER BAR -->
    <div class="news-controls">
      <!-- Search Input -->
      <div class="news-search-box">
        <svg class="news-search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input type="search" id="newsSearchInput" class="news-search-input" placeholder="Search by topic, country, company, or keyword (e.g. Ads Manager, India, DMA, formats)..." aria-label="Search news articles">
      </div>

      <!-- Region Filter Pills -->
      <div class="news-filter-group" id="regionFilters" role="radiogroup" aria-label="Filter by region">
        <span class="news-filter-label">Region:</span>
        <button type="button" class="news-pill active" data-filter="region" data-value="all">All</button>
        <button type="button" class="news-pill" data-filter="region" data-value="Global">Global</button>
        <button type="button" class="news-pill" data-filter="region" data-value="North America">North America</button>
        <button type="button" class="news-pill" data-filter="region" data-value="Europe">Europe &amp; UK</button>
        <button type="button" class="news-pill" data-filter="region" data-value="Asia">Asia &amp; India</button>
      </div>

      <!-- Topic Filter Pills -->
      <div class="news-filter-group" id="topicFilters" role="radiogroup" aria-label="Filter by topic">
        <span class="news-filter-label">Topic:</span>
        <button type="button" class="news-pill active" data-filter="topic" data-value="all">All Topics</button>
        <button type="button" class="news-pill" data-filter="topic" data-value="Ad Formats">Ad Formats</button>
        <button type="button" class="news-pill" data-filter="topic" data-value="Ads Manager">Ads Manager</button>
        <button type="button" class="news-pill" data-filter="topic" data-value="Product Updates">Product Updates</button>
        <button type="button" class="news-pill" data-filter="topic" data-value="Targeting">Targeting</button>
        <button type="button" class="news-pill" data-filter="topic" data-value="Measurement">Measurement</button>
        <button type="button" class="news-pill" data-filter="topic" data-value="Availability">Availability</button>
        <button type="button" class="news-pill" data-filter="topic" data-value="Policy">Policy</button>
      </div>
    </div>

    {featured_html}

    <!-- LATEST NEWS GRID -->
    <section>
      <h2 style="font-size: 1.5rem; font-weight: 800; margin: 0 0 20px; color: var(--color-news-black);">Latest Intelligence Briefs</h2>
      <div class="news-grid" id="newsGrid">
        {cards_grid_html}
      </div>

      <!-- Empty State Fallback -->
      <div class="news-empty-state" id="newsEmptyState" style="display: none;">
        <h3 class="news-empty-title">No Matching Intelligence Found</h3>
        <p class="news-empty-text">No verified ChatGPT Ads stories matched your current search filters. Try clearing your search query or selecting "All" regions.</p>
        <button type="button" class="btn btn-secondary btn-sm" id="resetFiltersBtn" style="margin-top: 14px;">Reset All Filters</button>
      </div>
    </section>

    <!-- CALL TO ACTION -->
    <div class="news-cta-banner">
      <h3 class="news-cta-title">Prepare Your Brand for ChatGPT Ads</h3>
      <p class="news-cta-desc">As OpenAI rolls out advertising placements, early movers will secure the lowest clearing prices. Request an audit of your brand's conversational opportunity score today.</p>
      <a href="https://tally.so/r/GxZpre" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
        Get Your Free Opportunity Report →
      </a>
    </div>

  </main>

  {get_site_footer()}

  <!-- CLIENT-SIDE SEARCH & FILTER CONTROLLER -->
  <script>
  document.addEventListener("DOMContentLoaded", function() {{
    const searchInput = document.getElementById("newsSearchInput");
    const regionPills = document.querySelectorAll('#regionFilters .news-pill');
    const topicPills = document.querySelectorAll('#topicFilters .news-pill');
    const newsCards = document.querySelectorAll(".news-card");
    const featuredCard = document.querySelector(".news-featured-card");
    const emptyState = document.getElementById("newsEmptyState");
    const countDisplay = document.getElementById("newsCountDisplay");
    const resetBtn = document.getElementById("resetFiltersBtn");

    // Mobile nav toggle
    const mobileToggle = document.getElementById("mobileToggle");
    const mobileMenu = document.getElementById("mobileMenu");
    if (mobileToggle && mobileMenu) {{
      mobileToggle.addEventListener("click", () => {{
        const open = mobileMenu.classList.toggle("open");
        mobileToggle.classList.toggle("active", open);
        mobileToggle.setAttribute("aria-expanded", open ? "true" : "false");
        document.body.classList.toggle("menu-open", open);
      }});
    }}

    let selectedRegion = "all";
    let selectedTopic = "all";
    let searchQuery = "";

    function filterStories() {{
      let visibleCount = 0;

      // Filter featured card
      if (featuredCard) {{
        const fRegion = featuredCard.getAttribute("data-region") || "";
        const fTopics = (featuredCard.getAttribute("data-topics") || "").split(",");
        const fText = (featuredCard.innerText || "").toLowerCase();

        const matchRegion = (selectedRegion === "all") || (fRegion.toLowerCase().includes(selectedRegion.toLowerCase()));
        const matchTopic = (selectedTopic === "all") || fTopics.some(t => t.trim().toLowerCase() === selectedTopic.toLowerCase());
        const matchSearch = !searchQuery || fText.includes(searchQuery);

        if (matchRegion && matchTopic && matchSearch) {{
          featuredCard.parentElement.style.display = "block";
          visibleCount++;
        }} else {{
          featuredCard.parentElement.style.display = "none";
        }}
      }}

      // Filter grid cards
      newsCards.forEach(card => {{
        const cRegion = card.getAttribute("data-region") || "";
        const cTopics = (card.getAttribute("data-topics") || "").split(",");
        const cTitle = card.getAttribute("data-title") || "";
        const cSummary = card.getAttribute("data-summary") || "";
        const cText = (card.innerText || "").toLowerCase();

        const matchRegion = (selectedRegion === "all") || (cRegion.toLowerCase().includes(selectedRegion.toLowerCase()));
        const matchTopic = (selectedTopic === "all") || cTopics.some(t => t.trim().toLowerCase() === selectedTopic.toLowerCase());
        const matchSearch = !searchQuery || cText.includes(searchQuery) || cTitle.includes(searchQuery) || cSummary.includes(searchQuery);

        if (matchRegion && matchTopic && matchSearch) {{
          card.style.display = "flex";
          visibleCount++;
        }} else {{
          card.style.display = "none";
        }}
      }});

      if (countDisplay) {{
        countDisplay.textContent = visibleCount;
      }}

      if (emptyState) {{
        emptyState.style.display = visibleCount === 0 ? "block" : "none";
      }}
    }}

    // Region Pills
    regionPills.forEach(pill => {{
      pill.addEventListener("click", () => {{
        regionPills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        selectedRegion = pill.getAttribute("data-value");
        filterStories();
      }});
    }});

    // Topic Pills
    topicPills.forEach(pill => {{
      pill.addEventListener("click", () => {{
        topicPills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        selectedTopic = pill.getAttribute("data-value");
        filterStories();
      }});
    }});

    // Search Input
    if (searchInput) {{
      searchInput.addEventListener("input", (e) => {{
        searchQuery = e.target.value.trim().toLowerCase();
        filterStories();
      }});
    }}

    // Reset button
    if (resetBtn) {{
      resetBtn.addEventListener("click", () => {{
        selectedRegion = "all";
        selectedTopic = "all";
        searchQuery = "";
        if (searchInput) searchInput.value = "";
        regionPills.forEach(p => p.classList.toggle("active", p.getAttribute("data-value") === "all"));
        topicPills.forEach(p => p.classList.toggle("active", p.getAttribute("data-value") === "all"));
        filterStories();
      }});
    }}
  }});
  </script>
</body>
</html>'''

    OUTPUT_NEWS_DIR.mkdir(parents=True, exist_ok=True)
    index_file = OUTPUT_NEWS_DIR / "index.html"
    index_file.write_text(page_html, encoding="utf-8")
    print(f"✓ Generated: news/index.html ({total_published} stories)")

def build_article_page(item, all_items):
    slug = item["slug"]
    article_dir = OUTPUT_NEWS_DIR / slug
    article_dir.mkdir(parents=True, exist_ok=True)

    title = item["title"]
    subhead = item["subhead"]
    pub_date = format_date(item["sourcePublishedAt"])
    source_name = item["sourceName"]
    source_url = item["sourceUrl"]
    source_author = item.get("sourceAuthor", "Editorial Desk")
    region = item.get("region", "Global")
    verification = item.get("verificationStatus", "CONFIRMED")
    importance = item.get("importance", "HIGH")
    logo = item.get("sourceLogo", source_name[:2].upper())

    # Format updates if any
    updates_html = ""
    if item.get("updates"):
        for upd in item["updates"]:
            upd_date = format_date(upd.get("date", item["sourcePublishedAt"]))
            updates_html += f'''    <div class="news-update-box">
      <div class="news-update-title">UPDATE — {html.escape(upd_date)}</div>
      <div class="news-update-content">{html.escape(upd.get("content",""))}</div>
    </div>'''

    # Format also reported by
    also_reported_html = ""
    if item.get("alsoReportedBy"):
        links = ", ".join(f'<a href="{html.escape(ar["sourceUrl"])}" target="_blank" rel="noopener noreferrer" style="color:var(--color-news-orange);font-weight:700;">{html.escape(ar["sourceName"])} ↗</a>' for ar in item["alsoReportedBy"])
        also_reported_html = f'''    <div class="news-section-box">
      <h3>ALSO REPORTED BY</h3>
      <p>This development was also independently verified and reported by: {links}.</p>
    </div>'''

    # Related news cards (up to 3 other items)
    related_items = [i for i in all_items if i["slug"] != slug][:3]
    related_html_list = []
    for r in related_items:
        related_html_list.append(f'''      <a href="/news/{r['slug']}/" class="news-related-card">
        <div class="news-badge-row" style="margin-bottom:8px;">
          {render_badge_verification(r.get('verificationStatus','REPORTED'))}
          <span class="badge-region">{html.escape(r.get('region','Global'))}</span>
        </div>
        <div class="news-related-card-title">{html.escape(r['title'])}</div>
        <div style="font-size:0.8rem;color:var(--color-news-muted);margin-top:6px;">{format_date(r['sourcePublishedAt'])}</div>
      </a>''')
    related_html = "\n".join(related_html_list)

    # Related blog posts
    related_blogs_html = ""
    if item.get("relatedBlogPosts"):
        blog_links = "".join(f'<li style="margin-bottom:8px;"><a href="{html.escape(bp["url"])}" style="color:var(--color-news-orange);font-weight:700;">{html.escape(bp["title"])} →</a></li>' for bp in item["relatedBlogPosts"])
        related_blogs_html = f'''    <div class="news-section-box">
      <h3>STRATEGIC RESOURCES &amp; ANALYSIS</h3>
      <ul style="list-style:none;padding-left:0;">
        {blog_links}
      </ul>
    </div>'''

    page_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} | Aepify News</title>
  <meta name="description" content="{html.escape(subhead)}">
  <link rel="canonical" href="https://aepify.com/news/{slug}/">

  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:title" content="{html.escape(title)} | Aepify News">
  <meta property="og:description" content="{html.escape(subhead)}">
  <meta property="og:url" content="https://aepify.com/news/{slug}/">
  <meta property="og:site_name" content="Aepify">
  <meta property="og:image" content="https://aepify.com/assets/blog/chatgpt-ads-context-hints-explained.png">
  <meta property="article:published_time" content="{html.escape(item.get('sourcePublishedAt',''))}">
  <meta property="article:modified_time" content="{html.escape(item.get('updatedAt', item.get('sourcePublishedAt','')))}">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title)} | Aepify News">
  <meta name="twitter:description" content="{html.escape(subhead)}">
  <meta name="twitter:image" content="https://aepify.com/assets/blog/chatgpt-ads-context-hints-explained.png">

  <!-- Fonts & Styles -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css?v=5.0">
  <link rel="icon" type="image/png" href="/favicon.png">

  {get_google_tag()}

  <!-- Schema.org NewsArticle -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    "headline": "{html.escape(title)}",
    "description": "{html.escape(subhead)}",
    "url": "https://aepify.com/news/{slug}/",
    "datePublished": "{html.escape(item.get('sourcePublishedAt',''))}",
    "dateModified": "{html.escape(item.get('updatedAt', item.get('sourcePublishedAt','')))}",
    "mainEntityOfPage": "https://aepify.com/news/{slug}/",
    "publisher": {{
      "@type": "Organization",
      "name": "Aepify",
      "url": "https://aepify.com"
    }},
    "author": {{
      "@type": "Organization",
      "name": "{html.escape(source_name)}"
    }}
  }}
  </script>
</head>
<body>

  {get_site_header(active_nav="news")}

  <main class="news-article-container">
    
    <!-- BREADCRUMB -->
    <nav class="news-breadcrumb" aria-label="Breadcrumb">
      <a href="/">Home</a>
      <span>/</span>
      <a href="/news/">News</a>
      <span>/</span>
      <span style="color:var(--color-news-black);">{html.escape(region)}</span>
    </nav>

    <!-- HEADER -->
    <header class="news-article-header">
      <div class="news-badge-row">
        {render_badge_importance(importance)}
        {render_badge_verification(verification)}
        <span class="badge-region">{html.escape(region)}</span>
      </div>

      <h1 class="news-article-title">{html.escape(title)}</h1>
      <p class="news-article-subhead">{html.escape(subhead)}</p>

      <div class="news-article-meta-row">
        <div class="news-article-meta-item">
          <span>Source:</span> <strong>{html.escape(source_name)}</strong>
        </div>
        <div class="news-article-meta-item">
          <span>Published:</span> <strong>{pub_date}</strong>
        </div>
        <div class="news-article-meta-item">
          <span>Region:</span> <strong>{html.escape(region)}</strong>
        </div>
        <div class="news-article-meta-item">
          <span>Verification:</span> <strong>{html.escape(verification)}</strong>
        </div>
      </div>
    </header>

    <!-- ORIGINAL SOURCE CARD / ATTRIBUTION PREVIEW -->
    <section class="news-article-source-card">
      <div class="news-article-source-top">
        <div class="news-source-left">
          <div class="news-source-avatar">{html.escape(logo)}</div>
          <div>
            <div class="news-article-source-badge">ORIGINAL REPORTING SOURCE</div>
            <div class="news-source-name" style="font-size:1.05rem;">{html.escape(source_name)}</div>
          </div>
        </div>
        <a href="{html.escape(source_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm">
          Read the original →
        </a>
      </div>
      <div class="news-article-source-headline">"{html.escape(title)}"</div>
      <div style="font-size:0.82rem;color:var(--color-news-muted);">Reported by {html.escape(source_author)} on {pub_date}</div>
      <p class="news-article-source-disclaimer">
        Source Attribution Note: Aepify's intelligence desk discovers, verifies, and analyzes global developments in ChatGPT advertising. Full journalistic reporting credit belongs to {html.escape(source_name)}.
      </p>
    </section>

    {updates_html}

    <!-- EDITORIAL INTELLIGENCE BLOCKS -->
    <article>
      <!-- WHAT HAPPENED -->
      <div class="news-section-box">
        <h3>WHAT HAPPENED</h3>
        <p>{html.escape(item.get('whatHappened',''))}</p>
      </div>

      <!-- WHY IT MATTERS -->
      <div class="news-section-box">
        <h3>WHY IT MATTERS</h3>
        <p>{html.escape(item.get('whyItMatters',''))}</p>
      </div>

      <!-- WHAT CHANGED -->
      <div class="news-section-box">
        <h3>WHAT CHANGED</h3>
        <p>{html.escape(item.get('whatChanged',''))}</p>
      </div>

      <!-- WHAT THIS COULD MEAN FOR ADVERTISERS -->
      <div class="news-section-box">
        <h3>WHAT THIS COULD MEAN FOR ADVERTISERS</h3>
        <p>{html.escape(item.get('advertiserImpact',''))}</p>
      </div>

      <!-- AEPIFY TAKE -->
      <div class="news-take-box">
        <h3>AEPIFY'S TAKE</h3>
        <p>{html.escape(item.get('aepifyTake',''))}</p>
      </div>

      {also_reported_html}
      {related_blogs_html}
    </article>

    <!-- RELATED INTELLIGENCE -->
    <section class="news-related-section">
      <h2 class="news-related-title">Related Intelligence Briefs</h2>
      <div class="news-related-grid">
        {related_html}
      </div>
    </section>

    <!-- BRIEFING CTA -->
    <div class="news-cta-banner">
      <h3 class="news-cta-title">Navigate ChatGPT Advertising with Aepify</h3>
      <p class="news-cta-desc">Stay ahead of every OpenAI advertising development. Get your brand audited for conversational readiness and ad placement eligibility.</p>
      <a href="https://tally.so/r/GxZpre" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
        Claim Your Opportunity Scan →
      </a>
    </div>

  </main>

  {get_site_footer()}

  <script>
  // Mobile drawer navigation toggle
  document.addEventListener("DOMContentLoaded", function() {{
    const mobileToggle = document.getElementById("mobileToggle");
    const mobileMenu = document.getElementById("mobileMenu");
    if (mobileToggle && mobileMenu) {{
      mobileToggle.addEventListener("click", () => {{
        const open = mobileMenu.classList.toggle("open");
        mobileToggle.classList.toggle("active", open);
        mobileToggle.setAttribute("aria-expanded", open ? "true" : "false");
        document.body.classList.toggle("menu-open", open);
      }});
    }}
  }});
  </script>
</body>
</html>'''

    article_file = article_dir / "index.html"
    article_file.write_text(page_html, encoding="utf-8")
    print(f"✓ Generated: news/{slug}/index.html")

def build_sitemaps(news_items):
    # 1. Update main sitemap.xml
    sitemap_file = BASE_DIR / "sitemap.xml"
    existing_content = sitemap_file.read_text(encoding="utf-8") if sitemap_file.exists() else ""

    # Parse existing URLs
    existing_urls = set(re.findall(r'<loc>(https://aepify\.com/[^<]+)</loc>', existing_content))

    # Add news index
    existing_urls.add("https://aepify.com/news/")

    # Add news items
    for item in news_items:
        existing_urls.add(f"https://aepify.com/news/{item['slug']}/")

    # Rebuild clean sitemap
    today_str = datetime.now().strftime("%Y-%m-%d")
    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    # Deterministic ordering
    for u in sorted(existing_urls):
        priority = "1.00" if u == "https://aepify.com/" else "0.90" if u in ["https://aepify.com/blog/", "https://aepify.com/news/"] else "0.80"
        changefreq = "daily" if "news" in u else "weekly"
        sitemap_lines.append(f'''  <url>
    <loc>{u}</loc>
    <lastmod>{today_str}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>''')

    sitemap_lines.append('</urlset>')
    sitemap_file.write_text("\n".join(sitemap_lines), encoding="utf-8")
    print(f"✓ Updated: sitemap.xml with {len(existing_urls)} total URLs")

    # 2. Generate Google News sitemap (news-sitemap.xml)
    news_sitemap_file = BASE_DIR / "news-sitemap.xml"
    news_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">'
    ]
    for item in news_items:
        pub_iso = item.get("sourcePublishedAt", f"{today_str}T00:00:00Z")
        news_lines.append(f'''  <url>
    <loc>https://aepify.com/news/{item['slug']}/</loc>
    <news:news>
      <news:publication>
        <news:name>Aepify News</news:name>
        <news:language>en</news:language>
      </news:publication>
      <news:publication_date>{pub_iso}</news:publication_date>
      <news:title>{html.escape(item['title'])}</news:title>
    </news:news>
  </url>''')
    news_lines.append('</urlset>')
    news_sitemap_file.write_text("\n".join(news_lines), encoding="utf-8")
    print(f"✓ Generated: news-sitemap.xml with {len(news_items)} news URLs")

def main():
    print("Starting Aepify News Hub Build...")
    news_items = load_news()
    status = load_status()

    # Filter only published items, sort by date descending
    published_items = [i for i in news_items if i.get("published", True)]
    published_items.sort(key=lambda x: x.get("sourcePublishedAt", ""), reverse=True)

    # Build Index Hub
    build_index_page(published_items, status)

    # Build each article page
    for item in published_items:
        build_article_page(item, published_items)

    # Build sitemaps
    build_sitemaps(published_items)

    print("\nAepify News Build completed successfully!")

if __name__ == "__main__":
    main()
