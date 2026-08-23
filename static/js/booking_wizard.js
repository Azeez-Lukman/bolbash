/**
 * Bolbash Beauty Spot — Multi-Step Booking Wizard & Availability Slot Manager
 */

document.addEventListener('DOMContentLoaded', () => {
    let currentStep = 1;
    const totalSteps = 4;

    const stepElements = {
        1: document.getElementById('step-1-content'),
        2: document.getElementById('step-2-content'),
        3: document.getElementById('step-3-content'),
        4: document.getElementById('step-4-content'),
    };

    const stepIndicators = {
        1: document.getElementById('step-1-indicator'),
        2: document.getElementById('step-2-indicator'),
        3: document.getElementById('step-3-indicator'),
        4: document.getElementById('step-4-indicator'),
    };

    const prevBtn = document.getElementById('prev-step-btn');
    const nextBtn = document.getElementById('next-step-btn');
    const submitBtn = document.getElementById('submit-booking-btn');

    // Hidden Inputs
    const inputServiceId = document.getElementById('id_service_id');
    const inputDate = document.getElementById('id_appointment_date');
    const inputTime = document.getElementById('id_appointment_time');

    // Form inputs
    const inputName = document.getElementById('id_customer_name');
    const inputPhone = document.getElementById('id_customer_phone');
    const inputEmail = document.getElementById('id_customer_email');

    // UI elements
    const timeSlotsContainer = document.getElementById('time-slots-container');
    const slotsLoadingState = document.getElementById('slots-loading');
    const slotsEmptyState = document.getElementById('slots-empty');
    const slotsMessage = document.getElementById('slots-message');

    // Summary elements
    const summaryService = document.getElementById('summary-service-name');
    const summaryDate = document.getElementById('summary-date');
    const summaryTime = document.getElementById('summary-time');
    const summaryPrice = document.getElementById('summary-price');
    const summaryCustomer = document.getElementById('summary-customer-name');
    const summaryContact = document.getElementById('summary-customer-contact');

    // State Variables
    let selectedServiceName = '';
    let selectedServicePrice = '';

    function updateWizardUI() {
        for (let i = 1; i <= totalSteps; i++) {
            if (stepElements[i]) {
                if (i === currentStep) {
                    stepElements[i].classList.remove('hidden');
                } else {
                    stepElements[i].classList.add('hidden');
                }
            }

            if (stepIndicators[i]) {
                if (i < currentStep) {
                    stepIndicators[i].className = 'w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold text-xs';
                    stepIndicators[i].textContent = '✓';
                } else if (i === currentStep) {
                    stepIndicators[i].className = 'w-8 h-8 rounded-full bg-brand-pink text-white flex items-center justify-center font-bold text-xs ring-4 ring-brand-pink/20';
                    stepIndicators[i].textContent = i;
                } else {
                    stepIndicators[i].className = 'w-8 h-8 rounded-full bg-brand-neutral-200 text-brand-neutral-500 flex items-center justify-center font-bold text-xs';
                    stepIndicators[i].textContent = i;
                }
            }
        }

        // Control Nav Buttons
        if (prevBtn) {
            if (currentStep === 1) {
                prevBtn.classList.add('hidden');
            } else {
                prevBtn.classList.remove('hidden');
            }
        }

        if (nextBtn && submitBtn) {
            if (currentStep === totalSteps) {
                nextBtn.classList.add('hidden');
                submitBtn.classList.remove('hidden');
            } else {
                nextBtn.classList.remove('hidden');
                submitBtn.classList.add('hidden');
            }
        }

        if (currentStep === 4) {
            updateSummary();
        }
    }

    function validateCurrentStep() {
        if (currentStep === 1) {
            if (!inputServiceId.value) {
                alert('Please select a service before proceeding.');
                return false;
            }
        } else if (currentStep === 2) {
            if (!inputDate.value) {
                alert('Please choose an appointment date.');
                return false;
            }
            if (!inputTime.value) {
                alert('Please select an available time slot.');
                return false;
            }
        } else if (currentStep === 3) {
            if (!inputName.value.trim() || !inputPhone.value.trim() || !inputEmail.value.trim()) {
                alert('Please fill in your Name, Phone Number, and Email.');
                return false;
            }
        }
        return true;
    }

    // Step 1: Service Card Selection
    const serviceCards = document.querySelectorAll('.service-select-card');
    serviceCards.forEach(card => {
        card.addEventListener('click', () => {
            serviceCards.forEach(c => {
                c.classList.remove('border-brand-pink', 'ring-2', 'ring-brand-pink', 'bg-brand-pink-50/30');
            });

            card.classList.add('border-brand-pink', 'ring-2', 'ring-brand-pink', 'bg-brand-pink-50/30');
            
            const serviceId = card.getAttribute('data-service-id');
            selectedServiceName = card.getAttribute('data-service-name');
            selectedServicePrice = card.getAttribute('data-service-price');
            
            inputServiceId.value = serviceId;

            // Reset time selection if service changes
            inputTime.value = '';
            if (inputDate.value) {
                fetchAvailableSlots();
            }
        });

        // Pre-select logic if initialized
        if (card.getAttribute('data-preselected') === 'true') {
            card.click();
        }
    });

    // Step 2: Date Change & AJAX Time Slots
    if (inputDate) {
        // Set min date to today
        const today = new Date().toISOString().split('T')[0];
        inputDate.setAttribute('min', today);

        inputDate.addEventListener('change', () => {
            inputTime.value = '';
            fetchAvailableSlots();
        });
    }

    function fetchAvailableSlots() {
        const serviceId = inputServiceId.value;
        const dateVal = inputDate.value;

        if (!serviceId || !dateVal) return;

        if (slotsLoadingState) slotsLoadingState.classList.remove('hidden');
        if (slotsEmptyState) slotsEmptyState.classList.add('hidden');
        if (timeSlotsContainer) timeSlotsContainer.innerHTML = '';

        fetch(`/booking/api/available-slots/?service_id=${serviceId}&date=${dateVal}`)
            .then(res => res.json())
            .then(data => {
                if (slotsLoadingState) slotsLoadingState.classList.add('hidden');

                if (data.slots && data.slots.length > 0) {
                    timeSlotsContainer.innerHTML = '';
                    data.slots.forEach(slot => {
                        const slotBtn = document.createElement('button');
                        slotBtn.type = 'button';
                        slotBtn.className = 'py-3 px-4 rounded-xl border border-brand-neutral-200 text-sm font-semibold text-brand-black bg-white hover:border-brand-pink hover:text-brand-pink transition-all focus:outline-none focus:ring-2 focus:ring-brand-pink';
                        
                        // Format slot nicely (e.g. 09:00 -> 09:00 AM)
                        const [hrs, mins] = slot.split(':');
                        const h = parseInt(hrs, 10);
                        const ampm = h >= 12 ? 'PM' : 'AM';
                        const displayHrs = h % 12 || 12;
                        const formattedDisplay = `${displayHrs.toString().padStart(2, '0')}:${mins} ${ampm}`;

                        slotBtn.textContent = formattedDisplay;

                        slotBtn.addEventListener('click', () => {
                            const allBtns = timeSlotsContainer.querySelectorAll('button');
                            allBtns.forEach(b => {
                                b.classList.remove('bg-brand-pink', 'text-white', 'border-brand-pink');
                                b.classList.add('bg-white', 'text-brand-black', 'border-brand-neutral-200');
                            });

                            slotBtn.classList.remove('bg-white', 'text-brand-black', 'border-brand-neutral-200');
                            slotBtn.classList.add('bg-brand-pink', 'text-white', 'border-brand-pink');
                            
                            inputTime.value = slot;
                        });

                        timeSlotsContainer.appendChild(slotBtn);
                    });
                } else {
                    if (slotsEmptyState) slotsEmptyState.classList.remove('hidden');
                    if (slotsMessage) slotsMessage.textContent = data.message || 'No appointment slots available.';
                }
            })
            .catch(err => {
                if (slotsLoadingState) slotsLoadingState.classList.add('hidden');
                if (slotsEmptyState) slotsEmptyState.classList.remove('hidden');
                if (slotsMessage) slotsMessage.textContent = 'Error loading available slots. Please try again.';
            });
    }

    function updateSummary() {
        if (summaryService) summaryService.textContent = selectedServiceName || 'Not Selected';
        if (summaryDate) summaryDate.textContent = inputDate.value || 'Not Selected';
        if (summaryTime) summaryTime.textContent = inputTime.value || 'Not Selected';
        if (summaryPrice) summaryPrice.textContent = selectedServicePrice ? `₦${selectedServicePrice}` : 'Price on enquiry';
        if (summaryCustomer) summaryCustomer.textContent = inputName.value || 'Not Entered';
        if (summaryContact) summaryContact.textContent = `${inputPhone.value} • ${inputEmail.value}`;
    }

    // Step Nav Button Event Listeners
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (validateCurrentStep()) {
                currentStep = Math.min(currentStep + 1, totalSteps);
                updateWizardUI();
                window.scrollTo({ top: 100, behavior: 'smooth' });
            }
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            currentStep = Math.max(currentStep - 1, 1);
            updateWizardUI();
            window.scrollTo({ top: 100, behavior: 'smooth' });
        });
    }

    // Initialize UI State
    updateWizardUI();
});
