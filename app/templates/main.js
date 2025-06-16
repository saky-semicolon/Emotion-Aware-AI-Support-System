document.addEventListener('DOMContentLoaded', () => {
    // Add smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Add logo hover effect
    const logo = document.querySelector('.logo');
    if(logo) {
        logo.addEventListener('mouseenter', () => {
            logo.style.transform = 'scale(1.05) rotate(-5deg)';
        });
        logo.addEventListener('mouseleave', () => {
            logo.style.transform = 'none';
        });
    }
});
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');

    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Clear previous errors
        document.querySelectorAll('.error').forEach(el => el.remove());

        let isValid = true;

        // Validate username
        if(usernameInput.value.trim() === '') {
            showError(usernameInput, 'Username is required');
            isValid = false;
        }

        // Validate password
        if(passwordInput.value.trim() === '') {
            showError(passwordInput, 'Password is required');
            isValid = false;
        }

        if(isValid) {
            // Add loading animation
            loginForm.classList.add('animate__animated', 'animate__zoomOut');
            
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 500);
        }
    });

    function showError(input, message) {
        const error = document.createElement('div');
        error.className = 'error animate__animated animate__shakeX';
        error.textContent = message;
        error.style.color = '#e74c3c';
        error.style.fontSize = '0.9rem';
        error.style.marginTop = '0.5rem';
        input.parentElement.appendChild(error);
    }
});


// Additional Work
document.addEventListener('DOMContentLoaded', () => {

    // --- Sticky Header ---
    const header = document.querySelector('.site-header');
    const heroSection = document.getElementById('hero-section');
    const headerHeight = header.offsetHeight;
    let lastScrollTop = 0;

    // Add a class to the body when the header is sticky
    const body = document.body;

    const checkSticky = () => {
        let scrollTop = window.scrollY;

        // Add sticky class if scrolled past the header height
        if (scrollTop > headerHeight) {
            header.classList.add('sticky');
             body.classList.add('header-is-sticky'); // Add class to body
        } else {
            header.classList.remove('sticky');
             body.classList.remove('header-is-sticky'); // Remove class from body
        }

        // Optional: Hide header on scroll down, show on scroll up (more complex)
        // if (scrollTop > lastScrollTop && scrollTop > headerHeight) {
        //     // Scrolling down
        //     header.classList.add('hidden');
        // } else {
        //     // Scrolling up
        //     header.classList.remove('hidden');
        // }
        // lastScrollTop = scrollTop;
    };

    window.addEventListener('scroll', checkSticky);
    checkSticky(); // Run on page load


    // --- Smooth Scrolling for Navigation Links ---
    document.querySelectorAll('.main-nav a[href^="#"], .mobile-nav-overlay a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            // Close mobile menu if open
            const mobileNav = document.querySelector('.mobile-nav-overlay');
            const menuToggle = document.querySelector('.menu-toggle');
             if (mobileNav.classList.contains('open')) {
                 mobileNav.classList.remove('open');
                 // Optionally remove body overflow-hidden class if added by mobile menu toggle
                 // document.body.classList.remove('overflow-hidden');
             }


            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            const headerOffset = header.offsetHeight; // Account for fixed header

            if (targetElement) {
                 // Scroll slightly above the section if header is sticky
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.scrollY - headerOffset - 20; // Added 20px buffer

                window.scrollTo({
                    top: offsetPosition,
                    behavior: "smooth"
                });
            }
        });
    });


    // --- Scroll Animations using Intersection Observer ---
    const elementsToAnimate = document.querySelectorAll('.animate-on-scroll');

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Element is visible
                entry.target.classList.add('animated');
                observer.unobserve(entry.target); // Stop observing once animated
            }
        });
    }, {
        threshold: 0.1, // Trigger when 10% of the element is visible
        rootMargin: '0px 0px -50px 0px' // Start animation 50px before reaching the bottom of the viewport
    });

    elementsToAnimate.forEach(element => {
        observer.observe(element);
    });


    // --- Mobile Menu Toggle ---
    const menuToggle = document.querySelector('.menu-toggle');
    const mobileNavOverlay = document.querySelector('.mobile-nav-overlay');

    if (menuToggle && mobileNavOverlay) {
        menuToggle.addEventListener('click', () => {
            mobileNavOverlay.classList.toggle('open');
             // Optional: Prevent scrolling when mobile menu is open
             // document.body.classList.toggle('overflow-hidden');
        });
    }


    // --- Footer Year ---
    const currentYearSpan = document.getElementById('current-year');
    if (currentYearSpan) {
        currentYearSpan.textContent = new Date().getFullYear();
    }


    // --- Add other interactive features here ---
    // Example: Demo button action (if not a link to a new page)
    // const demoButton = document.querySelector('#demo-section .btn-primary');
    // if (demoButton) {
    //     demoButton.addEventListener('click', (e) => {
    //         e.preventDefault();
    //         // Add code here to open a modal, start audio recording, etc.
    //         console.log('Demo button clicked!');
    //         alert('Demo feature coming soon!'); // Replace with actual demo logic
    //     });
    // }

});