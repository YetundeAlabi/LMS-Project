document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.messages');
    
    // Remove each message after 3 seconds
    messages.forEach(message => {
      setTimeout(() => {
        message.classList.add('vanish');
      }, 3000);
      setTimeout(() => {
      message.remove();
      }, 3400);
    });

    var closeButtons = document.querySelectorAll('.alert__close');
    closeButtons.forEach(button => {
    button.addEventListener('click', () => {
      button.closest('.alert').remove();
    });
  });

  });

  