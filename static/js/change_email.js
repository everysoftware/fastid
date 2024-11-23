document.addEventListener("DOMContentLoaded", () => {
    const sendCodeButton = document.getElementById("sendCodeButton");
    const codeInputContainer = document.getElementById("codeInputContainer");
    const confirmButton = document.getElementById("confirmButton");
    const codeInputs = codeInputContainer.querySelectorAll("input[type='text']");
    const fullCodeInput = document.getElementById("fullCodeInput");

    // Отправка кода
    sendCodeButton.addEventListener("click", () => {
        const email = document.getElementById("newEmail").value;
        if (!email) {
            alert("Please enter a valid email address.");
            return;
        }
        fetch(`/api/v1/notify/otp?new_email=${email}`, {
            method: "POST"
        })
            .then((res) => {
                if (!res.ok) throw new Error("Failed to send code.");
                return res.json();
            })
            .then(() => {
                codeInputContainer.classList.remove("d-none");
                confirmButton.disabled = false;
            })
            .catch((err) => alert(err.message));
    });

    // Сбор кода
    codeInputs.forEach((input, index) => {
        input.addEventListener("input", () => {
            if (index < codeInputs.length - 1 && input.value.length === 1) {
                codeInputs[index + 1].focus();
            }
            fullCodeInput.value = Array.from(codeInputs).map((input) => input.value).join("");
        });
    });

    // Подтверждение смены
    document.getElementById("emailChangeForm").addEventListener("submit", (e) => {
        e.preventDefault();

        const email = document.getElementById("newEmail").value;
        const code = fullCodeInput.value;

        if (code.length !== 6) {
            alert("Please enter the complete verification code.");
            return;
        }

        fetch(`/api/v1/users/me/email`, {
            method: "PATCH",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({code: code, new_email: email})
        })
            .then((res) => {
                if (!res.ok) throw new Error("Failed to update email.");
                return res.json();
            })
            .then(() => {
                alert("Email updated successfully!");
                location.assign("/profile")
            })
            .catch((err) => alert(err.message));
    });
});
