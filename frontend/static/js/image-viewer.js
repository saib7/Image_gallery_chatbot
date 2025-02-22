// Animation for page load
gsap.from('.rounded-lg', {
    opacity: 0,
    y: 20,
    duration: 0.8,
    ease: 'power3.out'
});

gsap.from('.tag', {
    opacity: 1,  // Keep the tags at full opacity from the start
    y: 10,
    duration: 0.5,
    stagger: 0.1,
    ease: 'power3.out',
    delay: 0.3
});


// Initialize zoom on scroll and click
const image = document.getElementById('zoomImage');
let scale = 1;  // Default scale

// Scroll zoom
image.addEventListener('wheel', (e) => {
    if (e.deltaY > 0) {
        // Zoom out
        scale -= 0.1;
    } else {
        // Zoom in
        scale += 0.1;
    }

    // Limit scale range
    scale = Math.min(Math.max(scale, 1), 3);

    // Apply the zoom
    image.style.transform = `scale(${scale})`;
});

// Click zoom
image.addEventListener('click', () => {
    // Toggle zoom state
    if (scale === 1) {
        scale = 2;  // Zoom in to 2x
    } else {
        scale = 1;  // Zoom out to 1x
    }

    // Apply the zoom
    image.style.transform = `scale(${scale})`;
});

