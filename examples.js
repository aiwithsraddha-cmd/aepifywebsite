/**
 * AEPIFY SEE IT IN ACTION
 * Real-world campaign switcher with animated performance metrics
 */

(function () {
  'use strict';

  const examples = {
    reno: {
      query: "“How much should I budget for a 2,000 sq ft renovation?”",
      situation: "BUYING SITUATION: Major renovation planning",
      campaign: "Plan Your Renovation Properly",
      adCopy: "“Planning a major renovation? One team from design to construction.”",
      adTarget: "Targeting prompts around project estimates & contractor selection",
      spendVal: 612,
      clicksVal: 141,
      enquiriesVal: 8,
      enquiriesLabel: "ENQUIRIES",
      signal: "“Planning a full-home renovation”"
    },
    travel: {
      query: "“Can you plan a 10-day luxury Italy trip without changing hotels every two days?”",
      situation: "BUYING SITUATION: High-end bespoke European vacation",
      campaign: "Seamless Italian Private Escapes",
      adCopy: "“Luxury Italy made effortless. Private drivers, hand-picked villas, zero logistics stress.”",
      adTarget: "Targeting prompts around luxury Italian itineraries & transfers",
      spendVal: 840,
      clicksVal: 218,
      enquiriesVal: 14,
      enquiriesLabel: "ITINERARY REQUESTS",
      signal: "“Bespoke multi-city travel with concierge”"
    },
    consulting: {
      query: "“Do I need help restructuring my sales team?”",
      situation: "BUYING SITUATION: B2B Revenue Operations Scaling",
      campaign: "Sales Team Architecture & Scaling",
      adCopy: "“Scaling past $5M? Fix sales enablement and quota structure before hiring more reps.”",
      adTarget: "Targeting prompts around VP of Sales hiring & quota design",
      spendVal: 950,
      clicksVal: 112,
      enquiriesVal: 11,
      enquiriesLabel: "CONSULTATIONS",
      signal: "“Mid-market sales org restructure”"
    }
  };

  const tabs = document.querySelectorAll('.action-tab');
  const elQuery = document.getElementById('actionBuyerQuery');
  const elSituation = document.getElementById('actionSituation');
  const elCampaign = document.getElementById('actionCampaignTitle');
  const elAdCopy = document.getElementById('actionAdCopy');
  const elAdTarget = document.getElementById('actionAdTarget');
  const elSpend = document.getElementById('actionSpend');
  const elClicks = document.getElementById('actionClicks');
  const elEnquiries = document.getElementById('actionEnquiries');
  const elEnquiriesLabel = document.getElementById('actionEnquiriesLabel');
  const elSignal = document.getElementById('actionSignal');

  function renderExample(key, animate = true) {
    const data = examples[key];
    if (!data) return;

    tabs.forEach(function (tab) {
      const active = tab.getAttribute('data-action-tab') === key;
      tab.classList.toggle('active', active);
      tab.setAttribute('aria-selected', active ? 'true' : 'false');
    });

    if (elQuery) elQuery.textContent = data.query;
    if (elSituation) elSituation.textContent = data.situation;
    if (elCampaign) elCampaign.textContent = data.campaign;
    if (elAdCopy) elAdCopy.textContent = data.adCopy;
    if (elAdTarget) elAdTarget.textContent = data.adTarget;
    if (elEnquiriesLabel) elEnquiriesLabel.textContent = data.enquiriesLabel;
    if (elSignal) elSignal.textContent = data.signal;

    if (animate && window.AepifyUtils && window.AepifyUtils.animateValue) {
      window.AepifyUtils.animateValue(elSpend, 0, data.spendVal, 400, '$');
      window.AepifyUtils.animateValue(elClicks, 0, data.clicksVal, 450);
      window.AepifyUtils.animateValue(elEnquiries, 0, data.enquiriesVal, 500);
    } else {
      if (elSpend) elSpend.textContent = '$' + data.spendVal;
      if (elClicks) elClicks.textContent = data.clicksVal;
      if (elEnquiries) elEnquiries.textContent = data.enquiriesVal;
    }
  }

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      const key = this.getAttribute('data-action-tab');
      renderExample(key, true);
    });
  });

  // Initial render with animation
  renderExample('reno', false);
})();
