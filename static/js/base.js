document.addEventListener('DOMContentLoaded', () => {
    // Verification Modal
    const otpInputs = document.querySelectorAll('.otp-input');
    otpInputs.forEach((input, index) => {
        input.addEventListener('input', (event) => {
            const {value} = event.target;
            if (!/^\d?$/.test(value)) {
                event.target.value = '';
                return;
            }
            if (value && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }
        });
        input.addEventListener('keydown', (event) => {
            const {key} = event;
            if (key === 'Backspace' && index > 0 && input.value === '') {
                otpInputs[index - 1].focus();
            }
        });
    });
});
