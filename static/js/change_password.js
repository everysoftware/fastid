document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("changePasswordForm").addEventListener("submit", (e) => {
        e.preventDefault();

        const newPassword = document.getElementById("newPassword").value;
        const confirmNewPassword = document.getElementById("confirmNewPassword").value;

        if (newPassword !== confirmNewPassword) {
            alert("New password and confirmation do not match.");
            return;
        }

        const passwordRegex = /^((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,20})$/;
        if (!passwordRegex.test(newPassword)) {
            alert("Password must be at least 8 characters long and include a number and a special character.");
            return;
        }

        fetch("/api/v1/users/me/password", {
            method: "PATCH",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({password: newPassword}),
        })
            .then((res) => {
                if (!res.ok) throw new Error("Failed to change password.");
                return res.json();
            })
            .then(() => {
                alert("Password changed successfully!");
                location.assign("/profile");
            })
            .catch((err) => alert(err.message));
    });
    document.getElementById("changePasswordBtn").addEventListener("click", () => {
        document.getElementById("changePasswordForm").requestSubmit();
    });
});
