/**
 * AEPIFY READINESS REPORT (SECTION 5)
 * Interactive readiness preview demonstrating the core differentiator:
 * Aepify determines whether a business is ready before spending on ads.
 * If not ready: Fix -> Reassess -> Advertise.
 * If ready: Score, campaign themes, strategy, and next steps.
 */

(function () {
  'use strict';

  const btnReady = document.getElementById('reportToggleReady');
  const btnNotReady = document.getElementById('reportToggleNotReady');
  const panelReady = document.getElementById('reportPanelReady');
  const panelNotReady = document.getElementById('reportPanelNotReady');
  const statusBadge = document.getElementById('reportStatusBadge');
  const reportDomain = document.getElementById('reportDomainDisplay');

  function setReadinessState(state) {
    const isReady = state === 'ready';

    if (btnReady) {
      btnReady.classList.toggle('active', isReady);
      btnReady.setAttribute('aria-pressed', isReady ? 'true' : 'false');
    }
    if (btnNotReady) {
      btnNotReady.classList.toggle('active', !isReady);
      btnNotReady.setAttribute('aria-pressed', !isReady ? 'true' : 'false');
    }

    if (statusBadge) {
      if (isReady) {
        statusBadge.textContent = 'READY TO ADVERTISE';
        statusBadge.className = 'readiness-badge status-ready';
      } else {
        statusBadge.textContent = 'NOT READY YET';
        statusBadge.className = 'readiness-badge status-not-ready';
      }
    }

    if (panelReady && panelNotReady) {
      if (isReady) {
        panelNotReady.classList.remove('active');
        setTimeout(() => {
          panelNotReady.style.display = 'none';
          panelReady.style.display = 'grid';
          requestAnimationFrame(() => {
            panelReady.classList.add('active');
          });
        }, 150);
      } else {
        panelReady.classList.remove('active');
        setTimeout(() => {
          panelReady.style.display = 'none';
          panelNotReady.style.display = 'grid';
          requestAnimationFrame(() => {
            panelNotReady.classList.add('active');
          });
        }, 150);
      }
    }
  }

  if (btnReady) {
    btnReady.addEventListener('click', function () {
      setReadinessState('ready');
    });
  }

  if (btnNotReady) {
    btnNotReady.addEventListener('click', function () {
      setReadinessState('not-ready');
    });
  }

  // Allow other components to update report domain
  window.AepifyReadiness = {
    setState: setReadinessState,
    setDomain: function (domain) {
      if (reportDomain && domain) {
        reportDomain.textContent = domain;
      }
    }
  };
})();
