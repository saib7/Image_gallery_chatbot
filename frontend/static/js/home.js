// Navbar scroll effect
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('bg-white', 'shadow-md');
        navbar.classList.remove('bg-transparent');
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('text-gray-100');
            link.classList.add('text-gray-800');
        });
    } else {
        navbar.classList.remove('bg-white', 'shadow-md');
        navbar.classList.add('bg-transparent');
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.add('text-gray-100');
            link.classList.remove('text-gray-800');
        });
    }
});

// GSAP Animations
gsap.registerPlugin(ScrollTrigger);

gsap.from('.feature-card', {
    scrollTrigger: {
        trigger: '#features',
        start: 'top center'
    },
    y: 60,
    opacity: 0,
    duration: 1,
    stagger: 0.2
});