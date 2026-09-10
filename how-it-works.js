/**
 * AEPIFY HOW IT WORKS (THE SYSTEM)
 * Interactive 5-Step System Stepper
 */

(function () {
  'use strict';

  const steps = document.querySelectorAll('.sys-step');

  function activateStep(stepIndex) {
    steps.forEach(function (step, index) {
      step.classList.toggle('active', index === stepIndex);
    });
  }

  steps.forEach(function (step, index) {
    step.addEventListener('click', function () {
      activateStep(index);
    });
  });

  // Cycle automatically on a gentle pulse if not clicked
  let current = 0;
  let autoCycle = setInterval(function () {
    current = (current + 1) % steps.length;
    activateStep(current);
  }, 4000);

  // Stop auto cycle if user interacts
  steps.forEach(function (step) {
    step.addEventListener('mouseenter', function () {
      if (autoCycle) clearInterval(autoCycle);
    });
  });
})();
