import {authClient} from './dependencies.js';

(function () {
    'use strict'

    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function (event) {
            event.preventDefault()
            if (!loginForm.checkValidity()) {
                event.stopPropagation()
                loginForm.classList.add('was-validated')
                return;
            }
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const response = await authClient.login(email, password);
            if (response) {
                location.reload();
            }
        }, false)

        document.getElementById("loginBtn").addEventListener("click", function (event) {
            loginForm.requestSubmit();
        });
    }

    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function (event) {
            event.preventDefault()
            if (!registerForm.checkValidity()) {
                event.stopPropagation()
                registerForm.classList.add('was-validated')
                return;
            }
            const name = document.getElementById("name").value;
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const response = await authClient.register(name, email, password);
            if (response) {
                location.assign("/authorize");
            }
        }, false)

        document.getElementById("registerBtn").addEventListener("click", function (event) {
            registerForm.requestSubmit();
        });
    }
})()
