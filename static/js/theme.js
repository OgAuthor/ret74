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
})();
