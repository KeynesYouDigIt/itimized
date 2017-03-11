window.onload = function() {
  console.log('JS is in');

  menu.addEventListener('click', function(e) {
      sidebar.classList.toggle('open');
      //all this does is set id drawer to have the class open
      //css can take it from there
  e.stopPropagation();
  });

};
