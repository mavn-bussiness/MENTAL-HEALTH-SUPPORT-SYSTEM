// Shared Authentication Scripts

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    initializeCrisisBanner();
    initializeFloatingHelp();
    initializeFormValidation();
    
    // Initialize multi-step form if present
    if (document.getElementById('multi-step-form')) {
        initializeMultiStepForm();
    }
});

// Crisis banner functionality
function initializeCrisisBanner() {
    const closeBanner = document.getElementById('closeCrisisBanner');
    const banner = document.getElementById('crisisBanner');
    
    if (closeBanner && banner) {
        closeBanner.addEventListener('click', function() {
            banner.style.display = 'none';
            // Store preference in session storage
            sessionStorage.setItem('crisisBannerClosed', 'true');
        });
        
        // Check if banner was previously closed
        if (sessionStorage.getItem('crisisBannerClosed') === 'true') {
            banner.style.display = 'none';
        }
    }
}

// Floating help button functionality
function initializeFloatingHelp() {
    const helpButton = document.getElementById('helpButton');
    if (helpButton) {
        helpButton.addEventListener('click', function() {
            window.open('tel:0800-21-21-21', '_self');
        });
    }
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Email validation
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        }
    });
    
    // Password confirmation
    const password1 = form.querySelector('input[name="password1"]');
    const password2 = form.querySelector('input[name="password2"]');
    
    if (password1 && password2) {
        if (password1.value !== password2.value) {
            showFieldError(password2, 'Passwords do not match');
            isValid = false;
        }
    }
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorElement = document.createElement('div');
    errorElement.className = 'field-error';
    errorElement.style.color = '#dc2626';
    errorElement.style.fontSize = '12px';
    errorElement.style.marginTop = '4px';
    errorElement.textContent = message;
    
    field.parentNode.appendChild(errorElement);
    field.style.borderColor = '#dc2626';
}

function clearFieldError(field) {
    const errorElement = field.parentNode.querySelector('.field-error');
    if (errorElement) {
        errorElement.remove();
    }
    field.style.borderColor = '#d1d5db';
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Multi-step form functionality
function initializeMultiStepForm() {
    window.currentStep = 1;
    window.totalSteps = document.querySelectorAll('.form-step').length;
    
    updateStepDisplay();
    updateProgressIndicator();
}

function nextStep(step) {
    if (step && step <= window.totalSteps) {
        // Validate current step before proceeding
        if (validateCurrentStep()) {
            window.currentStep = step;
            updateStepDisplay();
            updateProgressIndicator();
            scrollToTop();
        }
    }
}

function prevStep(step) {
    if (step && step >= 1) {
        window.currentStep = step;
        updateStepDisplay();
        updateProgressIndicator();
        scrollToTop();
    }
}

function validateCurrentStep() {
    const currentStepElement = document.getElementById(`step-${window.currentStep}`);
    if (!currentStepElement) return true;
    
    const requiredFields = currentStepElement.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    return isValid;
}

function updateStepDisplay() {
    document.querySelectorAll('.form-step').forEach((step, index) => {
        step.classList.toggle('hidden', index + 1 !== window.currentStep);
    });
}

function updateProgressIndicator() {
    const progressSteps = document.querySelectorAll('.progress-step');
    
    progressSteps.forEach((step, index) => {
        const stepNumber = index + 1;
        step.classList.remove('active', 'completed');
        
        if (stepNumber < window.currentStep) {
            step.classList.add('completed');
        } else if (stepNumber === window.currentStep) {
            step.classList.add('active');
        }
    });
}

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Password strength checker
function checkPasswordStrength(password) {
    const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /\d/.test(password),
        special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };
    
    const strength = Object.values(requirements).filter(Boolean).length;
    
    return {
        requirements,
        strength,
        score: strength / 5
    };
}

// Real-time password validation
function initializePasswordValidation() {
    const passwordField = document.querySelector('input[name="password1"]');
    if (passwordField) {
        passwordField.addEventListener('input', function() {
            const strength = checkPasswordStrength(this.value);
            updatePasswordRequirements(strength.requirements);
        });
    }
}

function updatePasswordRequirements(requirements) {
    const requirementsList = document.querySelector('.password-requirements ul');
    if (!requirementsList) return;
    
    const items = requirementsList.querySelectorAll('li');
    const checks = [
        requirements.length,
        requirements.uppercase && requirements.lowercase,
        requirements.number,
        requirements.special
    ];
    
    items.forEach((item, index) => {
        if (checks[index]) {
            item.style.color = '#10b981';
            item.style.fontWeight = '500';
        } else {
            item.style.color = '#6b7280';
            item.style.fontWeight = '400';
        }
    });
}

// Smooth page transitions
function initializePageTransitions() {
    // Add fade-in effect to main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.style.opacity = '0';
        mainContent.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            mainContent.style.transition = 'all 0.5s ease';
            mainContent.style.opacity = '1';
            mainContent.style.transform = 'translateY(0)';
        }, 100);
    }
}

// Utility functions
function showAlert(message, type = 'error') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type}`;
    alertElement.innerHTML = `
        <svg class="alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="${type === 'error' ? 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z' : 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'}">
            </path>
        </svg>
        <div>${message}</div>
    `;
    
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alertElement);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertElement.remove();
    }, 5000);
}

// Form submission with loading state
function handleFormSubmission(form, submitButton) {
    const originalText = submitButton.textContent;
    const originalHTML = submitButton.innerHTML;
    
    submitButton.disabled = true;
    submitButton.innerHTML = `
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Processing...
    `;
    
    // Reset button after 30 seconds (fallback)
    setTimeout(() => {
        submitButton.disabled = false;
        submitButton.innerHTML = originalHTML;
    }, 30000);
}

// Initialize all functionality
function initializePage() {
    initializeCrisisBanner();
    initializeFloatingHelp();
    initializeFormValidation();
    initializePasswordValidation();
    initializePageTransitions();
    
    if (document.getElementById('multi-step-form')) {
        initializeMultiStepForm();
    }
}

// Export functions for global use
window.nextStep = nextStep;
window.prevStep = prevStep;
window.showAlert = showAlert;
window.initializePage = initializePage;