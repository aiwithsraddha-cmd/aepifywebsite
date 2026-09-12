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
