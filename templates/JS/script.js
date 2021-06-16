$(function() {
  $(".accordion").click(function() {
    $(this).toggleClass("close").next().slideToggle();
  });
});