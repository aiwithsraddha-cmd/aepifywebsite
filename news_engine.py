#!/usr/bin/env python3
"""
news_engine.py - Global News Monitoring, Verification, Deduplication & Publishing Engine
Monitors Tier 1 (OpenAI official) and Tier 2 (Reuters, TechCrunch, Verge, Search Engine Land, etc.)
Filters for ChatGPT Ads & OpenAI advertising developments.
Deduplicates, verifies, generates structured analytical briefs, updates data/news.json,
and rebuilds static news pages via build_news.py.
"""

import sys
import os
import re
import json
import subprocess
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from difflib import SequenceMatcher

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
NEWS_FILE = DATA_DIR / "news.json"
STATUS_FILE = DATA_DIR / "news_status.json"
BUILD_SCRIPT = BASE_DIR / "build_news.py"

# Monitored Sources Configuration (Tier 1 & Tier 2)
SOURCES_CONFIG = [
    {
        "name": "OpenAI Newsroom & Updates",
        "tier": 1,
        "region": "Global",
        "url": "https://openai.com/news/rss.xml",
        "type": "rss",
        "defaultVerification": "CONFIRMED"
    },
    {
        "name": "TechCrunch (Enterprise & AI)",
        "tier": 2,
        "region": "North America",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "type": "rss",
        "defaultVerification": "REPORTED"
    },
    {
        "name": "Search Engine Land",
        "tier": 2,
        "region": "North America",
        "url": "https://searchengineland.com/feed",
        "type": "rss",
        "defaultVerification": "REPORTED"
    },
    {
        "name": "The Verge (Tech & AI)",
        "tier": 2,
        "region": "North America",
        "url": "https://www.theverge.com/rss/index.xml",
        "type": "rss",
        "defaultVerification": "REPORTED"
    },
    {
        "name": "Adweek Media & Tech",
        "tier": 2,
        "region": "North America",
        "url": "https://www.adweek.com/feed/",
        "type": "rss",
        "defaultVerification": "REPORTED"
    },
    {
        "name": "Digiday",
        "tier": 2,
        "region": "North America",
        "url": "https://digiday.com/feed/",
        "type": "rss",
        "defaultVerification": "REPORTED"
    }
]

# Strict Relevance Keywords (Must match at least one advertising trigger)
PRIMARY_AD_KEYWORDS = [
    "chatgpt ads",
    "openai ads",
    "chatgpt advertising",
    "openai advertising",
    "ads manager",
    "sponsored search",
    "sponsored placement",
    "conversational ad",
    "conversational advertising",
    "chatgpt sponsored",
    "ad monetization",
    "ad formats",
    "ad-supported"
]

# Secondary validation keywords (must appear alongside OpenAI or ChatGPT)
SECONDARY_AD_KEYWORDS = [
    "advertising",
    "advertiser",
    "monetization",
    "sponsored link",
    "commercial search",
    "ad format",
    "ad revenue",
    "sponsored result"
]

def load_news():
    if not NEWS_FILE.exists():
        return []
    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_news(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_status():
    if not STATUS_FILE.exists():
        return {
            "last_successful_scan": None,
            "next_scheduled_scan": None,
            "stories_discovered": 0,
            "stories_published": 0,
            "duplicate_stories_merged": 0,
            "stories_skipped_low_importance": 0,
            "failed_sources": 0,
            "pending_verification": 0
        }
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_status(status):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)

def slugify(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")

def is_relevant_story(title, summary=""):
    full_text = f"{title} {summary}".lower()
    
    # Direct match on primary ad keywords
    for kw in PRIMARY_AD_KEYWORDS:
        if kw in full_text:
            return True, kw
            
    # OpenAI/ChatGPT combined with secondary ad keywords
    has_brand = ("openai" in full_text) or ("chatgpt" in full_text)
    if has_brand:
        for skw in SECONDARY_AD_KEYWORDS:
            if skw in full_text:
                return True, f"brand+{skw}"
                
    return False, None

def calculate_similarity(text1, text2):
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def find_duplicate(candidate_title, candidate_url, existing_news):
    for story in existing_news:
        # Exact URL match
        if story.get("sourceUrl") == candidate_url:
            return story, "exact_url"
            
        # Also reported by match
        for ar in story.get("alsoReportedBy", []):
            if ar.get("sourceUrl") == candidate_url:
                return story, "also_reported_url"
                
        # Semantic title similarity (> 0.70)
        sim = calculate_similarity(candidate_title, story.get("title", ""))
        if sim > 0.70:
            return story, f"semantic_title ({sim:.2f})"
            
    return None, None

def assess_importance(title, summary=""):
    full_text = f"{title} {summary}".lower()
    if any(k in full_text for k in ["confirms", "launches", "official", "rollout", "unveils", "breaking"]):
        return "BREAKING"
    elif any(k in full_text for k in ["ads manager", "targeting", "ad format", "expansion", "bidding", "measurement"]):
        return "HIGH"
    return "MEDIUM"

def detect_region(title, summary=""):
    full_text = f"{title} {summary}".lower()
    if any(k in full_text for k in ["europe", "eu", "dma", "gdpr", "uk", "britain"]):
        return "Europe"
    elif any(k in full_text for k in ["india", "bengaluru", "mumbai", "delhi", "japan", "tokyo", "asia"]):
        return "Asia"
    elif any(k in full_text for k in ["united states", "us", "u.s.", "north america"]):
        return "North America"
    elif any(k in full_text for k in ["middle east", "uae", "dubai"]):
        return "Middle East"
    elif any(k in full_text for k in ["latin america", "brazil"]):
        return "Latin America"
    return "Global"

def fetch_rss_feed(source):
    url = source["url"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Aepify-News-Crawler/1.0"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            content = response.read()
            root = ET.fromstring(content)
            items = []
            
            # Parse RSS 2.0 or Atom
            for item in root.findall(".//item"):
                title_elem = item.find("title")
                link_elem = item.find("link")
                pub_elem = item.find("pubDate")
                desc_elem = item.find("description")
                
                title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
                link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                pub_date = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else datetime.now(timezone.utc).isoformat()
                desc = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""
                
                # Strip HTML tags from description
                desc_clean = re.sub(r"<[^>]+>", "", desc).strip()
                
                if title and link:
                    items.append({
                        "title": title,
                        "url": link,
                        "publishedAt": pub_date,
                        "summary": desc_clean,
                        "sourceName": source["name"],
                        "tier": source["tier"],
                        "defaultVerification": source["defaultVerification"],
                        "region": source["region"]
                    })
            return items
    except Exception as e:
        # Gracefully log failure without crashing
        print(f"   ⚠️ Source scan error for {source['name']}: {e}")
        return []

def run_scan():
    print("==================================================")
    print("      AEPIFY CHATGPT ADS NEWS MONITORING         ")
    print("==================================================")
    now_iso = datetime.now(timezone.utc).isoformat()
    status = load_status()
    existing_news = load_news()
    
    print(f"Scanning {len(SOURCES_CONFIG)} Global Tier 1 & Tier 2 sources...")
    
    discovered_count = 0
    newly_published = 0
    duplicates_merged = 0
    failed_sources = 0
    
    for src in SOURCES_CONFIG:
        print(f" • Checking [{src['name']}] (Tier {src['tier']})...")
        items = fetch_rss_feed(src)
        if not items:
            failed_sources += 1
            continue
            
        for item in items:
            relevant, trigger = is_relevant_story(item["title"], item["summary"])
            if not relevant:
                continue
                
            discovered_count += 1
            print(f"   🔍 Candidate Detected: \"{item['title'][:65]}...\" (Trigger: {trigger})")
            
            # Deduplication Check
            dup_story, dup_reason = find_duplicate(item["title"], item["url"], existing_news)
            if dup_story:
                print(f"      ↳ Matched existing story ({dup_reason}). Merging into 'alsoReportedBy'...")
                # Add to alsoReportedBy if not already there
                existing_urls = [ar["sourceUrl"] for ar in dup_story.get("alsoReportedBy", [])]
                if item["url"] not in existing_urls and item["url"] != dup_story.get("sourceUrl"):
                    dup_story.setdefault("alsoReportedBy", []).append({
                        "sourceName": item["sourceName"],
                        "sourceUrl": item["url"]
                    })
                    dup_story["updatedAt"] = now_iso
                    duplicates_merged += 1
                continue
                
            # Create new structured article
            slug = slugify(item["title"])
            # Ensure unique slug
            base_slug = slug
            counter = 1
            while any(n.get("slug") == slug for n in existing_news):
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            importance = assess_importance(item["title"], item["summary"])
            region = detect_region(item["title"], item["summary"])
            verification = "CONFIRMED" if "reportedly" not in item["title"].lower() and item["tier"] == 1 else "REPORTED"
            
            new_story = {
                "id": f"news-{len(existing_news)+1:03d}",
                "slug": slug,
                "title": item["title"],
                "subhead": item["summary"][:200] if item["summary"] else f"Latest verified developments regarding {item['title']}.",
                "category": "ChatGPT Ads News",
                "topics": ["Product Updates", "Industry"],
                "importance": importance,
                "verificationStatus": verification,
                "region": region,
                "country": region,
                "sourceName": item["sourceName"],
                "sourceUrl": item["url"],
                "sourceAuthor": "Industry Bureau",
                "sourcePublishedAt": now_iso,
                "detectedAt": now_iso,
                "updatedAt": now_iso,
                "sourceLanguage": "en",
                "sourceLogo": item["sourceName"][:2].upper(),
                "whatHappened": f"Official reporting indicates: {item['summary'] or item['title']}.",
                "whyItMatters": "This development directly affects how brands, agencies, and performance marketers plan commercial placements and budget allocation inside OpenAI's conversational surface.",
                "whatChanged": "Expands the capability footprint and monetization availability of conversational search ad placements.",
                "advertiserImpact": "Advertisers should monitor account eligibility and review contextual prompt keywords.",
                "aepifyTake": "Aepify's take: The strategic impact here is another indicator of conversational search maturation. Advertisers should prepare their brand entity clarity and testing strategy early.",
                "updates": [],
                "alsoReportedBy": [],
                "relatedBlogPosts": [
                    {"title": "What Are ChatGPT Ads? The Complete Strategic Guide", "url": "/blog/what-are-chatgpt-ads/"},
                    {"title": "ChatGPT Ads Context Hints Explained", "url": "/blog/chatgpt-ads-context-hints-explained/"}
                ],
                "published": True
            }
            
            existing_news.insert(0, new_story)
            newly_published += 1
            print(f"      ✅ Published new intelligence brief: /news/{slug}/")

    # Update state
    status["last_successful_scan"] = now_iso
    status["stories_discovered"] = status.get("stories_discovered", 0) + discovered_count
    status["stories_published"] = len(existing_news)
    status["duplicate_stories_merged"] = status.get("duplicate_stories_merged", 0) + duplicates_merged
    status["failed_sources"] = failed_sources
    
    save_news(existing_news)
    save_status(status)
    
    print("\nScan complete!")
    print(f"Discovered: {discovered_count} | Published New: {newly_published} | Duplicates Merged: {duplicates_merged}")
    
    # Automatically trigger static build
    print("\nRunning Static Site Generator for News (build_news.py)...")
    res = subprocess.run([sys.executable, str(BUILD_SCRIPT)], capture_output=True, text=True)
    if res.returncode == 0:
        print(res.stdout.strip())
    else:
        print(f"❌ build_news.py error:\n{res.stderr}")

def show_status():
    status = load_status()
    news = load_news()
    print("==================================================")
    print("       AEPIFY NEWS INTELLIGENCE STATUS            ")
    print("==================================================")
    print(f"Last Successful Scan:     {status.get('last_successful_scan', 'Never')}")
    print(f"Total Stories In DB:      {len(news)}")
    print(f"Published to Feed:        {len([n for n in news if n.get('published', True)])}")
    print(f"Duplicates Merged:        {status.get('duplicate_stories_merged', 0)}")
    print(f"Skipped Low-Importance:   {status.get('stories_skipped_low_importance', 0)}")
    print(f"Active Monitored Sources: {len(SOURCES_CONFIG)}")
    print("--------------------------------------------------")
    print("Recent News Items:")
    for n in news[:5]:
        print(f" • [{n.get('importance','MED')}] [{n.get('verificationStatus','CONFIRMED')}] {n['title'][:60]}... ({n.get('region','Global')})")
    print("==================================================")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 news_engine.py [scan|status|build]")
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    if cmd == "status":
        show_status()
    elif cmd in ["scan", "crawl"]:
        run_scan()
    elif cmd == "build":
        subprocess.run([sys.executable, str(BUILD_SCRIPT)])
    else:
        print(f"Unknown command: {cmd}. Available: scan, status, build")

if __name__ == "__main__":
    main()
