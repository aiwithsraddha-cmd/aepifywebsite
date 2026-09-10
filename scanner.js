/**
 * AEPIFY OPPORTUNITY SCAN ENGINE
 * Core functional tool: Multi-stage scan simulator with realistic intent mapping
 * and extensible architecture for live backend/API connection.
 */

(function () {
  'use strict';

  // Config: Set to true if a live API endpoint is configured
  const USE_LIVE_API = false;
  const LIVE_API_ENDPOINT = '/api/scan';

  const form = document.getElementById('scanForm');
  const inputUrl = document.getElementById('scanUrlInput');
  const btnSubmit = document.getElementById('btnScanSubmit');
  const loader = document.getElementById('scanLoader');
  const progressFill = document.getElementById('loaderProgressFill');
  const stepMsg = document.getElementById('scanStepMsg');
  const substepMsg = document.getElementById('scanSubstepMsg');
  const resultsContainer = document.getElementById('scanResults');

  // Result Fields
  const resDomain = document.getElementById('resDomain');
  const resCategory = document.getElementById('resCategory');
  const resProblem = document.getElementById('resProblem');
  const resProblemDesc = document.getElementById('resProblemDesc');
  const resConversation = document.getElementById('resConversation');
  const resOpportunity = document.getElementById('resOpportunity');
  const resOpportunityDesc = document.getElementById('resOpportunityDesc');
  const resAdAngle = document.getElementById('resAdAngle');
  const resAdUrl = document.getElementById('resAdUrl');
  const btnClaim = document.getElementById('btnClaimOpportunities');

  // Preset buttons
  const presetPills = document.querySelectorAll('.preset-pill');

  /**
   * Domain analysis heuristics for realistic simulation
   */
  function analyzeDomainHeuristics(rawUrl) {
    let clean = rawUrl.trim().toLowerCase();
    clean = clean.replace(/^(https?:\/\/)?(www\.)?/, '').replace(/\/.*$/, '');
    if (!clean) clean = 'yourwebsite.com';

    if (clean.includes('reno') || clean.includes('build') || clean.includes('arch') || clean.includes('home')) {
      return {
        domain: clean,
        category: "Home Remodeling & Architecture",
        problem: "Planning a major home renovation",
        problemDesc: "Homeowners need transparent budget planning, scope estimates, and architect vs contractor guidance.",
        conversation: "“We’re renovating a 20-year-old house. Should we redo the kitchen and bathrooms together or separately?”",
        opportunity: "High-Budget Renovation Scoping & Cost Transparency",
        opportunityDesc: "Position your service directly when homeowners calculate budgets and explore design-build firms.",
        adAngle: "“Planning a major renovation? Know the real cost before construction begins. One unified team from design to completion.”",
        adLink: "Schedule Design Walkthrough →"
      };
    }

    if (clean.includes('trip') || clean.includes('travel') || clean.includes('villa') || clean.includes('tour') || clean.includes('escape')) {
      return {
        domain: clean,
        category: "Luxury Travel & Concierge",
        problem: "High-end bespoke European vacation logistics",
        problemDesc: "Affluent travelers want curated private stays without the logistical headache of fragmented booking.",
        conversation: "“Can you plan a 10-day luxury Italy trip without changing hotels every two days?”",
        opportunity: "Frictionless Curated Concierge Travel",
        opportunityDesc: "Capture travelers while they formulate multi-city luxury vacation itineraries.",
        adAngle: "“Luxury European travel made effortless. Private drivers, hand-picked villas, zero logistics friction.”",
        adLink: "Request Custom Itinerary →"
      };
    }

    if (clean.includes('sales') || clean.includes('advisory') || clean.includes('consult') || clean.includes('ops') || clean.includes('growth')) {
      return {
        domain: clean,
        category: "B2B Advisory & Sales Consulting",
        problem: "Sales organization restructuring & scaling beyond $5M",
        problemDesc: "CEOs and founders face quota misalignment and slowing rep ramp times as they scale.",
        conversation: "“Do I need help restructuring my sales team after hitting $5M ARR?”",
        opportunity: "Executive Sales Architecture & Diagnostics",
        opportunityDesc: "Target leadership at the exact inflection point when they search for organizational blueprints.",
        adAngle: "“Scaling past $5M? Fix sales enablement and quota structure before hiring more reps.”",
        adLink: "Book 30-Min Diagnostic →"
      };
    }

    if (clean.includes('clinic') || clean.includes('dent') || clean.includes('care') || clean.includes('health')) {
      return {
        domain: clean,
        category: "High-Value Aesthetic & Health Services",
        problem: "Complex elective treatment comparison",
        problemDesc: "Patients research specialist credentials, recovery timelines, and procedural safety before contacting clinics.",
        conversation: "“Which boutique clinic specializes in Invisalign and veneers with custom 3D simulations?”",
        opportunity: "Consultation Pre-Qualification & Procedure Clarity",
        opportunityDesc: "Show up before the patient settles on a commoditized directory search.",
        adAngle: "“Clear answers before you commit. See your 3D smile simulation before booking treatment.”",
        adLink: "Claim Digital Consultation →"
      };
    }

    // Default intelligent SMB service model
    const businessName = clean.split('.')[0];
    const capitalized = businessName.charAt(0).toUpperCase() + businessName.slice(1);

    return {
      domain: clean,
      category: "Specialized Service Business",
      problem: "Evaluating trusted providers for high-stakes services",
      problemDesc: "Prospective buyers use AI to compare methodologies, pricing structures, and project guarantees.",
      conversation: `“What should I look for when hiring a top-tier ${capitalized} specialist, and what questions should I ask?”`,
      opportunity: "High-Intent Vendor Selection & Trust Anchoring",
      opportunityDesc: "Position your firm as the benchmark authority while prospects assemble their shortlist.",
      adAngle: `“Choosing a ${capitalized} partner? Get transparent milestones and proven expertise from day one.”`,
      adLink: "Explore Custom Client Solutions →"
    };
  }

  /**
   * Decoupled Scan Provider
   * Swappable with a real backend API endpoint
   */
  async function performScan(url) {
    if (USE_LIVE_API) {
      try {
        const response = await fetch(LIVE_API_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: url })
        });
        if (!response.ok) throw new Error('Scan API failed');
        return await response.json();
      } catch (err) {
        console.warn('API fallback to client simulation:', err);
        return analyzeDomainHeuristics(url);
      }
    } else {
      // Return simulated heuristics with real multi-stage delay
      return analyzeDomainHeuristics(url);
    }
  }

  /**
   * Run animated 4-stage scan sequence
   */
  async function runScanSequence(url) {
    if (!url) return;

    // Reset view states
    if (resultsContainer) resultsContainer.classList.remove('active');
    if (loader) loader.classList.add('active');
    if (btnSubmit) btnSubmit.disabled = true;

    const stages = [
      {
        progress: 25,
        msg: "UNDERSTANDING YOUR BUSINESS...",
        sub: `Analyzing ${url} metadata, core offerings & market niche...`,
        duration: 900
      },
      {
        progress: 55,
        msg: "FINDING BUYER PROBLEMS...",
        sub: "Identifying high-friction questions prospective buyers ask ChatGPT...",
        duration: 1100
      },
      {
        progress: 85,
        msg: "MAPPING BUYING CONVERSATIONS...",
        sub: "Clustering commercial intent vectors & conversational buying signals...",
        duration: 1200
      },
      {
        progress: 100,
        msg: "BUILDING OPPORTUNITIES...",
        sub: "Synthesizing custom ChatGPT Ads campaign angles & placement copy...",
        duration: 800
      }
    ];

    for (let i = 0; i < stages.length; i++) {
      const stage = stages[i];
      if (progressFill) progressFill.style.width = stage.progress + '%';
      if (stepMsg) stepMsg.textContent = stage.msg;
      if (substepMsg) substepMsg.textContent = stage.sub;
      await new Promise(r => setTimeout(r, stage.duration));
    }

    // Retrieve scan data
    const data = await performScan(url);

    // Populate Results
    if (resDomain) resDomain.textContent = data.domain;
    if (resCategory) resCategory.textContent = data.category;
    if (resProblem) resProblem.textContent = data.problem;
    if (resProblemDesc) resProblemDesc.textContent = data.problemDesc;
    if (resConversation) resConversation.textContent = data.conversation;
    if (resOpportunity) resOpportunity.textContent = data.opportunity;
    if (resOpportunityDesc) resOpportunityDesc.textContent = data.opportunityDesc;
    if (resAdAngle) resAdAngle.textContent = data.adAngle;
    if (resAdUrl) resAdUrl.textContent = data.adLink;

    // Hide loader, show results
    if (loader) loader.classList.remove('active');
    if (resultsContainer) {
      resultsContainer.classList.add('active');
      resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    if (btnSubmit) btnSubmit.disabled = false;
  }

  // Handle form submit
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const val = inputUrl ? inputUrl.value.trim() : '';
      if (!val) {
        if (inputUrl) inputUrl.focus();
        return;
      }
      runScanSequence(val);
    });
  }

  // Preset pill clicks
  presetPills.forEach(function (pill) {
    pill.addEventListener('click', function () {
      const presetUrl = this.getAttribute('data-preset');
      if (inputUrl) inputUrl.value = presetUrl;
      runScanSequence(presetUrl);
    });
  });

  // Claim button interaction: opens modal and prefills website
  if (btnClaim) {
    btnClaim.addEventListener('click', function () {
      const modal = document.getElementById('intakeModal');
      const intakeWebsite = document.getElementById('intakeWebsite');
      const intakeService = document.getElementById('intakeService');

      if (intakeWebsite && inputUrl && inputUrl.value.trim()) {
        intakeWebsite.value = inputUrl.value.trim();
      }
      if (intakeService && resCategory) {
        intakeService.value = resCategory.textContent;
      }
      if (modal) {
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
      }
    });
  }

  // Expose API function globally for testing or backend integration
  window.AepifyScanner = {
    scan: runScanSequence,
    analyzeHeuristics: analyzeDomainHeuristics
  };

})();
