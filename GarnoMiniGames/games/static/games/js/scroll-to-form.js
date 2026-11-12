'use strict';

document.addEventListener('DOMContentLoaded', function () {
  const formElement = document.getElementById('rejoindre-form');
  if (formElement && formElement.dataset.hasError === 'true') {
    setTimeout(function () {
      formElement.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      });
    }, 100);
  }
});
