"use strict";

// document.addEventListener("DOMContentLoaded", function () {
//   document
//     .getElementById("location-dropdown")
//     .addEventListener("change", function () {
//       const selectedLocation = this.value;
//       console.log("Selected location:", selectedLocation);

//       if (selectedLocation) {
//         const xhr = new XMLHttpRequest();
//         xhr.open("POST", "/save-location/", true);
//         xhr.setRequestHeader("Content-Type", "application/json");
//         xhr.setRequestHeader(
//           "X-CSRFToken",
//           document.querySelector("[name=csrfmiddlewaretoken]").value
//         );

//         xhr.onreadystatechange = function () {
//           if (xhr.readyState === XMLHttpRequest.DONE) {
//             if (xhr.status === 200) {
//               const response = JSON.parse(xhr.responseText);
//               console.log("XHR success response:", response);
//               // Optionally refresh the page or update UI
//               window.location.reload();
//             } else {
//               console.log("XHR error response:", xhr.responseText);
//               alert("Error: " + xhr.responseText);
//             }
//           }
//         };

//         xhr.send(JSON.stringify({ location: selectedLocation }));
//       } else {
//         console.log("No location selected");
//       }
//     });

//   // Add location button logic (if needed)
//   document
//     .getElementById("add-location-btn")
//     .addEventListener("click", function () {
//       console.log("Add Location button clicked");
//       // Implement add location functionality
//     });
// });
