/* ============================================
   Petrol Buddy – Online Petrol Delivery System
   Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* ------------------------------------------
     1. Mobile Sidebar Toggle
     ------------------------------------------ */
  const hamburgerBtn = document.getElementById('hamburgerBtn');
  const appSidebar = document.getElementById('appSidebar');
  const sidebarOverlay = document.getElementById('sidebarOverlay');

  if (hamburgerBtn && appSidebar) {
    hamburgerBtn.addEventListener('click', function () {
      appSidebar.classList.toggle('show');
      if (sidebarOverlay) {
        sidebarOverlay.classList.toggle('show');
      }
    });

    // Close sidebar when overlay is clicked
    if (sidebarOverlay) {
      sidebarOverlay.addEventListener('click', function () {
        appSidebar.classList.remove('show');
        sidebarOverlay.classList.remove('show');
      });
    }

    // Close sidebar on Escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && appSidebar.classList.contains('show')) {
        appSidebar.classList.remove('show');
        if (sidebarOverlay) {
          sidebarOverlay.classList.remove('show');
        }
      }
    });
  }

  /* ------------------------------------------
     2. Alert Auto-Dismiss (6 seconds)
     ------------------------------------------ */
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      dismissAlert(alert);
    }, 6000);
  });

  /* ------------------------------------------
     3. Alert Close Button Handler
     ------------------------------------------ */
  document.addEventListener('click', function (e) {
    const closeBtn = e.target.closest('.alert-close');
    if (closeBtn) {
      const alert = closeBtn.closest('.alert');
      if (alert) {
        dismissAlert(alert);
      }
    }
  });

  function dismissAlert(alertEl) {
    if (!alertEl || alertEl.classList.contains('fade-out')) return;
    alertEl.classList.add('fade-out');
    setTimeout(function () {
      alertEl.remove();
    }, 400);
  }

  /* ------------------------------------------
     4. Live Fuel Order Price Calculation
     ------------------------------------------ */
  const fuelTypeSelect = document.getElementById('fuel_type');
  const quantityInput = document.getElementById('quantity_litres');
  const unitPriceDisplay = document.getElementById('unit_price_display');
  const pricePerLitreHidden = document.getElementById('price_per_litre');
  const totalAmountDisplay = document.getElementById('total_amount_display');
  const totalAmountHidden = document.getElementById('total_amount');
  const stockNoticeDiv = document.getElementById('stock_notice');

  function calculateFuelPrice() {
    if (!fuelTypeSelect || !quantityInput) return;

    const selectedOption = fuelTypeSelect.options[fuelTypeSelect.selectedIndex];
    if (!selectedOption || !selectedOption.value) {
      // No fuel selected – reset displays
      if (unitPriceDisplay) unitPriceDisplay.textContent = '₹0.00';
      if (totalAmountDisplay) totalAmountDisplay.textContent = '₹0.00';
      if (pricePerLitreHidden) pricePerLitreHidden.value = '';
      if (totalAmountHidden) totalAmountHidden.value = '';
      if (stockNoticeDiv) stockNoticeDiv.style.display = 'none';
      return;
    }

    const price = parseFloat(selectedOption.getAttribute('data-price')) || 0;
    const stock = parseFloat(selectedOption.getAttribute('data-stock')) || 0;
    const quantity = parseFloat(quantityInput.value) || 0;
    const total = price * quantity;

    // Update displays
    if (unitPriceDisplay) unitPriceDisplay.textContent = '₹' + price.toFixed(2);
    if (pricePerLitreHidden) pricePerLitreHidden.value = price.toFixed(2);
    if (totalAmountDisplay) totalAmountDisplay.textContent = '₹' + total.toFixed(2);
    if (totalAmountHidden) totalAmountHidden.value = total.toFixed(2);

    // Stock warnings
    if (stockNoticeDiv) {
      if (quantity > stock && stock > 0) {
        stockNoticeDiv.textContent = 'Requested quantity (' + quantity + 'L) exceeds available stock (' + stock + 'L). Your order may be partially fulfilled or delayed.';
        stockNoticeDiv.className = 'stock-notice danger';
        stockNoticeDiv.style.display = 'block';
      } else if (quantity > 0 && stock > 0 && quantity >= stock * 0.8) {
        stockNoticeDiv.textContent = 'Low stock alert: Only ' + stock + 'L available for this fuel type.';
        stockNoticeDiv.className = 'stock-notice warning';
        stockNoticeDiv.style.display = 'block';
      } else {
        stockNoticeDiv.style.display = 'none';
      }
    }
  }

  if (fuelTypeSelect) {
    fuelTypeSelect.addEventListener('change', calculateFuelPrice);
  }

  if (quantityInput) {
    quantityInput.addEventListener('input', calculateFuelPrice);
  }

  // Initial calculation in case form is pre-filled
  calculateFuelPrice();

  /* ------------------------------------------
     5. Browser GPS Geolocation
     ------------------------------------------ */
  const detectLocationBtn = document.getElementById('detectLocationBtn');
  const latitudeInput = document.getElementById('latitude');
  const longitudeInput = document.getElementById('longitude');
  const locationStatus = document.getElementById('locationStatus');

  if (detectLocationBtn) {
    detectLocationBtn.addEventListener('click', function () {
      if (!navigator.geolocation) {
        updateLocationStatus('Geolocation is not supported by your browser.', 'error');
        return;
      }

      updateLocationStatus('Detecting your location...', 'loading');
      detectLocationBtn.disabled = true;

      navigator.geolocation.getCurrentPosition(
        function (position) {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;

          if (latitudeInput) latitudeInput.value = lat.toFixed(6);
          if (longitudeInput) longitudeInput.value = lng.toFixed(6);

          updateLocationStatus('Location detected successfully! (' + lat.toFixed(4) + ', ' + lng.toFixed(4) + ')', 'success');
          detectLocationBtn.disabled = false;
        },
        function (error) {
          let message = 'Unable to detect location.';
          switch (error.code) {
            case error.PERMISSION_DENIED:
              message = 'Location permission denied. Please allow location access and try again.';
              break;
            case error.POSITION_UNAVAILABLE:
              message = 'Location information is unavailable.';
              break;
            case error.TIMEOUT:
              message = 'Location request timed out. Please try again.';
              break;
          }
          updateLocationStatus(message, 'error');
          detectLocationBtn.disabled = false;
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000
        }
      );
    });
  }

  function updateLocationStatus(message, type) {
    if (!locationStatus) return;
    locationStatus.textContent = message;
    locationStatus.className = 'location-status ' + type;
  }

  /* ------------------------------------------
     6. Star Rating Picker
     ------------------------------------------ */
  const starRatingPicker = document.getElementById('starRatingPicker');
  const ratingValueInput = document.getElementById('ratingValue');

  if (starRatingPicker) {
    const ratingStars = starRatingPicker.querySelectorAll('.rating-star');
    let currentRating = 0;

    ratingStars.forEach(function (star) {
      // Click to set rating
      star.addEventListener('click', function () {
        currentRating = parseInt(this.getAttribute('data-value'), 10);
        if (ratingValueInput) ratingValueInput.value = currentRating;
        updateStarDisplay(currentRating);
      });

      // Hover preview
      star.addEventListener('mouseenter', function () {
        const hoverValue = parseInt(this.getAttribute('data-value'), 10);
        previewStars(hoverValue);
      });
    });

    // Mouse leave – restore to current rating
    starRatingPicker.addEventListener('mouseleave', function () {
      updateStarDisplay(currentRating);
    });

    function updateStarDisplay(rating) {
      ratingStars.forEach(function (star) {
        const value = parseInt(star.getAttribute('data-value'), 10);
        star.classList.remove('active', 'preview');
        if (value <= rating) {
          star.classList.add('active');
        }
      });
    }

    function previewStars(hoverValue) {
      ratingStars.forEach(function (star) {
        const value = parseInt(star.getAttribute('data-value'), 10);
        star.classList.remove('active', 'preview');
        if (value <= hoverValue) {
          star.classList.add('preview');
        }
      });
    }

    // Initialize if there's a pre-set value
    if (ratingValueInput && ratingValueInput.value) {
      currentRating = parseInt(ratingValueInput.value, 10) || 0;
      updateStarDisplay(currentRating);
    }
  }

  /* ------------------------------------------
     7. Demo Credential Auto-Fill
     ------------------------------------------ */
  window.fillDemoCredentials = function (role) {
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const roleInput = document.getElementById('role');

    const credentials = {
      admin: {
        email: 'admin@petrolbuddy.com',
        password: 'Admin@123',
        role: 'admin'
      },
      customer: {
        email: 'customer@petrolbuddy.com',
        password: 'Customer@123',
        role: 'customer'
      },
      delivery: {
        email: 'delivery@petrolbuddy.com',
        password: 'Delivery@123',
        role: 'delivery'
      }
    };

    const cred = credentials[role];
    if (!cred) return;

    if (emailInput) emailInput.value = cred.email;
    if (passwordInput) passwordInput.value = cred.password;
    if (roleInput) roleInput.value = cred.role;

    // Trigger input events so any form validators pick up the change
    if (emailInput) emailInput.dispatchEvent(new Event('input', { bubbles: true }));
    if (passwordInput) passwordInput.dispatchEvent(new Event('input', { bubbles: true }));
    if (roleInput) roleInput.dispatchEvent(new Event('change', { bubbles: true }));
  };

  /* ------------------------------------------
     8. Print Report
     ------------------------------------------ */
  window.printReport = function () {
    window.print();
  };

});
