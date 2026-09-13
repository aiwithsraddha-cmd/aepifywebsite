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
