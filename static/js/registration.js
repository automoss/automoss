(function () {
    'use strict'
    // Get registration form
    let form = document.getElementById('register')
    let password1 = document.getElementById('id_password1')
    let password2 = document.getElementById('id_password2')
  
    // Prevent submission if not valid
    form.addEventListener('submit', function (event) {
        let passwordMatch = password1.value === password2.value
        if (!form.checkValidity() || !passwordMatch) {
          event.preventDefault()
          event.stopPropagation()
        }
        form.classList.add('was-validated')
      }, false)
      

    password2.addEventListener('input', function(event){
      if(password1.value === password2.value){
        console.log("valid")
      }
      
    })

  })()
  