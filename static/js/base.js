'use strict';

document.addEventListener('DOMContentLoaded', () => {
    // One-time password (OTP) input
    const codeInputContainer = document.getElementById("codeInputContainer");
    if (!codeInputContainer) {
        return;
    }
    const codeInputs = codeInputContainer.querySelectorAll("input[type='text']");
    const fullCodeInput = document.getElementById("fullCodeInput");

    const updateFullCode = () => {
        fullCodeInput.value = Array.from(codeInputs).map((input) => input.value).join("");
    };

    codeInputs.forEach((input, index) => {
        // Обработка ввода символов
        input.addEventListener("input", () => {
            if (input.value.length > 1) {
                input.value = input.value.charAt(0); // Ограничение на 1 символ
            }
            updateFullCode();
            if (index < codeInputs.length - 1 && input.value) {
                codeInputs[index + 1].focus();
            }
        });

        // Обработка Backspace
        input.addEventListener("keydown", (e) => {
            if (e.key === "Backspace" && !input.value && index > 0) {
                codeInputs[index - 1].focus();
            }
        });

        // Обработка вставки из буфера обмена
        input.addEventListener("paste", (e) => {
            e.preventDefault();
            const pasteData = (e.clipboardData || window.clipboardData).getData("text").slice(0, 6);
            pasteData.split("").forEach((char, i) => {
                if (i < codeInputs.length) {
                    codeInputs[i].value = char;
                }
            });
            updateFullCode();
            codeInputs[Math.min(pasteData.length, codeInputs.length - 1)].focus();
        });
    });
});
