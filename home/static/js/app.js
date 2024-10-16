"use strict";
document.addEventListener("DOMContentLoaded", function () {
  let userLocation, allRestaurants;

  try {
    userLocation = JSON.parse(window.userLocationJSON || "null");
    allRestaurants = JSON.parse(window.allRestaurantsJSON || "[]");
  } catch (error) {
    console.error("Error parsing JSON:", error);
    userLocation = null;
    allRestaurants = [];
  }

  console.log("User Location:", userLocation);
  console.log("All Restaurants:", allRestaurants);

  if (userLocation && userLocation.latitude && userLocation.longitude) {
    console.log(
      "Fetching nearby restaurants for:",
      userLocation.latitude,
      userLocation.longitude
    );
    fetchNearbyRestaurants(userLocation.latitude, userLocation.longitude);
  } else {
    console.log("No valid user location found");
  }

  function fetchNearbyRestaurants(lat, lon) {
    const overpassUrl = "https://overpass-api.de/api/interpreter";
    const query = `
          [out:json];
          (
            node["amenity"="restaurant"](around:15000,${lat},${lon});
            way["amenity"="restaurant"](around:15000,${lat},${lon});
            relation["amenity"="restaurant"](around:15000,${lat},${lon});
          );
          out center;
      `;

    console.log("Sending query to Overpass API:", query);

    fetch(overpassUrl, {
      method: "POST",
      body: query,
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Received data from Overpass API:", data);
        const nearbyRestaurants = data.elements.map((element) => ({
          name: element.tags.name,
          lat: element.lat || element.center.lat,
          lon: element.lon || element.center.lon,
        }));
        console.log("Nearby restaurants found:", nearbyRestaurants);
        displayRestaurants(nearbyRestaurants);
      })
      .catch((error) =>
        console.error("Error fetching nearby restaurants:", error)
      );
  }

  function displayRestaurants(nearbyRestaurants) {
    const container = document.getElementById("restaurant-recommendations");
    let html =
      '<h2>Recommended Restaurants Near You</h2><div class="restaurant-grid">';
    let matchCount = 0;

    nearbyRestaurants.forEach((nearby) => {
      console.log("Checking nearby restaurant:", nearby);
      const match = allRestaurants.find((r) => {
        if (!r || !r.restaurant_name) {
          console.warn("Invalid restaurant object:", r);
          return false;
        }
        const nameMatch =
          r.restaurant_name.toLowerCase() === (nearby.name || "").toLowerCase();
        const locationMatch =
          r.latitude &&
          r.longitude &&
          Math.abs(r.latitude - nearby.lat) < 0.0001 &&
          Math.abs(r.longitude - nearby.lon) < 0.0001;
        console.log(
          `Comparing with ${r.restaurant_name}:`,
          `Name match: ${nameMatch}`,
          `Location match: ${locationMatch}`
        );
        return nameMatch || locationMatch;
      });

      if (match) {
        console.log("Match found:", match);
        matchCount++;
        html += `
            <div class="restaurant-card">
                <img src="${
                  match.restaurant_image
                    ? "/media/" + match.restaurant_image
                    : "/static/img/default-restaurant.jpg"
                }" 
                     alt="${match.restaurant_name}"
                     onerror="this.onerror=null; this.src='/static/img/default-restaurant.jpg';">
                <h3>${match.restaurant_name}</h3>
                <p>${match.restaurant_location}</p>
            </div>
        `;
      }
    });

    html += "</div>";
    container.innerHTML = html;

    console.log(`Total matches found: ${matchCount}`);
    if (matchCount === 0) {
      console.log("No matching restaurants found in the database");
      container.innerHTML +=
        "<p>No matching restaurants found in our database within 15km of your location.</p>";
    }
  }
});
