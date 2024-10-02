"use strict";

let slideIndex = 0;

function moveSlide(n) {
  const slides = document.querySelector(".slider-images");
  const totalSlides = slides.children.length;
  slideIndex = (slideIndex + n + totalSlides) % totalSlides;
  const newTransform = `translateX(-${(slideIndex * 100) / totalSlides}%)`;
  slides.style.transform = newTransform;
}

// Auto slide every 5 seconds
setInterval(() => {
  moveSlide(1);
}, 5000);
