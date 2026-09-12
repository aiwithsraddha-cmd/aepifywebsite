/**
 * AEPIFY HERO SIGNATURE INTERACTIVE DEMO
 * Visual transformation pipeline:
 * USER PROMPT -> BUYING INTENT -> OPPORTUNITY -> CAMPAIGN -> CHATGPT AD
 */

(function () {
  'use strict';

  const scenarios = {
    renovation: {
      prompt: "“We’re renovating a 20-year-old house. Should we redo the kitchen and bathrooms together?”",
      intent: "Renovation planning",
      opportunity: "Major Home Renovation",
      campaign: "Planning a Major Home Renovation",
      adHeadline: "“Planning a major renovation? One team from design to construction.”",
      adUrl: "oakandiron.build · Direct Consultation",
      adBtn: "Book Initial Walkthrough →"
    },
    travel: {
      prompt: "“Can you plan a 10-day luxury Italy trip without changing hotels every two days?”",
      intent: "Bespoke Italy itinerary & private logistics",
      opportunity: "Seamless Italian Private Escapes",
      campaign: "Bespoke Italian Concierge Travel",
      adHeadline: "“Luxury Italy made effortless. Private drivers, hand-picked villas, zero logistics stress.”",
      adUrl: "bellavillatrips.com · Private Itinerary",
      adBtn: "Request Custom Itinerary →"
    },
    consulting: {
      prompt: "“Do I need help restructuring my sales team after hitting $5M ARR?”",
      intent: "B2B Sales Org Architecture & quota design",
      opportunity: "Sales Leadership Advisory",
      campaign: "Mid-Market Sales Org Architecture",
      adHeadline: "“Scaling past $5M? Fix sales enablement and quota structure before hiring more reps.”",
      adUrl: "apexsalesadvisory.com · Strategy Session",
      adBtn: "Schedule 30-Min Diagnostic →"
    }
  };

  let currentScenario = 'renovation';
  let activeStep = 1;
  let isPlaying = true;
  let timer = null;

  // DOM Elements
  const elPrompt = document.getElementById('heroUserPrompt');
  const elIntent = document.getElementById('pipelineIntent');
  const elOpportunity = document.getElementById('pipelineOpportunity');
  const elCampaign = document.getElementById('pipelineCampaign');
  const elAdHeadline = document.getElementById('pipelineAdHeadline');
  const elAdUrl = document.getElementById('pipelineAdUrl');
  const elAdBtn = document.getElementById('pipelineAdBtn');
  const steps = document.querySelectorAll('.pipeline-step');

  const btnPrev = document.getElementById('btnDemoPrev');
  const btnPlay = document.getElementById('btnDemoPlay');
  const btnNext = document.getElementById('btnDemoNext');
  const playIcon = btnPlay ? btnPlay.querySelector('.play-icon') : null;
  const pauseIcon = btnPlay ? btnPlay.querySelector('.pause-icon') : null;
  const statusLabel = document.getElementById('demoStatusText');
  const tabs = document.querySelectorAll('.scenario-tab');

  function renderScenario(key) {
    const data = scenarios[key];
    if (!data) return;

    if (elPrompt) elPrompt.textContent = data.prompt;
    if (elIntent) elIntent.textContent = data.intent;
    if (elOpportunity) elOpportunity.textContent = data.opportunity;
    if (elCampaign) elCampaign.textContent = data.campaign;
    if (elAdHeadline) elAdHeadline.textContent = data.adHeadline;
    if (elAdUrl) elAdUrl.textContent = data.adUrl;
    if (elAdBtn) elAdBtn.textContent = data.adBtn;
  }

  const connectors = document.querySelectorAll('.pipeline-connector');

  function setStep(stepNum) {
    activeStep = ((stepNum - 1 + 4) % 4) + 1;
    steps.forEach(function (step) {
      const num = parseInt(step.getAttribute('data-step'), 10);
      if (num <= activeStep) {
        step.classList.add('active');
      } else {
        step.classList.remove('active');
      }
      if (num === activeStep) {
        step.classList.add('pulse-active');
      } else {
        step.classList.remove('pulse-active');
      }
    });

    connectors.forEach(function (conn, idx) {
      if (idx < activeStep - 1) {
        conn.classList.add('active');
      } else {
        conn.classList.remove('active');
      }
    });

    if (statusLabel) {
      const labels = [
        "Analyzing prompt intent...",
        "Identifying commercial opportunity...",
        "Structuring ChatGPT campaign...",
        "Live ChatGPT Ad preview ready"
      ];
      statusLabel.textContent = labels[activeStep - 1] || "Live AI Intent Engine: Active";
    }
  }

  function startAutoplay() {
    if (timer) clearInterval(timer);
    timer = setInterval(function () {
      if (!isPlaying) return;
      if (activeStep >= 4) {
        // Switch to next scenario automatically on loop
        const keys = Object.keys(scenarios);
        const nextIdx = (keys.indexOf(currentScenario) + 1) % keys.length;
        switchScenario(keys[nextIdx]);
        setStep(1);
      } else {
        setStep(activeStep + 1);
      }
    }, 2800);
  }

  function switchScenario(key) {
    if (!scenarios[key]) return;
    currentScenario = key;
    if (elPrompt) {
      elPrompt.style.opacity = '0.35';
      elPrompt.style.transform = 'translateY(3px)';
      setTimeout(function () {
        renderScenario(key);
        elPrompt.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        elPrompt.style.opacity = '1';
        elPrompt.style.transform = 'translateY(0)';
      }, 140);
    } else {
      renderScenario(key);
    }
    tabs.forEach(function (tab) {
      const matches = tab.getAttribute('data-scenario') === key;
      tab.classList.toggle('active', matches);
      tab.setAttribute('aria-selected', matches ? 'true' : 'false');
    });
  }

  // Setup event listeners
  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      const key = this.getAttribute('data-scenario');
      switchScenario(key);
      setStep(4); // show full pipeline immediately on user click
    });
  });

  if (btnPrev) {
    btnPrev.addEventListener('click', function () {
      setStep(activeStep - 1);
    });
  }

  if (btnNext) {
    btnNext.addEventListener('click', function () {
      setStep(activeStep + 1);
    });
  }

  if (btnPlay) {
    btnPlay.addEventListener('click', function () {
      isPlaying = !isPlaying;
      if (playIcon) playIcon.classList.toggle('hidden', isPlaying);
      if (pauseIcon) pauseIcon.classList.toggle('hidden', !isPlaying);
      if (isPlaying) {
        startAutoplay();
      } else {
        clearInterval(timer);
      }
    });
  }

  // Initialize
  renderScenario(currentScenario);
  setStep(4);
  startAutoplay();
})();
