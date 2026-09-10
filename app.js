/**
 * AEPIFY APP COORDINATOR
 * Navigation shrink on scroll, mobile menu drawer, FAQ accordion,
 * performant scroll reveal animations, and dynamic number counters.
 */

(function () {
  'use strict';

  // 1. Sticky Navigation Scroll Effect
  const navbar = document.getElementById('navbar');
  function handleNavScroll() {
    if (!navbar) return;
    if (window.scrollY > 24) {
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

  // Close when clicking outside navbar / drawer
  document.addEventListener('click', function (e) {
    if (!mobileMenu || !mobileToggle) return;
    if (mobileMenu.classList.contains('open')) {
      if (!mobileMenu.contains(e.target) && !mobileToggle.contains(e.target)) {
        closeMobileMenu();
      }
    }
  });

  // Close on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && mobileMenu && mobileMenu.classList.contains('open')) {
      closeMobileMenu();
    }
  });

  // Close when tapping any link inside the drawer
  mobileLinks.forEach(function (link) {
    link.addEventListener('click', function () {
      closeMobileMenu();
    });
  });

  // 3. FAQ Accordion
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(function (item) {
    const btn = item.querySelector('.faq-question');
    if (!btn) return;

    btn.addEventListener('click', function () {
      const isExpanded = item.classList.contains('active');
      
      // Close other items for crisp accordion feel
      faqItems.forEach(function (other) {
        other.classList.remove('active');
        const otherBtn = other.querySelector('.faq-question');
        if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
      });

      if (!isExpanded) {
        item.classList.add('active');
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  });

  // 4. Smooth Anchor Link Handler with Focus
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href === '#' || href === '') return;
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
        
        // If mobile menu open, close it
        if (mobileMenu && mobileMenu.classList.contains('open')) {
          toggleMobileMenu();
        }

        // If target is opportunity scan, autofocus the input
        if (href === '#opportunity-scan') {
          setTimeout(function () {
            const input = document.getElementById('scanUrlInput');
            if (input) input.focus();
          }, 450);
        }
      }
    });
  });

  // 5. Lightweight Performant Scroll Reveal
  if ('IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          revealObserver.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.08,
      rootMargin: '0px 0px -40px 0px'
    });

    document.querySelectorAll('.reveal').forEach(function (el) {
      revealObserver.observe(el);
    });
  } else {
    // Fallback if no observer
    document.querySelectorAll('.reveal').forEach(function (el) {
      el.classList.add('in-view');
    });
  }

  // 6. Number Counter Utility
  function animateValue(element, start, end, duration, prefix = '', suffix = '') {
    if (!element) return;
    let startTimestamp = null;
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const current = Math.floor(progress * (end - start) + start);
      element.textContent = prefix + current + suffix;
      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        element.textContent = prefix + end + suffix;
      }
    };
    window.requestAnimationFrame(step);
  }

  window.AepifyUtils = {
    animateValue: animateValue
  };

})();
