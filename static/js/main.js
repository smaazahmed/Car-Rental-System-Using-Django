document.addEventListener("DOMContentLoaded", function () {
    // -------------------------------------------------------------
    // 1. Dark/Light Theme Manager
    // -------------------------------------------------------------
    const themeToggleBtn = document.getElementById("theme-toggle");
    const currentTheme = localStorage.getItem("theme") || "light";

    // Set initial theme
    document.documentElement.setAttribute("data-theme", currentTheme);
    updateThemeIcon(currentTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", function () {
            let activeTheme = document.documentElement.getAttribute("data-theme");
            let targetTheme = activeTheme === "dark" ? "light" : "dark";
            
            document.documentElement.setAttribute("data-theme", targetTheme);
            localStorage.setItem("theme", targetTheme);
            updateThemeIcon(targetTheme);
            
            // Show toast message
            showToast("Theme switched to " + targetTheme.toUpperCase() + " mode!", "info");
        });
    }

    function updateThemeIcon(theme) {
        const icon = document.getElementById("theme-toggle-icon");
        if (icon) {
            if (theme === "dark") {
                icon.className = "fas fa-sun"; // Sun icon for light mode option
            } else {
                icon.className = "fas fa-moon"; // Moon icon for dark mode option
            }
        }
    }

    // -------------------------------------------------------------
    // 2. Toast Notification System
    // -------------------------------------------------------------
    window.showToast = function (message, type = "success") {
        const container = document.getElementById("toast-container");
        if (!container) return;

        const toast = document.createElement("div");
        toast.className = `toast-premium animate-fade-in d-flex align-items-center gap-3 p-3 bg-white text-dark shadow rounded-3 border-start border-4 border-${type === "success" ? "success" : type === "info" ? "primary" : type === "warning" ? "warning" : "danger"}`;
        
        let iconClass = "fa-check-circle text-success";
        if (type === "info") iconClass = "fa-info-circle text-primary";
        else if (type === "warning") iconClass = "fa-exclamation-triangle text-warning";
        else if (type === "danger") iconClass = "fa-times-circle text-danger";

        toast.innerHTML = `
            <i class="fas ${iconClass} fs-4"></i>
            <div class="flex-grow-1 font-weight-500">${message}</div>
            <button class="btn-close ms-auto fs-7" onclick="this.parentElement.remove()"></button>
        `;

        container.appendChild(toast);
        setTimeout(() => {
            toast.remove();
        }, 5000);
    };

    // -------------------------------------------------------------
    // 3. Search Autocomplete Suggestions
    // -------------------------------------------------------------
    const searchInput = document.getElementById("search-input");
    const suggestionBox = document.getElementById("search-suggestions");

    if (searchInput && suggestionBox) {
        let debounceTimer;
        searchInput.addEventListener("input", function () {
            clearTimeout(debounceTimer);
            const val = this.value.trim();
            if (val.length < 2) {
                suggestionBox.style.display = "none";
                return;
            }

            debounceTimer = setTimeout(() => {
                fetch(`/cars/suggestions/?term=${encodeURIComponent(val)}`)
                    .then(res => res.json())
                    .then(data => {
                        suggestionBox.innerHTML = "";
                        if (data.length > 0) {
                            suggestionBox.style.display = "block";
                            data.forEach(item => {
                                const el = document.createElement("div");
                                el.className = "suggestion-item";
                                el.innerText = item.label;
                                el.addEventListener("click", () => {
                                    searchInput.value = item.label;
                                    suggestionBox.style.display = "none";
                                    // Submit search form
                                    searchInput.closest("form").submit();
                                });
                                suggestionBox.appendChild(el);
                            });
                        } else {
                            suggestionBox.style.display = "none";
                        }
                    });
            }, 300);
        });

        // Hide suggestions on outside click
        document.addEventListener("click", function (e) {
            if (e.target !== searchInput && e.target !== suggestionBox) {
                suggestionBox.style.display = "none";
            }
        });
    }

    // -------------------------------------------------------------
    // 4. AJAX Live Filtering for Cars Listing
    // -------------------------------------------------------------
    const filterForm = document.getElementById("filter-form");
    const carListContainer = document.getElementById("car-list-container");

    if (filterForm && carListContainer) {
        const inputs = filterForm.querySelectorAll("input, select");
        inputs.forEach(input => {
            input.addEventListener("change", triggerAJAXFilter);
            if (input.type === "text" || input.type === "number") {
                input.addEventListener("input", debounce(triggerAJAXFilter, 400));
            }
        });

        // Handle sort dropdown change outside form if exists
        const sortSelect = document.getElementById("sort-by-select");
        if (sortSelect) {
            sortSelect.addEventListener("change", function () {
                const sortInput = document.getElementById("sort-by-hidden");
                if (sortInput) {
                    sortInput.value = this.value;
                    triggerAJAXFilter();
                }
            });
        }

        function triggerAJAXFilter() {
            const formData = new FormData(filterForm);
            // Include sort value if hidden input exists
            const sortInput = document.getElementById("sort-by-hidden");
            if (sortInput) formData.append("sort_by", sortInput.value);

            const searchParams = new URLSearchParams(formData);
            
            // Add loading spinner or visual indicator
            carListContainer.style.opacity = "0.5";

            // Update URL browser bar without reloading page
            history.pushState(null, "", "?" + searchParams.toString());

            fetch("?" + searchParams.toString(), {
                headers: { "X-Requested-With": "XMLHttpRequest" }
            })
            .then(res => res.text())
            .then(html => {
                carListContainer.innerHTML = html;
                carListContainer.style.opacity = "1";
                // Re-bind click handlers for items (like favorites or sliders)
                bindWishlistButtons();
            })
            .catch(err => {
                carListContainer.style.opacity = "1";
                console.error("Filtering error: ", err);
            });
        }
    }

    // -------------------------------------------------------------
    // 5. AJAX Wishlist Favorites toggler
    // -------------------------------------------------------------
    function bindWishlistButtons() {
        const favButtons = document.querySelectorAll(".fav-btn-toggle");
        favButtons.forEach(btn => {
            // Remove previous listener to avoid multiples
            btn.replaceWith(btn.cloneNode(true));
        });

        // Re-query and bind
        document.querySelectorAll(".fav-btn-toggle").forEach(btn => {
            btn.addEventListener("click", function (e) {
                e.preventDefault();
                e.stopPropagation();
                const carId = this.dataset.carId;
                
                fetch(`/accounts/favorites/toggle/${carId}/`, {
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        if (data.is_favorite) {
                            this.classList.add("active");
                            this.innerHTML = '<i class="fas fa-heart"></i>';
                            showToast(data.message, "success");
                        } else {
                            this.classList.remove("active");
                            this.innerHTML = '<i class="far fa-heart"></i>';
                            showToast(data.message, "info");
                        }
                    }
                })
                .catch(err => {
                    console.error("Wishlist action failed: ", err);
                });
            });
        });
    }
    
    // Initial binding
    bindWishlistButtons();

    // -------------------------------------------------------------
    // 6. Dynamic Booking Checkout Pricing calculation
    // -------------------------------------------------------------
    const pickupInput = document.getElementById("pickup_date");
    const returnInput = document.getElementById("return_date");
    const pricePerDayVal = document.getElementById("price-per-day-val");

    if (pickupInput && returnInput && pricePerDayVal) {
        const daysLabel = document.getElementById("checkout-days");
        const basePriceLabel = document.getElementById("checkout-base-price");
        const serviceFeeLabel = document.getElementById("checkout-service-fee");
        const grandTotalLabel = document.getElementById("checkout-grand-total");
        const pricePerDay = parseFloat(pricePerDayVal.value);

        function updatePricingPreview() {
            const pDate = new Date(pickupInput.value);
            const rDate = new Date(returnInput.value);

            if (!isNaN(pDate) && !isNaN(rDate) && rDate >= pDate) {
                const diffTime = Math.abs(rDate - pDate);
                const diffDays = Math.max(Math.ceil(diffTime / (1000 * 60 * 60 * 24)), 1);

                const basePrice = pricePerDay * diffDays;
                const fee = basePrice * 0.05;
                const grandTotal = basePrice + fee;

                // Update UI elements
                if (daysLabel) daysLabel.innerText = `${diffDays} Day${diffDays > 1 ? 's' : ''}`;
                if (basePriceLabel) basePriceLabel.innerText = `$${basePrice.toFixed(2)}`;
                if (serviceFeeLabel) serviceFeeLabel.innerText = `$${fee.toFixed(2)}`;
                if (grandTotalLabel) grandTotalLabel.innerText = `$${grandTotal.toFixed(2)}`;
            }
        }

        pickupInput.addEventListener("change", updatePricingPreview);
        returnInput.addEventListener("change", updatePricingPreview);
    }

    // Helper functions
    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
});
