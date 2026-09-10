/**
 * AEPIFY WHO IT'S FOR (AUDIENCE SELECTOR)
 * Interactive card grid with live conversation preview
 */

(function () {
  'use strict';

  const audienceData = {
    home: {
      category: "HOME SERVICES",
      quote: "“How much should I budget for a full kitchen renovation?”",
      intent: "High-ticket home remodel & budget planning",
      audience: "Homeowners with immediate renovation intent",
      angle: "Transparent pricing guide + turnkey project management"
    },
    travel: {
      category: "TRAVEL",
      quote: "“Can you plan a luxury Italy trip without changing hotels every two days?”",
      intent: "High-end bespoke European vacation & private transfers",
      audience: "Affluent travelers seeking curated convenience",
      angle: "Private concierge itinerary with hand-picked boutique villas"
    },
    consulting: {
      category: "CONSULTING",
      quote: "“Do I need help restructuring my sales team?”",
      intent: "B2B Revenue Operations & quota realignment",
      audience: "Founders & CEOs at $2M-$10M ARR",
      angle: "Fractional VP Sales Diagnostic & Org Blueprint"
    },
    professional: {
      category: "PROFESSIONAL SERVICES",
      quote: "“When should an SMB switch from accounting software to a fractional CFO?”",
      intent: "Financial strategy, cash flow modeling & runway extension",
      audience: "Growing SMBs outgrowing basic bookkeeping",
      angle: "High-impact financial roadmapping & capital advisory"
    },
    local: {
      category: "LOCAL BUSINESSES",
      quote: "“Which boutique clinic specializes in Invisalign for adults in central London?”",
      intent: "High-value elective cosmetic dental treatment",
      audience: "Local high-intent buyers ready to schedule consultations",
      angle: "3D Smile Simulation & direct consultation reservation"
    },
    premium: {
      category: "PREMIUM SERVICES",
      quote: "“How do I select an executive coach for senior leadership onboarding?”",
      intent: "Executive leadership development & enterprise retention",
      audience: "HR executives & C-suite leaders evaluating coaches",
      angle: "Tailored 1:1 confidential leadership acceleration"
    }
  };

  const cards = document.querySelectorAll('.audience-card');
  const elCategory = document.getElementById('audPrevCategory');
  const elQuote = document.getElementById('audPrevQuote');
  const elIntent = document.getElementById('audPrevIntent');
  const elAudience = document.getElementById('audPrevAudience');
  const elAngle = document.getElementById('audPrevAngle');

  function updateAudience(key) {
    const data = audienceData[key];
    if (!data) return;

    cards.forEach(function (c) {
      c.classList.toggle('active', c.getAttribute('data-cat') === key);
    });

    if (elCategory) elCategory.textContent = data.category;
    if (elQuote) elQuote.textContent = data.quote;
    if (elIntent) elIntent.textContent = data.intent;
    if (elAudience) elAudience.textContent = data.audience;
    if (elAngle) elAngle.textContent = data.angle;
  }

  cards.forEach(function (card) {
    card.addEventListener('click', function () {
      const key = this.getAttribute('data-cat');
      updateAudience(key);
    });
  });
})();
