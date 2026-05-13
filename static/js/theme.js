(() => {
    const root = document.documentElement;
    const button = document.getElementById("themeToggle");
    const savedTheme = localStorage.getItem("theme");
    const preferredTheme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    const initialTheme = savedTheme || preferredTheme;

    root.setAttribute("data-bs-theme", initialTheme);

    if (button) {
        button.addEventListener("click", () => {
            const current = root.getAttribute("data-bs-theme");
            const next = current === "dark" ? "light" : "dark";
            root.setAttribute("data-bs-theme", next);
            localStorage.setItem("theme", next);
        });
    }

    const formatPhone = (value) => {
        let digits = value.replace(/\D/g, "");

        if (digits.startsWith("8")) {
            digits = `7${digits.slice(1)}`;
        }
        if (!digits.startsWith("7")) {
            digits = `7${digits}`;
        }

        digits = digits.slice(0, 11);
        const national = digits.slice(1);
        let formatted = "+7";

        if (national.length > 0) {
            formatted += ` (${national.slice(0, 3)}`;
        }
        if (national.length >= 3) {
            formatted += ")";
        }
        if (national.length > 3) {
            formatted += ` ${national.slice(3, 6)}`;
        }
        if (national.length > 6) {
            formatted += `-${national.slice(6, 8)}`;
        }
        if (national.length > 8) {
            formatted += `-${national.slice(8, 10)}`;
        }

        return formatted;
    };

    document.querySelectorAll("[data-phone-mask='ru']").forEach((input) => {
        input.addEventListener("input", () => {
            input.value = formatPhone(input.value);
        });
        input.addEventListener("focus", () => {
            if (!input.value) {
                input.value = "+7";
            }
        });
        input.addEventListener("blur", () => {
            if (input.value === "+7") {
                input.value = "";
            }
        });
        if (input.value) {
            input.value = formatPhone(input.value);
        }
    });
})();
