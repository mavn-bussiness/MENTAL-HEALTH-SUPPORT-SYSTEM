// Mobile menu functionality
const mobileMenuButton = document.getElementById("mobileMenuButton");
const mobileMenu = document.getElementById("mobileMenu");

mobileMenuButton.addEventListener("click", () => {
  mobileMenu.classList.toggle("hidden");
});

// Navbar scroll effect
function updateNavbarOnScroll() {
    const header = document.getElementById('mainHeader');
    const brandName = document.getElementById('brandName');
    const navLinks = document.querySelectorAll('.nav-link');
    const crisisBanner = document.getElementById('crisisBanner');
    const scrollPosition = window.scrollY;
    
    // Check if crisis banner is visible
    const crisisBannerVisible = crisisBanner.style.transform !== 'translateY(-100%)';
    const crisisBannerHeight = crisisBannerVisible ? crisisBanner.offsetHeight : 0;
    const triggerPoint = crisisBannerHeight + 50;

    if (scrollPosition > triggerPoint) {
        // Scrolled state - solid background
        header.classList.remove('navbar-transparent');
        header.classList.add('navbar-solid');
        
        // Update text colors for solid background
        brandName.classList.remove('text-white');
        brandName.classList.add('text-gray-800');
        
        navLinks.forEach(link => {
            link.classList.remove('text-white', 'hover:text-blue-300');
            link.classList.add('text-gray-700', 'hover:text-blue-600');
        });
        
        // Update mobile menu button
        mobileMenuButton.classList.remove('text-white', 'hover:text-blue-300');
        mobileMenuButton.classList.add('text-gray-700', 'hover:text-blue-600');
        
    } else {
        // Top of page - transparent background
        header.classList.remove('navbar-solid');
        header.classList.add('navbar-transparent');
        
        // Update text colors for transparent background
        brandName.classList.remove('text-gray-800');
        brandName.classList.add('text-white');
        
        navLinks.forEach(link => {
            link.classList.remove('text-gray-700', 'hover:text-blue-600');
            link.classList.add('text-white', 'hover:text-blue-300');
        });
        
        // Update mobile menu button
        mobileMenuButton.classList.remove('text-gray-700', 'hover:text-blue-600');
        mobileMenuButton.classList.add('text-white', 'hover:text-blue-300');
    }
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      // Close mobile menu if open
      mobileMenu.classList.add("hidden");

      // Calculate offset for fixed header
      const headerHeight = document.getElementById("mainHeader").offsetHeight;
      const crisisBannerHeight =
        document.getElementById("crisisBanner").offsetHeight;
      const totalOffset = headerHeight + crisisBannerHeight;

      const targetPosition = target.offsetTop - totalOffset;

      window.scrollTo({
        top: targetPosition,
        behavior: "smooth",
      });
    }
  });
});

// Crisis banner functionality
const crisisBanner = document.getElementById("crisisBanner");
const mainHeader = document.getElementById("mainHeader");
const closeCrisisBanner = document.getElementById("closeCrisisBanner");
let crisisBannerClosed = false;
let lastScrollY = window.scrollY;

// Close crisis banner manually
closeCrisisBanner.addEventListener("click", () => {
  crisisBannerClosed = true;
  crisisBanner.style.transform = "translateY(-100%)";
  mainHeader.style.top = "0";

  // Update navbar immediately after closing banner
  updateNavbarOnScroll();

  // Store in localStorage so it stays closed during session
  localStorage.setItem("crisisBannerClosed", "true");
});

// Check if crisis banner was previously closed
if (localStorage.getItem("crisisBannerClosed") === "true") {
  crisisBannerClosed = true;
  crisisBanner.style.transform = "translateY(-100%)";
  mainHeader.style.top = "0";
}

// Handle scroll behavior for crisis banner and navbar
window.addEventListener("scroll", () => {
  const currentScrollY = window.scrollY;

  if (!crisisBannerClosed) {
    // Auto-hide crisis banner when scrolling down after 200px
    if (currentScrollY > 200 && currentScrollY > lastScrollY) {
      crisisBanner.style.transform = "translateY(-100%)";
      mainHeader.style.top = "0";
    }
    // Show crisis banner when scrolling up and near top
    else if (currentScrollY < 100 && currentScrollY < lastScrollY) {
      crisisBanner.style.transform = "translateY(0)";
      mainHeader.style.top = "40px"; // Adjust based on crisis banner height
    }
  }

  // Update navbar colors based on scroll position
  updateNavbarOnScroll();

  lastScrollY = currentScrollY;
});

// Floating help button functionality
const helpButton = document.getElementById("helpButton");
const helpModal = document.getElementById("helpModal");
const closeModal = document.getElementById("closeModal");

helpButton.addEventListener("click", () => {
  helpModal.classList.remove("hidden");
  helpModal.classList.add("flex");

  // Show crisis banner when help button is clicked
  if (crisisBannerClosed) {
    crisisBanner.style.transform = "translateY(0)";
    mainHeader.style.top = "40px";
    localStorage.removeItem("crisisBannerClosed");
    crisisBannerClosed = false;
    // Update navbar after showing banner
    updateNavbarOnScroll();
  }

  // Animate modal
  setTimeout(() => {
    helpModal.querySelector(".bg-white").style.transform = "scale(1)";
  }, 50);
});

closeModal.addEventListener("click", () => {
  closeHelpModal();
});

// Close modal when clicking outside
helpModal.addEventListener("click", (e) => {
  if (e.target === helpModal) {
    closeHelpModal();
  }
});

// Close modal with Escape key
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && helpModal.classList.contains("flex")) {
    closeHelpModal();
  }
});

function closeHelpModal() {
  helpModal.querySelector(".bg-white").style.transform = "scale(0.95)";
  setTimeout(() => {
    helpModal.classList.add("hidden");
    helpModal.classList.remove("flex");
  }, 200);
}

// Parallax effect for hero section
window.addEventListener("scroll", () => {
  const scrolled = window.scrollY;
  const rate = scrolled * -0.5;

  const hero = document.getElementById("home");
  if (hero && scrolled < hero.offsetHeight) {
    hero.style.transform = `translateY(${rate}px)`;
  }
});

// Initialize page
document.addEventListener("DOMContentLoaded", () => {
  // Ensure proper initial state
  if (!crisisBannerClosed) {
    crisisBanner.style.transform = "translateY(0)";
    mainHeader.style.top = "40px";
  }

  // Initialize navbar state
  updateNavbarOnScroll();

  // Add loading animation
  document.body.style.opacity = "0";
  setTimeout(() => {
    document.body.style.transition = "opacity 0.5s ease-in-out";
    document.body.style.opacity = "1";
  }, 100);
});

// Handle window resize
window.addEventListener("resize", () => {
  // Close mobile menu on resize
  mobileMenu.classList.add("hidden");
  // Update navbar on resize
  updateNavbarOnScroll();
});