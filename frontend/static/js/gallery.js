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

// Modal functionality
const modal = document.getElementById('image-modal');
const modalImage = document.getElementById('modal-image');
const closeModal = document.getElementById('close-modal');
const galleryItems = document.querySelectorAll('.gallery-item');

galleryItems.forEach(item => {
    item.addEventListener('click', () => {
        const imgSrc = item.querySelector('img').src;
        modalImage.src = imgSrc;
        modal.classList.remove('hidden');
        setTimeout(() => {
            modal.classList.remove('opacity-0');
        }, 10);
    });
});

closeModal.addEventListener('click', () => {
    modal.classList.add('opacity-0');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 300);
});

modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        closeModal.click();
    }
});

// GSAP Animations
gsap.registerPlugin(ScrollTrigger);

gsap.from('.gallery-item', {
    scrollTrigger: {
        trigger: '#gallery-grid',
        start: 'top center'
    },
    y: 60,
    opacity: 0,
    duration: 1,
    stagger: 0.2
});