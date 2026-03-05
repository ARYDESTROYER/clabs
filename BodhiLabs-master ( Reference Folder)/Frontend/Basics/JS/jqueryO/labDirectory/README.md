# Lightbox Gallery

## Overview

This project requires you to implement a lightbox gallery functionality using jQuery. When users click on gallery items, a lightbox opens displaying the enlarged image. Users can close the lightbox either by clicking a close button or clicking outside the image area.

## Problem Description

You need to complete the implementation of three event handlers in `script.js`:

1. Opening the lightbox when a gallery item is clicked
2. Closing the lightbox when the close button is clicked
3. Closing the lightbox when clicking outside the image area

## Requirements

### 1. Opening the Lightbox

When a gallery item is clicked:

- Get the `data-image` attribute value from the clicked `.gallery-item`
- Set this value as the `src` attribute of `.lightbox-image`
- Fade in the `.lightbox` element

### 2. Closing via Close Button

When the close button is clicked:

- Fade out the `.lightbox` element

### 3. Closing via Outside Click

When clicking outside the image area:

- Check if the clicked element (e.target) is either the lightbox background or close button
- If true, fade out the `.lightbox` element
