/**
 * AEPIFY OPPORTUNITY ENGINE (SECTION 8)
 * Core interactive tool:
 * Input URL -> Animated multi-stage analysis -> Displays:
 * CHATGPT ADS OPPORTUNITY SCORE: 82 / 100 (STRONG OPPORTUNITY)
 * Plus: Readiness, Opportunity, Campaign potential, Recommended next step.
 */

(function () {
  'use strict';

  const form = document.getElementById('oppEngineForm');
  const input = document.getElementById('oppEngineInput');
  const btnSubmit = document.getElementById('oppEngineSubmit');
  const loader = document.getElementById('oppEngineLoader');
  const loaderBar = document.getElementById('oppLoaderBar');
  const loaderStatus = document.getElementById('oppLoaderStatus');
  const loaderSub = document.getElementById('oppLoaderSub');
  const results = document.getElementById('oppEngineResults');
  const scoreNumber = document.getElementById('oppScoreNumber');
  const presetPills = document.querySelectorAll('.opp-preset-btn');
  const btnClaim = document.getElementById('btnOppClaim');

  const analysisStages = [
    {
      progress: 25,
      status: "ANALYSING WEBSITE & OFFER STRUCTURE...",
      sub: "Extracting core service deliverables, pricing indicators, and landing page readiness..."
    },
    {
      progress: 55,
      status: "SEARCHING CHATGPT BUYER CONVERSATIONS...",
      sub: "Scanning high-intent decision questions and comparative prompts..."
    },
    {
      progress: 85,
      status: "EVALUATING COMMERCIAL VIABILITY...",
      sub: "Benchmarking conversational CPC potential, intent match density, and ad creative angles..."
    },
    {
      progress: 100,
      status: "SYNTHESIZING OPPORTUNITY SCORE...",
      sub: "Finalising custom readiness assessment and campaign recommendations..."
    }
  ];

  async function runOpportunityScan(targetUrl) {
    if (!targetUrl) return;

    // Clean display domain
    let domainDisplay = targetUrl.replace(/^(https?:\/\/)?(www\.)?/, '').replace(/\/.*$/, '').trim();
    if (!domainDisplay) domainDisplay = 'examplebusiness.com';

    // Update display domain across result tags
    const domainLabels = document.querySelectorAll('.opp-result-domain');
    domainLabels.forEach(el => el.textContent = domainDisplay);

    // Hide results, show loader
    if (results) {
      results.classList.remove('active');
      results.style.display = 'none';
    }
    if (loader) {
      loader.style.display = 'block';
      requestAnimationFrame(() => loader.classList.add('active'));
    }
    if (btnSubmit) {
      btnSubmit.disabled = true;
      btnSubmit.classList.add('loading');
    }

    // Run stages
    for (let i = 0; i < analysisStages.length; i++) {
      const stage = analysisStages[i];
      if (loaderBar) loaderBar.style.width = stage.progress + '%';
      if (loaderStatus) loaderStatus.textContent = stage.status;
      if (loaderSub) loaderSub.textContent = stage.sub;
      await new Promise(r => setTimeout(r, 700));
    }

    // Hide loader, reveal results
    if (loader) {
      loader.classList.remove('active');
      setTimeout(() => {
        loader.style.display = 'none';
      }, 200);
    }

    if (results) {
      results.style.display = 'block';
      requestAnimationFrame(() => {
        results.classList.add('active');
      });
      results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    if (btnSubmit) {
      btnSubmit.disabled = false;
      btnSubmit.classList.remove('loading');
    }

    // Animate score counter to 82
    animateScoreCounter(82);

    // Also update domain in readiness report if available
    if (window.AepifyReadiness && typeof window.AepifyReadiness.setDomain === 'function') {
      window.AepifyReadiness.setDomain(domainDisplay);
    }
  }

  function animateScoreCounter(target) {
    if (!scoreNumber) return;
    let start = 0;
    const duration = 1200;
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const ease = 1 - Math.pow(1 - progress, 3);
      const current = Math.floor(ease * target);
      scoreNumber.textContent = current;

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        scoreNumber.textContent = target;
      }
    }

    requestAnimationFrame(update);
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const val = input ? input.value.trim() : '';
      if (!val) {
        if (input) input.focus();
        return;
      }
      runOpportunityScan(val);
    });
  }

  presetPills.forEach(function (pill) {
    pill.addEventListener('click', function () {
      const url = this.getAttribute('data-preset-url') || this.textContent.trim();
      if (input) input.value = url;
      runOpportunityScan(url);
    });
  });

  if (btnClaim) {
    btnClaim.addEventListener('click', function () {
      const modal = document.getElementById('intakeModal');
      const intakeWebsite = document.getElementById('intakeWebsite');
      if (intakeWebsite && input && input.value.trim()) {
        intakeWebsite.value = input.value.trim();
      }
      if (modal) {
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
      }
    });
  }

  window.AepifyOpportunityEngine = {
    scan: runOpportunityScan
  };
})();
