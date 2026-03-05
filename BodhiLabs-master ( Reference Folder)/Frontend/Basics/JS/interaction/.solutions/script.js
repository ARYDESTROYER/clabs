// Function to return the current dimensions of the browser window
function getWindowDimensions() {
  return {
    width: window.innerWidth,
    height: window.innerHeight
  };
}

// Function to update the displayed dimensions
function updateDimensionsDisplay() {
  const dimensions = getWindowDimensions();
  document.getElementById('width').textContent = dimensions.width + 'px';
  document.getElementById('height').textContent = dimensions.height + 'px';
}

// Initial display of dimensions when the page loads
updateDimensionsDisplay();

// Update dimensions every time the window is resized
window.addEventListener('resize', updateDimensionsDisplay);
