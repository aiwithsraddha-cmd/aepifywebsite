#!/usr/bin/env python3
"""
daily_publisher.py - Consistent Daily Blog Publishing System for Aepify
Enforces:
  - EXACTLY ONE article per day
  - Fixed 6-category rotation:
      1. ChatGPT Ads
      2. AI Marketing
      3. Performance Marketing
      4. Growth Marketing
      5. Marketing Strategy
      6. AEO & GEO
  - Persistent state in publishing_state.json
  - Quality, SEO, AEO, GEO, and mobile checks
  - Rebuilding static site via build_blog.py
"""

import sys
import os
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "publishing_state.json"
CONTENT_DIR = BASE_DIR / "content" / "blog"
BUILD_SCRIPT = BASE_DIR / "build_blog.py"

ROTATION_ORDER = [
    "ChatGPT Ads",
    "AI Marketing",
    "Performance Marketing",
    "Growth Marketing",
    "Marketing Strategy",
    "AEO & GEO"
]

CATEGORY_TOPIC_CURRICULUM = {
    "ChatGPT Ads": [
        "What are ChatGPT Ads?",
        "How ChatGPT Ads work",
        "ChatGPT Ads vs Google Ads",
        "ChatGPT Ads vs Meta Ads",
        "How businesses can prepare for ChatGPT Ads",
        "How to build a ChatGPT Ads campaign",
        "ChatGPT Ads campaign structure",
        "ChatGPT Ads context hints",
        "ChatGPT Ads ad groups",
        "ChatGPT Ads creative strategy",
        "ChatGPT Ads targeting",
        "ChatGPT Ads measurement",
        "ChatGPT Ads optimisation",
        "Common ChatGPT Ads mistakes",
        "Who should consider ChatGPT Ads?",
        "When ChatGPT Ads may not be the right channel",
        "How buyer conversations can inform ChatGPT Ads strategy",
        "How to identify high-intent conversations",
        "How to test ChatGPT Ads before scaling"
    ],
    "AI Marketing": [
        "How AI is changing digital marketing",
        "How customers use AI before buying",
        "AI and customer research",
        "AI and product discovery",
        "AI and brand discovery",
        "AI-powered marketing strategies",
        "AI and demand generation",
        "AI and conversion optimisation",
        "AI-assisted marketing workflows",
        "How marketers should adapt to AI-first behaviour",
        "AI marketing vs traditional digital marketing",
        "The changing marketing funnel",
        "AI and customer decision-making",
        "AI and content discovery",
        "The future of AI marketing"
    ],
    "Performance Marketing": [
        "Performance marketing in the AI era",
        "Measuring emerging advertising channels",
        "CAC and customer quality",
        "ROAS vs profitability",
        "Conversion tracking in conversational search",
        "Attribution challenges",
        "Incrementality testing",
        "Campaign experimentation frameworks",
        "Creative testing in conversational formats",
        "Landing page optimisation vs conversational funnels",
        "Performance reporting and metrics",
        "Campaign optimisation",
        "Testing new acquisition channels",
        "How to evaluate an emerging ad platform",
        "Clicks vs meaningful conversions",
        "Why high CTR does not always mean high-quality demand",
        "How campaign data should influence strategy",
        "How to build a performance marketing testing framework"
    ],
    "Growth Marketing": [
        "How to identify new acquisition channels",
        "Growth experiments",
        "Channel validation",
        "Customer acquisition strategy",
        "Demand generation",
        "Growth loops",
        "Experiment prioritisation",
        "Testing emerging platforms",
        "How startups should test new channels",
        "How to allocate experimental marketing budgets",
        "Finding product-market-channel fit",
        "Growth marketing vs performance marketing",
        "Building a repeatable acquisition system",
        "How to turn marketing experiments into growth channels",
        "When to stop an underperforming marketing experiment"
    ],
    "Marketing Strategy": [
        "How to build a modern marketing strategy",
        "Positioning strategy",
        "Customer journey mapping in AI environments",
        "Customer segmentation",
        "Messaging strategy",
        "Offer strategy",
        "Acquisition strategy",
        "Channel strategy",
        "Demand generation strategy",
        "Marketing experimentation",
        "Competitive positioning",
        "Brand vs performance marketing",
        "How to choose marketing channels",
        "How to build a go-to-market strategy",
        "Marketing strategy for emerging platforms",
        "How customer behaviour should influence strategy"
    ],
    "AEO & GEO": [
        "What is AEO?",
        "What is GEO?",
        "AEO vs SEO",
        "GEO vs SEO",
        "How AI answer engines change content discovery",
        "How businesses can prepare for AI discovery",
        "How to structure content for answer engines",
        "Entity clarity",
        "Topical authority",
        "First-hand experience and AI discovery",
        "How citations influence trustworthy content",
        "Question-led content",
        "Structured content for AI systems",
        "SEO + AEO + GEO integration",
        "How brands can improve their AI discovery presence",
        "Common GEO misconceptions",
        "What GEO cannot guarantee"
    ]
}

BANNED_INTRO_PHRASES = [
    "in today's rapidly evolving",
    "in today’s rapidly evolving",
    "with the rise of ai",
    "in the ever-changing world of marketing",
    "businesses today are constantly looking for",
    "in an era where ai",
    "in the fast-paced world of digital marketing"
]

def load_state():
    if not STATE_FILE.exists():
        sys.exit(f"Error: {STATE_FILE} not found. Initialize first.")
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def calculate_next_rotation(state):
    last_cat = state.get("last_published_category")
    if last_cat not in ROTATION_ORDER:
        return ROTATION_ORDER[0], 0
    last_idx = ROTATION_ORDER.index(last_cat)
    next_idx = (last_idx + 1) % len(ROTATION_ORDER)
    return ROTATION_ORDER[next_idx], next_idx

def parse_frontmatter(content):
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    yaml_str = parts[1].strip()
    body = parts[2].strip()
    meta = {}
    for line in yaml_str.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([a-zA-Z0-9_-]+):\s*(.*)$", line)
        if m:
            k, v = m.group(1), m.group(2).strip().strip("\"'")
            meta[k] = v
    return meta, body

def show_status():
    state = load_state()
    next_cat, next_idx = calculate_next_rotation(state)
    last_date = state.get("last_published_date", "None")
    today_str = datetime.now().strftime("%Y-%m-%d")
    already_published_today = (last_date == today_str)

    print("==================================================")
    print("      AEPIFY DAILY BLOG PUBLISHING SYSTEM        ")
    print("==================================================")
    print(f"Today's Date:           {today_str}")
    print(f"Last Published Date:    {last_date}")
    print(f"Last Category:          {state.get('last_published_category', 'None')}")
    print(f"Total Published:        {state.get('total_published', len(state.get('history', [])))}")
    print(f"Status for Today:       {'ALREADY PUBLISHED' if already_published_today else 'READY TO PUBLISH'}")
    print("--------------------------------------------------")
    print(f"NEXT CATEGORY IN ROTATION: >>> {next_cat} <<< (Position {next_idx + 1}/6)")
    print("--------------------------------------------------")
    print("Upcoming 6-Day Cycle:")
    for i in range(len(ROTATION_ORDER)):
        idx = (next_idx + i) % len(ROTATION_ORDER)
        print(f"  Day {i+1}: {ROTATION_ORDER[idx]}")
    print("==================================================")

def recommend_topic(category=None):
    state = load_state()
    if not category:
        category, _ = calculate_next_rotation(state)

    print(f"\nTarget Category: [{category}]")
    existing_titles = [h['title'].lower() for h in state.get('history', []) if h.get('category') == category]
    existing_slugs = [h['slug'] for h in state.get('history', []) if h.get('category') == category]

    print("\nPublished in this category so far:")
    for s in existing_slugs:
        print(f"  - {s}")

    candidates = CATEGORY_TOPIC_CURRICULUM.get(category, [])
    print("\nTopical Curriculum Candidates (Unpublished gaps):")
    gap_count = 0
    for cand in candidates:
        cand_lower = cand.lower()
        if not any(cand_lower in t or t in cand_lower for t in existing_titles):
            gap_count += 1
            print(f"  {gap_count}. {cand}")

def validate_article(file_path, bypass_date_check=False):
    path = Path(file_path)
    if not path.exists():
        return False, f"File not found: {file_path}"

    content = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)
    state = load_state()
    next_cat, _ = calculate_next_rotation(state)

    errors = []

    # 1. Frontmatter fields
    required_fields = ["title", "slug", "description", "category", "author", "publishedAt", "seoTitle", "metaDescription", "featuredImage", "readingTime"]
    for rf in required_fields:
        if rf not in meta or not meta[rf]:
            errors.append(f"Missing required frontmatter field: '{rf}'")

    cat = meta.get("category", "")
    if cat != next_cat:
        errors.append(f"Category mismatch! Expected next category in rotation: '{next_cat}', but article has: '{cat}'.")

    # 2. Daily frequency rule
    pub_date = meta.get("publishedAt", "")
    last_date = state.get("last_published_date", "")
    if not bypass_date_check and pub_date == last_date:
        errors.append(f"An article was already published on {pub_date}! Rule: EXACTLY ONE blog per day.")

    # 3. Slug uniqueness
    slug = meta.get("slug", "")
    existing_slugs = [h["slug"] for h in state.get("history", [])]
    if slug in existing_slugs:
        errors.append(f"Slug '{slug}' is already published in history!")

    # 4. Word count check
    words = len(re.findall(r"\w+", body))
    if words < 1000:
        errors.append(f"Article is too short: {words} words. Required minimum is 1,200 words (or 1,000 for tight technical briefs).")

    # 5. Banned intro phrases check
    body_lower = body[:800].lower()
    for banned in BANNED_INTRO_PHRASES:
        if banned in body_lower:
            errors.append(f"Article intro contains banned generic cliché: '{banned}'. Start directly with the core problem or insight.")

    # 6. Internal links check
    internal_links = re.findall(r"\[([^\]]+)\]\((/(?:blog|#[a-z0-9-]+)[^)]*|https://aepify\.com/[^)]*)\)", body)
    if len(internal_links) < 2:
        errors.append(f"Insufficient internal links: Found {len(internal_links)}. Must include at least 2 internal links to existing Aepify articles or pages.")

    # 7. SEO metadata checks
    seo_title = meta.get("seoTitle", "")
    if len(seo_title) < 40 or len(seo_title) > 75:
        errors.append(f"SEO title length is {len(seo_title)} chars. Recommended: 50–70 chars.")

    meta_desc = meta.get("metaDescription", "")
    if len(meta_desc) < 110 or len(meta_desc) > 175:
        errors.append(f"Meta description length is {len(meta_desc)} chars. Recommended: 130–165 chars.")

    # 8. AEO direct answer check
    if not any(pattern in body for pattern in ["article-takeaway-box", "article-callout", "Executive Summary", "Key Takeaways"]):
        errors.append("AEO Direct Answer / Executive Summary block is missing. Add an article-takeaway-box or direct answer near the beginning.")

    if errors:
        return False, "\n".join(f"  ❌ {e}" for e in errors)

    return True, f"✓ Article '{meta.get('title')}' ({words} words) passed all validations for category [{cat}]."

def publish_article(file_path, bypass_date_check=False, funnel_stage="MOFU"):
    valid, msg = validate_article(file_path, bypass_date_check=bypass_date_check)
    if not valid:
        print("VALIDATION FAILED:")
        print(msg)
        sys.exit(1)

    path = Path(file_path)
    content = path.read_text(encoding="utf-8")
    meta, _ = parse_frontmatter(content)

    slug = meta["slug"]
    target_dest = CONTENT_DIR / f"{slug}.md"

    # Copy markdown to content/blog/
    target_dest.write_text(content, encoding="utf-8")
    print(f"✓ Saved article to {target_dest}")

    # Rebuild static site
    print("\nRunning Static Site Generator (build_blog.py)...")
    res = subprocess.run([sys.executable, str(BUILD_SCRIPT)], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ build_blog.py failed:\n{res.stderr}")
        sys.exit(1)
    print(res.stdout.strip())

    # Update publishing state
    state = load_state()
    cat = meta["category"]
    next_cat, next_idx = calculate_next_rotation(state)

    new_entry = {
        "cycle": (len(state.get("history", [])) // 6) + 1,
        "day": len(state.get("history", [])) + 1,
        "date": meta["publishedAt"],
        "category": cat,
        "slug": slug,
        "title": meta["title"],
        "url": f"https://aepify.com/blog/{slug}/",
        "primary_keyword": meta.get("tags", [cat])[0] if isinstance(meta.get("tags"), list) else cat,
        "funnel_stage": funnel_stage,
        "status": "published"
    }

    state["history"].append(new_entry)
    state["last_published_date"] = meta["publishedAt"]
    state["last_published_category"] = cat
    state["total_published"] = len(state["history"])

    # Advance rotation
    future_cat, future_idx = calculate_next_rotation(state)
    state["current_rotation_position"] = future_idx + 1
    state["next_category"] = future_cat

    save_state(state)
    print(f"\n🎉 Successfully published '{meta['title']}'!")
    print(f"   Published Date: {meta['publishedAt']}")
    print(f"   Category:       {cat}")
    print(f"   URL:            https://aepify.com/blog/{slug}/")
    print(f"   Next Category in Rotation: >>> {future_cat} <<<")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 daily_publisher.py [status|next|validate <file>|publish <file> [--force]]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "status":
        show_status()
    elif cmd in ["next", "topics"]:
        cat = sys.argv[2] if len(sys.argv) > 2 else None
        recommend_topic(cat)
    elif cmd == "validate":
        if len(sys.argv) < 3:
            sys.exit("Error: Please provide path to markdown file.")
        force = "--force" in sys.argv
        valid, msg = validate_article(sys.argv[2], bypass_date_check=force)
        print(msg)
    elif cmd == "publish":
        if len(sys.argv) < 3:
            sys.exit("Error: Please provide path to markdown file.")
        force = "--force" in sys.argv
        stage = "MOFU"
        if "--stage" in sys.argv:
            idx = sys.argv.index("--stage")
            if idx + 1 < len(sys.argv):
                stage = sys.argv[idx + 1].upper()
        publish_article(sys.argv[2], bypass_date_check=force, funnel_stage=stage)
    else:
        print(f"Unknown command: {cmd}")
        print("Available commands: status, next, validate, publish")

if __name__ == "__main__":
    main()
