/**
 * Aepify Blog Interactive Script
 * - Client-side live search and category filtering
 * - Article Table of Contents scrollspy highlight
 * - Social link copying with toast notification
 * - Mobile navigation menu drawer
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Drawer Toggle
  const mobileToggle = document.getElementById('mobileToggle');
  const mobileMenu = document.getElementById('mobileMenu');
  if (mobileToggle && mobileMenu) {
    mobileToggle.addEventListener('click', () => {
      const isOpen = mobileToggle.getAttribute('aria-expanded') === 'true';
      mobileToggle.setAttribute('aria-expanded', !isOpen);
      mobileMenu.classList.toggle('open', !isOpen);
      mobileMenu.setAttribute('aria-hidden', isOpen);
    });
  }

  // 2. Blog Index Search & Category Filtering
  const searchInput = document.getElementById('blogSearchInput');
  const searchClear = document.getElementById('blogSearchClear');
  const catButtons = document.querySelectorAll('.blog-cat-btn');
  const cards = document.querySelectorAll('.blog-card');
  const emptyState = document.getElementById('blogEmptyState');
  const resetBtn = document.getElementById('btnResetFilters');

  if (cards.length > 0) {
    let currentCategory = 'all';
    let currentQuery = '';

    function filterArticles() {
      let visibleCount = 0;
      const q = currentQuery.trim().toLowerCase();

      cards.forEach(card => {
        const title = (card.getAttribute('data-title') || '').toLowerCase();
        const cat = (card.getAttribute('data-category') || '').toLowerCase();
        const tags = (card.getAttribute('data-tags') || '').toLowerCase();
        const text = card.textContent.toLowerCase();

        const matchesCategory = (currentCategory === 'all' || cat === currentCategory);
        const matchesQuery = !q || title.includes(q) || cat.includes(q) || tags.includes(q) || text.includes(q);

        if (matchesCategory && matchesQuery) {
          card.style.display = 'flex';
          visibleCount++;
        } else {
          card.style.display = 'none';
        }
      });

      if (emptyState) {
        if (visibleCount === 0) {
          emptyState.classList.add('visible');
        } else {
          emptyState.classList.remove('visible');
        }
      }

      if (searchClear) {
        searchClear.style.display = currentQuery ? 'flex' : 'none';
      }
    }

    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        currentQuery = e.target.value;
        filterArticles();
      });
    }

    if (searchClear) {
      searchClear.addEventListener('click', () => {
        if (searchInput) {
          searchInput.value = '';
          currentQuery = '';
          filterArticles();
          searchInput.focus();
        }
      });
    }

    catButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        catButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentCategory = (btn.getAttribute('data-category') || 'all').toLowerCase();
        filterArticles();
      });
    });

    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        currentCategory = 'all';
        currentQuery = '';
        if (searchInput) searchInput.value = '';
        catButtons.forEach(b => b.classList.toggle('active', (b.getAttribute('data-category') || '').toLowerCase() === 'all'));
        filterArticles();
      });
    }
  }

  // 3. Article Share: Copy Link Button
  const btnCopy = document.getElementById('btnCopyArticleLink');
  const toast = document.getElementById('copyToast');
  if (btnCopy) {
    btnCopy.addEventListener('click', () => {
      const url = window.location.href;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(showToast).catch(fallbackCopy);
      } else {
        fallbackCopy();
      }

      function fallbackCopy() {
        const temp = document.createElement('input');
        temp.value = url;
        document.body.appendChild(temp);
        temp.select();
        document.execCommand('copy');
        document.body.removeChild(temp);
        showToast();
      }

      function showToast() {
        if (!toast) return;
        toast.classList.add('show');
        setTimeout(() => {
          toast.classList.remove('show');
        }, 2500);
      }
    });
  }

  // 4. Article Table of Contents Scrollspy Link Highlight
  const tocLinks = document.querySelectorAll('.article-toc-nav a');
  const headings = Array.from(document.querySelectorAll('.article-content h2, .article-content h3'));

  if (tocLinks.length > 0 && headings.length > 0) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute('id');
          tocLinks.forEach(link => {
            if (link.getAttribute('href') === '#' + id) {
              link.classList.add('active');
            } else {
              link.classList.remove('active');
            }
          });
        }
      });
    }, {
      rootMargin: '-80px 0px -60% 0px',
      threshold: 0
    });

    headings.forEach(h => observer.observe(h));
  }
});
