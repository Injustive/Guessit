let card = document.querySelector('.card-f');
let chart = document.getElementById('chart_rotate_icon');

chart.addEventListener( 'click', function() {
  card.classList.toggle('is-flipped');
});
