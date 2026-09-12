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
