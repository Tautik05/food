"use strict";

document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("location-modal");
  const btn = document.getElementById("add-location-btn");
  const span = document.getElementsByClassName("close")[0];
  const form = document.getElementById("location-form");
  const locationDropdown = document.getElementById("location-dropdown");

  // Open modal and get user location when Add Location is clicked
  btn.onclick = function () {
    modal.style.display = "block";
    getLocation();
  };

  // Close modal
  span.onclick = function () {
    modal.style.display = "none";
  };

  window.onclick = function (event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  };

  // Geolocation API
  function getLocation() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
      alert("Geolocation is not supported by this browser.");
    }
  }

  function showPosition(position) {
    document.getElementById("latitude").value = position.coords.latitude;
    document.getElementById("longitude").value = position.coords.longitude;
  }

  function showError(error) {
    switch (error.code) {
      case error.PERMISSION_DENIED:
        alert("User denied the request for Geolocation.");
        break;
      case error.POSITION_UNAVAILABLE:
        alert("Location information is unavailable.");
        break;
      case error.TIMEOUT:
        alert("The request to get user location timed out.");
        break;
      case error.UNKNOWN_ERROR:
        alert("An unknown error occurred.");
        break;
    }
  }

  // Form submission
  form.onsubmit = function (e) {
    e.preventDefault();

    // Get form data
    var formData = {
      latitude: document.getElementById("latitude").value,
      longitude: document.getElementById("longitude").value,
      address: document.getElementById("address").value,
    };

    // Make AJAX call to save the new location
    $.ajax({
      type: "POST",
      url: "/home/location/", // Update with correct URL
      data: formData,
      headers: {
        "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val(),
      },
      success: function (response) {
        console.log(response);
        alert("Location saved successfully!");
        modal.style.display = "none";
        // Optionally reload or add the location to the dropdown
        window.location.reload();
      },
      error: function (xhr, status, error) {
        console.log(xhr.responseText);
        alert("Error: " + xhr.responseText);
      },
    });
  };

  // Handle dropdown change to select location, latitude, and longitude
  locationDropdown.addEventListener("change", function () {
    const selectedOption =
      locationDropdown.options[locationDropdown.selectedIndex];
    const selectedLocation = selectedOption.value;
    const latitude = selectedOption.getAttribute("data-lat");
    const longitude = selectedOption.getAttribute("data-lon");

    if (selectedLocation && latitude && longitude) {
      console.log("Selected Location:", selectedLocation);
      console.log("Latitude:", latitude);
      console.log("Longitude:", longitude);

      // Update the visible text of the dropdown
      locationDropdown.options[locationDropdown.selectedIndex].text =
        selectedLocation;

      // Send location data (address, latitude, longitude) to the backend
      const xhr = new XMLHttpRequest();
      xhr.open("POST", "/save-location/", true);
      xhr.setRequestHeader("Content-Type", "application/json");
      xhr.setRequestHeader(
        "X-CSRFToken",
        document.querySelector("[name=csrfmiddlewaretoken]").value
      );

      xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
          if (xhr.status === 200) {
            console.log("Location saved successfully");
            // No need to reload the page
          } else {
            alert("Error saving location");
          }
        }
      };

      xhr.send(
        JSON.stringify({
          location: selectedLocation,
          latitude: latitude,
          longitude: longitude,
        })
      );
    } else {
      console.log("No location, latitude, or longitude selected");
    }
  });
});
