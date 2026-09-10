/**
 * AEPIFY MODAL HANDLER
 * Founding 10 Intake Modal & Lead Strategy Booking
 */

(function () {
  'use strict';

  const modal = document.getElementById('intakeModal');
  const btnClose = document.getElementById('btnModalClose');
  const btnJoinFounding = document.getElementById('btnJoinFounding');
  const form = document.getElementById('intakeForm');
  const successBox = document.getElementById('modalSuccess');
  const btnCloseSuccess = document.getElementById('btnCloseSuccess');

  function openModal() {
    if (!modal) return;
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
    const firstInput = modal.querySelector('input');
    if (firstInput) setTimeout(() => firstInput.focus(), 100);
  }

  function closeModal() {
    if (!modal) return;
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
    // Reset state after transition
    setTimeout(function () {
      if (form) {
        form.classList.remove('hidden');
        form.reset();
      }
      if (successBox) successBox.classList.add('hidden');
    }, 280);
  }

  if (btnJoinFounding) {
    btnJoinFounding.addEventListener('click', function () {
      openModal();
    });
  }

  if (btnClose) {
    btnClose.addEventListener('click', closeModal);
  }

  if (btnCloseSuccess) {
    btnCloseSuccess.addEventListener('click', closeModal);
  }

  // Close on backdrop click
  if (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === modal) {
        closeModal();
      }
    });
  }

  // Close on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && modal && modal.classList.contains('active')) {
      closeModal();
    }
  });

  // Handle form submission
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      
      const submitBtn = document.getElementById('btnSubmitIntake');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Securing Your Spot...';
      }

      // Simulate instantaneous registration
      setTimeout(function () {
        if (form) form.classList.add('hidden');
        if (successBox) successBox.classList.remove('hidden');
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Submit & Claim Spot →';
        }
      }, 700);
    });
  }

  window.AepifyModal = {
    open: openModal,
    close: closeModal
  };

})();
