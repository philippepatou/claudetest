/* ============================================
   SITE INFIRMIÈRE LIBÉRALE - DUNKERQUE
   JavaScript - Fonctionnalités principales
   ============================================ */

// ============================================
// 1. MENU MOBILE RESPONSIVE
// ============================================

document.addEventListener('DOMContentLoaded', function() {

  // Toggle menu hamburger
  const menuToggle = document.getElementById('menuToggle');
  const mainNav = document.getElementById('mainNav');

  if (menuToggle && mainNav) {
    menuToggle.addEventListener('click', function() {
      mainNav.classList.toggle('active');
      menuToggle.classList.toggle('active');

      // Empêcher le scroll du body quand le menu est ouvert
      if (mainNav.classList.contains('active')) {
        document.body.style.overflow = 'hidden';
      } else {
        document.body.style.overflow = '';
      }
    });

    // Fermer le menu si on clique sur un lien
    const navLinks = mainNav.querySelectorAll('a');
    navLinks.forEach(function(link) {
      link.addEventListener('click', function() {
        mainNav.classList.remove('active');
        menuToggle.classList.remove('active');
        document.body.style.overflow = '';
      });
    });

    // Fermer le menu si on clique en dehors
    document.addEventListener('click', function(event) {
      const isClickInside = mainNav.contains(event.target) || menuToggle.contains(event.target);

      if (!isClickInside && mainNav.classList.contains('active')) {
        mainNav.classList.remove('active');
        menuToggle.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }

});

// ============================================
// 2. SMOOTH SCROLL VERS ANCRES
// ============================================

document.addEventListener('DOMContentLoaded', function() {

  // Smooth scroll vers ancres (#)
  const anchorLinks = document.querySelectorAll('a[href^="#"]');

  anchorLinks.forEach(function(anchor) {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');

      // Ne rien faire si c'est juste "#"
      if (href === '#') {
        return;
      }

      const target = document.querySelector(href);

      if (target) {
        e.preventDefault();

        // Calculer la position avec offset pour le header sticky
        const headerHeight = document.querySelector('.site-header').offsetHeight;
        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;

        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }
    });
  });

});

// ============================================
// 3. VALIDATION FORMULAIRE CONTACT
// ============================================

document.addEventListener('DOMContentLoaded', function() {

  const contactForm = document.getElementById('contactForm');
  const formSuccess = document.getElementById('form-success');

  if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
      e.preventDefault();

      // Récupérer les valeurs
      const nom = document.getElementById('nom').value.trim();
      const email = document.getElementById('email').value.trim();
      const message = document.getElementById('message').value.trim();

      // Validation de base
      let isValid = true;
      let errorMessage = '';

      if (!nom) {
        isValid = false;
        errorMessage += 'Le nom est obligatoire.\n';
      }

      if (!email) {
        isValid = false;
        errorMessage += 'L\'email est obligatoire.\n';
      } else if (!isValidEmail(email)) {
        isValid = false;
        errorMessage += 'L\'adresse email n\'est pas valide.\n';
      }

      if (!message) {
        isValid = false;
        errorMessage += 'Le message est obligatoire.\n';
      }

      if (isValid) {
        // Afficher message de succès
        if (formSuccess) {
          formSuccess.style.display = 'block';
          formSuccess.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        // Réinitialiser le formulaire
        contactForm.reset();

        // Masquer le message de succès après 10 secondes
        setTimeout(function() {
          if (formSuccess) {
            formSuccess.style.display = 'none';
          }
        }, 10000);

      } else {
        alert(errorMessage);
      }
    });
  }

  // Fonction de validation email
  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

});

// ============================================
// 4. LAZY LOADING IMAGES (Fallback)
// ============================================

document.addEventListener('DOMContentLoaded', function() {

  // Vérifier si le navigateur supporte le lazy loading natif
  if ('loading' in HTMLImageElement.prototype) {
    // Support natif, ne rien faire
    console.log('Native lazy loading supported');
  } else {
    // Fallback avec IntersectionObserver
    const images = document.querySelectorAll('img[loading="lazy"]');

    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            const img = entry.target;

            // Charger l'image
            if (img.dataset.src) {
              img.src = img.dataset.src;
            }

            // Retirer le dataset et arrêter d'observer
            delete img.dataset.src;
            imageObserver.unobserve(img);
          }
        });
      });

      images.forEach(function(img) {
        // Sauvegarder le src dans data-src si pas déjà fait
        if (!img.dataset.src && img.src) {
          img.dataset.src = img.src;
          img.src = ''; // Vider temporairement
        }
        imageObserver.observe(img);
      });
    } else {
      // Pas de support IntersectionObserver, charger toutes les images
      images.forEach(function(img) {
        if (img.dataset.src) {
          img.src = img.dataset.src;
        }
      });
    }
  }

});

// ============================================
// 5. HEADER STICKY AU SCROLL
// ============================================

document.addEventListener('DOMContentLoaded', function() {

  let lastScroll = 0;
  const header = document.querySelector('.site-header');

  if (header) {
    window.addEventListener('scroll', function() {
      const currentScroll = window.pageYOffset;

      // Ajouter classe 'scrolled' si on a scrollé de plus de 100px
      if (currentScroll > 100) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }

      lastScroll = currentScroll;
    });
  }

});

// ============================================
// 6. AMÉLIORATION ACCESSIBILITÉ
// ============================================

document.addEventListener('DOMContentLoaded', function() {

  // Gérer la navigation au clavier dans le menu mobile
  const menuToggle = document.getElementById('menuToggle');
  const mainNav = document.getElementById('mainNav');

  if (menuToggle && mainNav) {
    // Fermer avec la touche Escape
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && mainNav.classList.contains('active')) {
        mainNav.classList.remove('active');
        menuToggle.classList.remove('active');
        document.body.style.overflow = '';
        menuToggle.focus(); // Remettre le focus sur le bouton
      }
    });
  }

  // Améliorer le focus visible pour les éléments interactifs
  const focusableElements = document.querySelectorAll('a, button, input, textarea, select');

  focusableElements.forEach(function(element) {
    element.addEventListener('focus', function() {
      this.setAttribute('data-focus-visible', 'true');
    });

    element.addEventListener('blur', function() {
      this.removeAttribute('data-focus-visible');
    });
  });

});

// ============================================
// 7. DÉTECTION SCROLL POUR ANIMATIONS (Optionnel)
// ============================================

document.addEventListener('DOMContentLoaded', function() {

  // Animation au scroll pour les cards (optionnel, à activer si souhaité)
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
  };

  const fadeInObserver = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);

  // Commenter cette partie si vous ne voulez pas d'animations
  /*
  const cards = document.querySelectorAll('.card, .article-card');
  cards.forEach(function(card) {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    fadeInObserver.observe(card);
  });
  */

});

// ============================================
// 8. GESTION DES LIENS EXTERNES
// ============================================

document.addEventListener('DOMContentLoaded', function() {

  // Ajouter target="_blank" et rel="noopener" aux liens externes
  const links = document.querySelectorAll('a[href^="http"]');

  links.forEach(function(link) {
    const currentHost = window.location.hostname;
    const linkHost = new URL(link.href).hostname;

    // Si le lien pointe vers un autre domaine
    if (linkHost !== currentHost) {
      if (!link.hasAttribute('target')) {
        link.setAttribute('target', '_blank');
      }
      if (!link.hasAttribute('rel')) {
        link.setAttribute('rel', 'noopener noreferrer');
      }
    }
  });

});

// ============================================
// 9. AMÉLIORATION PERFORMANCE
// ============================================

// Debounce function pour optimiser les événements scroll/resize
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = function() {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Exemple d'utilisation pour resize (si nécessaire)
/*
window.addEventListener('resize', debounce(function() {
  console.log('Window resized');
  // Code à exécuter au resize
}, 250));
*/

// ============================================
// 10. CONSOLE LOG (À RETIRER EN PRODUCTION)
// ============================================

console.log('Site Infirmière Libérale - Dunkerque');
console.log('Développé avec HTML5, CSS3 et JavaScript Vanilla');
console.log('Conforme RGPD et déontologie ONI');
