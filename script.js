document.addEventListener("DOMContentLoaded", () => {
  "use strict";

  // Make sure this is your EXACT Render backend URL + /predict
  const API_URL = "https://air-bnb-room-type.onrender.com/predict";

  // 1. Get all elements
  const form = document.getElementById("prediction-form");
  const submitBtn = document.getElementById("submit-btn");
  const resetBtn = document.getElementById("reset-btn");
  const errorMsg = document.getElementById("error-message");
  
  const resultSection = document.getElementById("result-section");
  const resultOutput = document.getElementById("result-output");
  const probOutput = document.getElementById("prob-output");
  const availSlider = document.getElementById("availability_365");
  const availValDisplay = document.getElementById("avail-val");

  // ==========================================
  // 2. RESET BUTTON LOGIC
  // ==========================================
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      // Clear the form
      if (form) form.reset();
      
      // Reset the slider display text
      if (availValDisplay) availValDisplay.textContent = "180";
      
      // Hide the result section and errors
      if (resultSection) resultSection.style.display = "none";
      if (errorMsg) errorMsg.textContent = "";
      
      // Scroll back to top smoothly
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ==========================================
  // 3. SLIDER LOGIC
  // ==========================================
  if (availSlider && availValDisplay) {
    availSlider.addEventListener("input", (e) => {
      availValDisplay.textContent = e.target.value;
    });
  }

  // ==========================================
  // 4. PREDICT BUTTON LOGIC
  // ==========================================
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault(); // Stop page refresh
      
      // Reset UI for loading
      errorMsg.textContent = "";
      resultSection.style.display = "none";
      submitBtn.disabled = true;
      submitBtn.textContent = "PROCESSING...";

      try {
        // Gather all data from the form
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

        // Send to backend
        const response = await fetch(API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        // Handle server errors
        if (!response.ok) {
          const errorData = await response.json().catch(() => null);
          throw new Error(errorData?.detail ? JSON.stringify(errorData.detail) : "Server error: Make sure the Python backend is running.");
        }

        // Display results
        const data = await response.json();
        
        // Account for any spelling variations in your Python output
        const predictedType = data.Prediction_room_type || data.Prediction_room_tpye || "UNKNOWN";
        resultOutput.textContent = String(predictedType).toUpperCase();
        
        if (data.Probability && Array.isArray(data.Probability)) {
          const probs = data.Probability.map(p => p.toFixed(4)).join(", ");
          probOutput.textContent = `PROBABILITY: [${probs}]`;
        } else {
          probOutput.textContent = "";
        }

        // Show the result box
        resultSection.style.display = "block";
        resultSection.scrollIntoView({ behavior: "smooth", block: "start" });

      } catch (error) {
        console.error("Prediction Error:", error);
        errorMsg.textContent = error.message;
      } finally {
        // Turn the button back on
        submitBtn.disabled = false;
        submitBtn.textContent = "PREDICT ROOM TYPE";
      }
    });
  }
});