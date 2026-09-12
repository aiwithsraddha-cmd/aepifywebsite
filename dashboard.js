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

  const chartPath = document.getElementById('dashChartPath');
  const chartFill = document.getElementById('dashChartFill');
  const chartTooltip = document.getElementById('dashChartTooltip');
  const chartPoints = document.querySelectorAll('.dash-chart-point');
  const dashboardContainer = document.getElementById('dashProductContainer');

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
