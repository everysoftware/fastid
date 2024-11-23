document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/v1/notify/otp", {
        method: "POST"
    })
        .then((res) => {
            if (!res.ok) throw new Error("Failed to send code.");
            return res.json();
        })
        .catch((err) => alert(err.message));

    const nextButton = document.getElementById("nextButton");
    const codeInputContainer = document.getElementById("codeInputContainer");
    const codeInputs = codeInputContainer.querySelectorAll("input[type='text']");
    const fullCodeInput = document.getElementById("fullCodeInput");

    codeInputs.forEach((input, index) => {
        input.addEventListener("input", () => {
            if (index < codeInputs.length - 1 && input.value.length === 1) {
                codeInputs[index + 1].focus();
            }
            fullCodeInput.value = Array.from(codeInputs).map((input) => input.value).join("");
        });
    });

    nextButton.addEventListener("click", (e) => {
        e.preventDefault();
        const code = fullCodeInput.value;

        if (code.length !== 6) {
            alert("Please enter the complete verification code.");
            return;
        }

        fetch(`/api/v1/notify/verify-token`, {
            method: "POST", body: JSON.stringify({code: code}), headers: {"Content-Type": "application/json"}
        })
            .then((res) => {
                if (!res.ok) throw new Error("Failed to obtain verify token.");
                return res.json();
            })
            .then(() => {
                location.reload();
            })
            .catch((err) => alert(err.message));
    });
});
