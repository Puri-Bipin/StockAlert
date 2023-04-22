function submitForm() {
  const form = document.querySelector('#my-form');
  const data = {
    stock_ticker: form.elements['stock-ticker'].value,
    price_threshold: form.elements['price-threshold'].value,
    frequency: form.elements['frequency'].value,
    notification_type: form.elements['notification-type'].value,
    email: form.elements['email'].value
  };
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  };
  fetch('/submit', options)
    .then(response => response.json())
    .then(data => {
    // Display a success message to the user
    const successMessage = document.createElement('p');
    successMessage.textContent = 'Your notification has been set up.';
    form.appendChild(successMessage);
    document.getElementById('stock-ticker').value = '';
    document.getElementById('price-threshold').value = '';
    document.getElementById('frequency').value = '';
    document.getElementById('notification-type').value = '';
    document.getElementById('email').value = '';

  })
    .catch(error => {
    // Display an error message to the user
    const errorMessage = document.createElement('p');
    errorMessage.textContent = 'An error occurred. Please try again.';
    form.appendChild(errorMessage);
  });
      }