document.addEventListener("DOMContentLoaded", () => {
  "use strict";

const API_URL = "https://air-bnb-room-type.onrender.com/predict";

  const form = document.getElementById("prediction-form");
  const submitBtn = document.getElementById("submit-btn");
  const errorMsg = document.getElementById("error-message");git 
  
  const resultSection = document.getElementById("result-section");
  const resultOutput = document.getElementById("result-output");
  const probOutput = document.getElementById("prob-output");
  const availSlider = document.getElementById("availability_365");
  const availValDisplay = document.getElementById("avail-val");

  // 1. Real-time Slider
  if (availSlider && availValDisplay) {
    availSlider.addEventListener("input", (e) => {
      availValDisplay.textContent = e.target.value;
    });
  }

  // 2. Prevent negative typing in number boxes
  const numberInputs = document.querySelectorAll('input[type="number"]');
  numberInputs.forEach(input => {
    input.addEventListener('keypress', function(e) {
      const min = this.hasAttribute('min') ? parseFloat(this.getAttribute('min')) : null;
      if (min !== null && min >= 0 && e.key === '-') {
        e.preventDefault(); 
      }
    });

    input.addEventListener('blur', function() {
      if (this.value !== "") {
        let val = parseFloat(this.value);
        const min = this.hasAttribute('min') ? parseFloat(this.getAttribute('min')) : null;
        const max = this.hasAttribute('max') ? parseFloat(this.getAttribute('max')) : null;
        if (min !== null && val < min) this.value = min;
        if (max !== null && val > max) this.value = max;
      }
    });
  });

  // 3. Form Submission
  form.addEventListener("submit", async (e) => {
    e.preventDefault(); // STOP THE PAGE REFRESH
    
    errorMsg.textContent = "";
    resultSection.style.display = "none";
    submitBtn.disabled = true;
    submitBtn.textContent = "PROCESSING...";

    try {
      const payload = {
        neighbourhood_group: document.querySelector('input[name="neighbourhood_group"]:checked').value,
        neighbourhood: document.getElementById("neighbourhood").value.trim(),
        latitude: parseFloat(document.getElementById("latitude").value),
        longitude: parseFloat(document.getElementById("longitude").value),
        price: parseFloat(document.getElementById("price").value),
        minimum_nights: parseInt(document.getElementById("minimum_nights").value, 10),
        number_of_reviews: parseInt(document.getElementById("number_of_reviews").value, 10),
        reviews_per_month: parseFloat(document.getElementById("reviews_per_month").value) || 0.0,
        calculated_host_listings_count: parseInt(document.getElementById("calculated_host_listings_count").value, 10),
        availability_365: parseInt(document.getElementById("availability_365").value, 10)
      };

      for (const [key, value] of Object.entries(payload)) {
        if (value === "" || Number.isNaN(value)) {
          throw new Error("Please ensure all fields are filled out with valid numbers.");
        }
      }

      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail ? JSON.stringify(errorData.detail) : "Server prediction failed. Make sure FastAPI is running!");
      }

      const data = await response.json();

      const predictedType = data.Prediction_room_tpye || data.Prediction_room_type || "UNKNOWN";
      resultOutput.textContent = String(predictedType).toUpperCase();
      
      if (data.Probability && Array.isArray(data.Probability)) {
        const probs = data.Probability.map(p => p.toFixed(4)).join(", ");
        probOutput.textContent = `PROBABILITY: [${probs}]`;
      } else {
        probOutput.textContent = "";
      }

      resultSection.style.display = "block";
      resultSection.scrollIntoView({ behavior: "smooth", block: "start" });

    } catch (error) {
      console.error("Prediction Error:", error);
      errorMsg.textContent = error.message;
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "PREDICT ROOM TYPE";
    }
  });
});