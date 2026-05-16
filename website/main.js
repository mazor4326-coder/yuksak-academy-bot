// Language Settings
const langBtn = document.getElementById('lang-toggle');
const languages = ['uz', 'ru', 'en'];
let currentLangIndex = 0; // Default to UZ (index 0)

const translatableElements = document.querySelectorAll('[data-ru]');

function updateLanguage(index) {
    const lang = languages[index];
    if (langBtn) {
        langBtn.textContent = lang.toUpperCase();
    }
    
    translatableElements.forEach(el => {
        const text = el.getAttribute('data-' + lang);
        if (text) {
            el.textContent = text;
        }
    });
}

if (langBtn) {
    langBtn.addEventListener('click', () => {
        currentLangIndex = (currentLangIndex + 1) % languages.length;
        updateLanguage(currentLangIndex);
        
        // Add a small feedback effect
        langBtn.style.transform = 'scale(1.1)';
        setTimeout(() => langBtn.style.transform = 'scale(1)', 200);
    });
}

// Scroll Reveal Observer (Fallback included if API not supported)
if ('IntersectionObserver' in window) {
    const scrollOptions = {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
    };

    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('aos-animate');
                scrollObserver.unobserve(entry.target);
            }
        });
    }, scrollOptions);

    document.querySelectorAll('[data-aos]').forEach(el => {
        scrollObserver.observe(el);
    });
} else {
    // Fallback for older browsers or local file restrictions
    document.querySelectorAll('[data-aos]').forEach(el => {
        el.style.opacity = '1';
        el.style.transform = 'none';
    });
}

// Navbar Dynamics & Smooth Scrolling
const navbar = document.querySelector('.navbar');
if (navbar) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            navbar.style.top = '0.5rem';
            navbar.style.background = 'rgba(5, 5, 7, 0.95)';
            navbar.style.boxShadow = '0 10px 30px rgba(0,0,0,0.5)';
        } else {
            navbar.style.top = '1.5rem';
            navbar.style.background = 'rgba(255, 255, 255, 0.03)';
            navbar.style.boxShadow = 'none';
        }
    });
}



console.log('YUKSAK ACADEMY Site-Vizitka Loaded.');
