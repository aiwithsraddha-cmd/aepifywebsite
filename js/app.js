/**
 * AEPIFY PRODUCTION BUNDLE
 * Includes all interactive modules: Hero Demo, Readiness Report, Who Its For, How It Works,
 * Opportunity Engine, Dashboard, Modals, and App Coordinator.
 */

// ==========================================
// MODULE: hero-demo.js
// ==========================================
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
  if (!elPrompt) return; // Exit cleanly if hero demo widget is not present on page
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
  const connectors = document.querySelectorAll('.pipeline-connector');

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


// ==========================================
// MODULE: readiness-report.js
// ==========================================
/**
 * AEPIFY READINESS REPORT (SECTION 5)
 * Interactive readiness preview demonstrating the core differentiator:
 * Aepify determines whether a business is ready before spending on ads.
 * If not ready: Fix -> Reassess -> Advertise.
 * If ready: Score, campaign themes, strategy, and next steps.
 */

(function () {
  'use strict';

  const tabBtns = document.querySelectorAll('.doc-tab-btn');
  const scrollBox = document.getElementById('docViewerScroll');

  if (!scrollBox || !tabBtns.length) return;

  function setActiveTab(pageNum) {
    tabBtns.forEach(btn => {
      const match = btn.getAttribute('data-page') === String(pageNum);
      btn.classList.toggle('active', match);
      btn.setAttribute('aria-selected', match ? 'true' : 'false');
    });
  }

  tabBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const pageNum = this.getAttribute('data-page');
      const targetPage = document.getElementById('docPage' + pageNum);
      if (targetPage && scrollBox) {
        const targetOffset = targetPage.offsetTop - scrollBox.offsetTop;
        scrollBox.scrollTo({
          top: targetOffset,
          behavior: 'smooth'
        });
        setActiveTab(pageNum);
      }
    });
  });

  // Track scroll position to update active tab
  let isScrolling;
  scrollBox.addEventListener('scroll', function () {
    window.clearTimeout(isScrolling);
    isScrolling = setTimeout(function () {
      const currentScroll = scrollBox.scrollTop + 60;
      const pages = [
        document.getElementById('docPage1'),
        document.getElementById('docPage2'),
        document.getElementById('docPage3')
      ];

      for (let i = pages.length - 1; i >= 0; i--) {
        const page = pages[i];
        if (page) {
          const pageTop = page.offsetTop - scrollBox.offsetTop;
          if (currentScroll >= pageTop - 20) {
            setActiveTab(i + 1);
            break;
          }
        }
      }
    }, 50);
  }, { passive: true });

  window.AepifyReportViewer = {
    goToPage: function (pageNum) {
      const btn = document.querySelector(`.doc-tab-btn[data-page="${pageNum}"]`);
      if (btn) btn.click();
    }
  };
})();


// ==========================================
// MODULE: who-its-for.js
// ==========================================
/**
 * AEPIFY WHO IT'S FOR (SECTION 6)
 * 5 Smooth Animated Industry Tabs:
 * 1. LOCAL SERVICES
 * 2. TRAVEL & HOSPITALITY
 * 3. RETAIL & ECOMMERCE
 * 4. EDUCATION & CAREERS
 * 5. CONSUMER GOODS
 */

(function () {
  'use strict';

  const industryData = {
    local: {
      id: "local",
      title: "LOCAL SERVICES",
      customer: "“We’re planning a major renovation for our 20-year-old house and need architectural design, structural engineering, and permits. Where do we start?”",
      situation: "Planning a Home Renovation",
      opportunity: "Design + Build Services",
      campaign: "Complete Home Renovation",
      adTitle: "Planning a major renovation?",
      adBody: "One team from design to construction.",
      adCta: "Learn More →"
    },
    travel: {
      id: "travel",
      title: "TRAVEL & HOSPITALITY",
      customer: "“What’s the best way to plan a 10-day Italy trip without constantly changing hotels?”",
      situation: "Planning a Multi-City Italy Trip",
      opportunity: "Private Itinerary Planning",
      campaign: "Bespoke Italy Travel",
      adTitle: "Italy, planned around the way you want to travel.",
      adBody: "Private itineraries. Hand-picked stays. One seamless journey.",
      adCta: "Explore →"
    },
    retail: {
      id: "retail",
      title: "RETAIL & ECOMMERCE",
      customer: "“How should I set up my work-from-home setup?”",
      situation: "Choosing a Work From Home Setup",
      opportunity: "Ergonomic Home Office",
      campaign: "Standing Desks for Home Offices",
      adTitle: "A better desk for better workdays.",
      adBody: "Compare ergonomic standing desks built for long hours.",
      adCta: "Shop Now →"
    },
    education: {
      id: "education",
      title: "EDUCATION & CAREERS",
      customer: "“Which data analytics course would actually help me move into a new career?”",
      situation: "Career Transition",
      opportunity: "Data Analytics Training",
      campaign: "Career-Focused Data Analytics",
      adTitle: "Build the skills for the next career move.",
      adBody: "Practical data analytics training built around real-world work.",
      adCta: "Explore Courses →"
    },
    consumer: {
      id: "consumer",
      title: "CONSUMER GOODS",
      customer: "“What should I look for when buying a good air purifier for a large bedroom?”",
      situation: "Choosing an Air Purifier",
      opportunity: "Large-Room Air Purification",
      campaign: "Air Purifiers for Large Rooms",
      adTitle: "Cleaner air for larger rooms.",
      adBody: "Find the right capacity without the guesswork.",
      adCta: "Shop Now →"
    }
  };

  const tabs = document.querySelectorAll('.industry-tab');
  const stage = document.getElementById('industryStage');
  const elCustomer = document.getElementById('indCustomerQuote');
  const elSituation = document.getElementById('indSituation');
  const elOpportunity = document.getElementById('indOpportunity');
  const elCampaign = document.getElementById('indCampaign');
  const elAdTitle = document.getElementById('indAdTitle');
  const elAdBody = document.getElementById('indAdBody');
  const elAdCta = document.getElementById('indAdCta');

  function switchIndustry(key) {
    const data = industryData[key];
    if (!data) return;

    // Update active tab button
    tabs.forEach(function (tab) {
      const match = tab.getAttribute('data-industry') === key;
      tab.classList.toggle('active', match);
      tab.setAttribute('aria-selected', match ? 'true' : 'false');
    });

    // Smooth transition: fade out slightly, update content, fade in with slide
    if (stage) {
      stage.classList.add('transitioning');
      setTimeout(function () {
        if (elCustomer) elCustomer.textContent = data.customer;
        if (elSituation) elSituation.textContent = data.situation;
        if (elOpportunity) elOpportunity.textContent = data.opportunity;
        if (elCampaign) elCampaign.textContent = data.campaign;
        if (elAdTitle) elAdTitle.textContent = data.adTitle;
        if (elAdBody) elAdBody.textContent = data.adBody;
        if (elAdCta) elAdCta.textContent = data.adCta;

        stage.classList.remove('transitioning');
      }, 160);
    }
  }

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      const key = this.getAttribute('data-industry');
      switchIndustry(key);
    });
  });

  window.AepifyWhoItsFor = {
    select: switchIndustry
  };
})();


// ==========================================
// MODULE: how-it-works.js
// ==========================================
/**
 * AEPIFY HOW IT WORKS (SECTION 7 - THE SYSTEM)
 * Interactive 5-Step Connected Nodes Workflow:
 * 01 - YOUR BUSINESS
 * 02 - READINESS REPORT
 * 03 - AD STRATEGY
 * 04 - CAMPAIGN
 * 05 - REPORT
 */

(function () {
  'use strict';

  const steps = document.querySelectorAll('.system-node');
  const progressLine = document.getElementById('systemProgressLine');
  let currentStep = 0;
  let autoPlay = true;
  let interval = null;

  function activateStep(index) {
    currentStep = index;
    steps.forEach(function (step, i) {
      if (i <= index) {
        step.classList.add('completed');
      } else {
        step.classList.remove('completed');
      }
      step.classList.toggle('active', i === index);
    });

    if (progressLine) {
      // Calculate progress width percentage between 5 nodes (0% to 100%)
      const percentage = (index / (steps.length - 1)) * 100;
      progressLine.style.width = percentage + '%';
    }
  }

  steps.forEach(function (step, index) {
    step.addEventListener('click', function () {
      autoPlay = false;
      if (interval) clearInterval(interval);
      activateStep(index);
    });

    step.addEventListener('mouseenter', function () {
      if (autoPlay && interval) clearInterval(interval);
    });

    step.addEventListener('mouseleave', function () {
      if (autoPlay) startAutoPlay();
    });
  });

  function startAutoPlay() {
    if (interval) clearInterval(interval);
    interval = setInterval(function () {
      if (!autoPlay) return;
      currentStep = (currentStep + 1) % steps.length;
      activateStep(currentStep);
    }, 3800);
  }

  // Initialize
  activateStep(0);
  startAutoPlay();

  window.AepifySystem = {
    setStep: activateStep
  };
})();


// ==========================================
// MODULE: opportunity-engine.js
// ==========================================
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
      let targetUrl = 'https://tally.so/r/GxZpre';
      if (val) {
        targetUrl += '?website=' + encodeURIComponent(val) + '&url=' + encodeURIComponent(val);
      }
      window.open(targetUrl, '_blank', 'noopener,noreferrer');
    });
  }

  if (btnClaim) {
    btnClaim.addEventListener('click', function () {
      // Direct navigation to Tally form
    });
  }

  window.AepifyOpportunityEngine = {
    scan: runOpportunityScan
  };
})();


// ==========================================
// MODULE: dashboard.js
// ==========================================
/**
 * AEPIFY CHATGPT ADS MANAGEMENT DASHBOARD (SECTION 9)
 * Interactive, realistic SaaS product dashboard visual:
 * - Animated metrics count-up
 * - Dynamic SVG chart line drawing with gradient fill & hover tooltips
 * - Interactive navigation tabs (Campaigns, Ad Groups, Ads, Reports)
 * - Live status badge pulse & weekly reporting indicator
 */

(function () {
  'use strict';

  const dashboardContainer = document.getElementById('dashProductContainer');
  if (!dashboardContainer) return;

  const chartPath = document.getElementById('dashChartPath');
  const chartFill = document.getElementById('dashChartFill');
  const chartTooltip = document.getElementById('dashChartTooltip');
  const chartPoints = document.querySelectorAll('.dash-chart-point');

  let hasAnimated = false;

  const metrics = [
    { id: 'dashMetricSpend', prefix: '$', target: 1240, suffix: '', decimals: 0 },
    { id: 'dashMetricImpressions', prefix: '', target: 48.2, suffix: 'k', decimals: 1 },
    { id: 'dashMetricClicks', prefix: '', target: 1842, suffix: '', decimals: 0 },
    { id: 'dashMetricCTR', prefix: '', target: 3.82, suffix: '%', decimals: 2 },
    { id: 'dashMetricConversions', prefix: '', target: 94, suffix: '', decimals: 0 },
    { id: 'dashMetricCPC', prefix: '$', target: 0.67, suffix: '', decimals: 2 }
  ];

  function animateMetric(metric) {
    const el = document.getElementById(metric.id);
    if (!el) return;

    let start = 0;
    const duration = 1400;
    const startTime = performance.now();

    function step(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      const current = start + (metric.target - start) * ease;

      if (metric.decimals > 0) {
        el.textContent = metric.prefix + current.toFixed(metric.decimals) + metric.suffix;
      } else {
        el.textContent = metric.prefix + Math.floor(current).toLocaleString() + metric.suffix;
      }

      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        if (metric.decimals > 0) {
          el.textContent = metric.prefix + metric.target.toFixed(metric.decimals) + metric.suffix;
        } else {
          el.textContent = metric.prefix + metric.target.toLocaleString() + metric.suffix;
        }
      }
    }
    requestAnimationFrame(step);
  }

  function triggerDashboardAnimation() {
    if (hasAnimated) return;
    hasAnimated = true;

    // Trigger SVG path animation
    if (chartPath) {
      chartPath.classList.add('animate-stroke');
    }
    if (chartFill) {
      chartFill.classList.add('animate-fill');
    }

    // Trigger metric counters
    metrics.forEach(animateMetric);
  }

  // IntersectionObserver to trigger animation when scrolled into view
  if ('IntersectionObserver' in window && dashboardContainer) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          triggerDashboardAnimation();
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });

    observer.observe(dashboardContainer);
  } else {
    setTimeout(triggerDashboardAnimation, 800);
  }

  // Interactive Chart Tooltips
  chartPoints.forEach(function (pt) {
    pt.addEventListener('mouseenter', function (e) {
      const day = this.getAttribute('data-day') || 'Day';
      const clicks = this.getAttribute('data-clicks') || '0';
      const spend = this.getAttribute('data-spend') || '$0';

      if (chartTooltip) {
        chartTooltip.innerHTML = `<strong>Day ${day}</strong> · ${clicks} clicks (${spend})`;
        chartTooltip.style.opacity = '1';
        chartTooltip.style.left = pt.getAttribute('cx') + 'px';
        chartTooltip.style.top = (parseFloat(pt.getAttribute('cy')) - 32) + 'px';
      }
    });

    pt.addEventListener('mouseleave', function () {
      if (chartTooltip) chartTooltip.style.opacity = '0';
    });
  });

  // Top Nav active states inside the mockup
  const dashNavLinks = document.querySelectorAll('.dash-nav-item');
  dashNavLinks.forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      dashNavLinks.forEach(l => l.classList.remove('active'));
      this.classList.add('active');
    });
  });

  window.AepifyDashboard = {
    trigger: triggerDashboardAnimation
  };
})();


// ==========================================
// MODULE: modal.js
// ==========================================
/**
 * AEPIFY MODAL HANDLER
 * Intake Modal & Legal Terms/Privacy Modals
 */

(function () {
  'use strict';

  // 1. Intake Modal
  const intakeModal = document.getElementById('intakeModal');
  const btnCloseIntake = document.getElementById('btnModalClose');
  const intakeForm = document.getElementById('intakeForm');
  const successBox = document.getElementById('modalSuccess');
  const btnCloseSuccess = document.getElementById('btnCloseSuccess');
  const modalTriggers = document.querySelectorAll('.open-intake-modal, #btnJoinFounding, #btnHeroCta, #btnFinalCta');

  function openIntakeModal(defaultWebsite) {
    if (!intakeModal) return;
    intakeModal.classList.add('active');
    intakeModal.setAttribute('aria-hidden', 'false');

    if (defaultWebsite) {
      const siteInput = document.getElementById('intakeWebsite');
      if (siteInput) siteInput.value = defaultWebsite;
    }

    const firstInput = intakeModal.querySelector('input');
    if (firstInput) setTimeout(() => firstInput.focus(), 100);
  }

  function closeIntakeModal() {
    if (!intakeModal) return;
    intakeModal.classList.remove('active');
    intakeModal.setAttribute('aria-hidden', 'true');
    setTimeout(function () {
      if (intakeForm) {
        intakeForm.classList.remove('hidden');
        intakeForm.reset();
      }
      if (successBox) successBox.classList.add('hidden');
    }, 280);
  }

  modalTriggers.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      // If it's an anchor to a section, let smooth scroll handle unless it's intended to trigger modal
      if (this.classList.contains('trigger-modal-only')) {
        e.preventDefault();
        openIntakeModal();
      }
    });
  });

  if (btnCloseIntake) btnCloseIntake.addEventListener('click', closeIntakeModal);
  if (btnCloseSuccess) btnCloseSuccess.addEventListener('click', closeIntakeModal);

  if (intakeModal) {
    intakeModal.addEventListener('click', function (e) {
      if (e.target === intakeModal) closeIntakeModal();
    });
  }

  // 2. Legal Policy Modal
  const legalModal = document.getElementById('legalModal');
  const legalClose = document.getElementById('btnLegalClose');
  const legalTitle = document.getElementById('legalModalTitle');
  const legalContent = document.getElementById('legalModalContent');
  const legalTriggers = document.querySelectorAll('.legal-link');

  const legalTexts = {
    privacy: {
      title: "Privacy Policy",
      content: `
        <p><strong>Effective Date:</strong> January 2026</p>
        <p>AEPIFY ("we", "our", or "us") respects your privacy. We are an independent ChatGPT Ads strategy and management service.</p>
        <p><strong>1. Information We Collect:</strong> When you request an Opportunity Score or submit a website assessment, we collect your website URL, contact email, and name. When managing campaigns, you maintain direct billing and credentials with OpenAI.</p>
        <p><strong>2. How We Use Information:</strong> Information submitted is used solely to evaluate your website's ChatGPT Ads readiness, calculate commercial viability, and structure your campaign deliverables. We never sell or distribute your data.</p>
        <p><strong>3. Zero Black Box Policy:</strong> Your advertiser account, billing data, and campaign performance remain your property and reside inside your direct advertiser account.</p>
        <p><strong>4. Contact:</strong> For inquiries, contact privacy@aepify.ai.</p>
      `
    },
    terms: {
      title: "Terms of Service",
      content: `
        <p><strong>Effective Date:</strong> January 2026</p>
        <p><strong>1. Service Overview:</strong> AEPIFY provides ChatGPT Ads readiness assessments, campaign strategy, ad copy creation, campaign setup, ongoing optimization, and weekly reporting.</p>
        <p><strong>2. Independence & OpenAI Disclaimer:</strong> AEPIFY is an independent ChatGPT Ads management service and is not affiliated with, endorsed by, or sponsored by OpenAI. OpenAI controls business verification, account eligibility, ad policies, placement, pricing, and auction delivery.</p>
        <p><strong>3. Billing & Ad Spend:</strong> The $99/month launch fee covers AEPIFY's strategy, setup, optimization, and reporting services. All media ad spend is paid directly by the client to OpenAI without markup.</p>
        <p><strong>4. Intellectual Property:</strong> All trademarks, logos, and brand assets of AEPIFY are proprietary.</p>
      `
    }
  };

  function openLegalModal(type) {
    if (!legalModal) return;
    const policy = legalTexts[type] || legalTexts.terms;
    if (legalTitle) legalTitle.textContent = policy.title;
    if (legalContent) legalContent.innerHTML = policy.content;
    legalModal.classList.add('active');
    legalModal.setAttribute('aria-hidden', 'false');
  }

  function closeLegalModal() {
    if (!legalModal) return;
    legalModal.classList.remove('active');
    legalModal.setAttribute('aria-hidden', 'true');
  }

  legalTriggers.forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      const type = this.getAttribute('data-legal') || 'terms';
      openLegalModal(type);
    });
  });

  if (legalClose) legalClose.addEventListener('click', closeLegalModal);
  if (legalModal) {
    legalModal.addEventListener('click', function (e) {
      if (e.target === legalModal) closeLegalModal();
    });
  }

  // Global Escape Key Listener
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      if (intakeModal && intakeModal.classList.contains('active')) closeIntakeModal();
      if (legalModal && legalModal.classList.contains('active')) closeLegalModal();
    }
  });

  // Handle intake submission
  if (intakeForm) {
    intakeForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const submitBtn = document.getElementById('btnSubmitIntake');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Securing Strategy Spot...';
      }
      setTimeout(function () {
        if (intakeForm) intakeForm.classList.add('hidden');
        if (successBox) successBox.classList.remove('hidden');
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Submit & Claim Spot →';
        }
      }, 600);
    });
  }

  window.AepifyModal = {
    openIntake: openIntakeModal,
    closeIntake: closeIntakeModal,
    openLegal: openLegalModal,
    closeLegal: closeLegalModal
  };
})();


// ==========================================
// MODULE: app-coordinator.js
// ==========================================
/**
 * AEPIFY APP COORDINATOR
 * - Sticky Navigation Scroll & Compaction
 * - Mobile Menu Drawer
 * - Smooth Anchor Scrolling
 * - Single-Open FAQ Accordion
 * - High-Performance Scroll Reveal Animations with Instant-Load Fallback
 */

(function () {
  'use strict';

  // 1. Sticky Navigation Compaction Effect
  const navbar = document.getElementById('navbar');
  function handleNavScroll() {
    if (!navbar) return;
    if (window.scrollY > 20) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }
  window.addEventListener('scroll', handleNavScroll, { passive: true });
  handleNavScroll();

  // 2. Mobile Menu Toggle
  const mobileToggle = document.getElementById('mobileToggle');
  const mobileMenu = document.getElementById('mobileMenu');
  const mobileLinks = document.querySelectorAll('.mobile-nav-link, .mobile-cta-btn');

  function openMobileMenu() {
    if (!mobileMenu || !mobileToggle) return;
    mobileMenu.classList.add('open');
    mobileToggle.setAttribute('aria-expanded', 'true');
    mobileMenu.setAttribute('aria-hidden', 'false');
    document.body.classList.add('mobile-menu-active');
  }

  function closeMobileMenu() {
    if (!mobileMenu || !mobileToggle) return;
    mobileMenu.classList.remove('open');
    mobileToggle.setAttribute('aria-expanded', 'false');
    mobileMenu.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('mobile-menu-active');
  }

  function toggleMobileMenu(e) {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (!mobileMenu) return;
    if (mobileMenu.classList.contains('open')) {
      closeMobileMenu();
    } else {
      openMobileMenu();
    }
  }

  if (mobileToggle) {
    mobileToggle.addEventListener('click', toggleMobileMenu);
  }

  document.addEventListener('click', function (e) {
    if (!mobileMenu || !mobileToggle) return;
    if (mobileMenu.classList.contains('open')) {
      if (!mobileMenu.contains(e.target) && !mobileToggle.contains(e.target)) {
        closeMobileMenu();
      }
    }
  });

  mobileLinks.forEach(function (link) {
    link.addEventListener('click', function () {
      closeMobileMenu();
    });
  });

  // 3. FAQ Accordion (Strict: Only one open at a time)
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(function (item) {
    const btn = item.querySelector('.faq-question');
    if (!btn) return;

    btn.addEventListener('click', function () {
      const isExpanded = item.classList.contains('active');

      // Close all others
      faqItems.forEach(function (other) {
        other.classList.remove('active');
        const otherBtn = other.querySelector('.faq-question');
        if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
      });

      // Toggle clicked item
      if (!isExpanded) {
        item.classList.add('active');
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  });

  // 4. Smooth Anchor Link Handler
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href === '#' || href === '') return;
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });

        if (mobileMenu && mobileMenu.classList.contains('open')) {
          closeMobileMenu();
        }

        // Focus Opportunity Engine input if target is opportunity-engine
        if (href === '#opportunity-engine') {
          setTimeout(function () {
            const input = document.getElementById('oppEngineInput');
            if (input) input.focus();
          }, 450);
        }
      }
    });
  });

  // 5. High-Performance Scroll Reveal with Instant Visibility
  const revealElements = document.querySelectorAll('.reveal');
  
  if ('IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          revealObserver.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.05,
      rootMargin: '50px 0px 50px 0px'
    });

    revealElements.forEach(function (el) {
      revealObserver.observe(el);
    });
  } else {
    revealElements.forEach(function (el) {
      el.classList.add('in-view');
    });
  }

  // Fallback to guarantee all elements appear even if headless renderer or fast scroll
  window.addEventListener('load', function () {
    setTimeout(function () {
      revealElements.forEach(function (el) {
        el.classList.add('in-view');
      });
    }, 400);
  });

  // 6. WhatsApp Desktop vs Mobile Smart Routing
  try {
    const whatsappLinks = document.querySelectorAll('.whatsapp-link');
    const isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    if (!isMobileDevice) {
      const desktopUrl = 'https://web.whatsapp.com/send?phone=919000271367&text=' + encodeURIComponent("Hi Aepify, I'd like to learn more about ChatGPT Ads management.");
      whatsappLinks.forEach(function (link) {
        link.href = desktopUrl;
      });
    }
  } catch (e) {
    // Graceful fallback to default wa.me href
  }

})();
