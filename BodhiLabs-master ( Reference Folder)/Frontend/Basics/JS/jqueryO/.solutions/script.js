$(document).ready(function () {
  // Open lightbox
  $(".gallery-item").on("click", function () {
    const imgSrc = $(this).data("image");
    $(".lightbox-image").attr("src", imgSrc);
    $(".lightbox").fadeIn();
  });

  // Close lightbox
  $(".close").on("click", function () {
    $(".lightbox").fadeOut();
  });

  // Close lightbox on outside click
  $(".lightbox").on("click", function (e) {
    if ($(e.target).is(".lightbox, .close")) {
      $(".lightbox").fadeOut();
    }
  });
});
