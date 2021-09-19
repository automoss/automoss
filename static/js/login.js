(function () {
    'use strict'
    // Get registration form and elements
    let form = document.getElementById('login')
    let username = document.getElementById('id_username')
    let usernameInvalid = document.getElementById('username_invalid')
    let password = document.getElementById('id_password')
    let passwordInvalid = document.getElementById('password_invalid')
    let formList = document.querySelectorAll("form .form-control")

    // Reset element to valid state
    function resetValidity(element, invalidDiv){
      element.setCustomValidity("")
      element.classList.remove("is-invalid")
      invalidDiv.innerHTML = ""
    }

    // Check if element is empty
    function isEmpty(element){
      return element.innerHTML.trim() === ""
    }

    // Return new list element with error message
    function createErrorElement(errorMessage){
      let li = document.createElement("li")
      li.appendChild(document.createTextNode(errorMessage))
      return li
    }

    // Performs validation on username and generates associated errors
    function performUsernameValidation(usernameElement){
      form.classList.add('was-validated')
      // Reset Validity
      usernameElement.setCustomValidity("")
      // Validation Checks
      let errorList = document.createElement("ul")
      if(!usernameElement.checkValidity()){
        errorList.appendChild(createErrorElement("Course Code Missing"))
      }
      // Set validity
      if(!isEmpty(errorList)){
        usernameElement.setCustomValidity("Invalid Course Code")
        usernameInvalid.innerHTML = ""
      }
      else{
        resetValidity(usernameElement, usernameInvalid)
      }
      return errorList
    }
    
    // Check username validity on focus out and display errors
    username.addEventListener('focusout', function(){
      let errors = performUsernameValidation(this)
      usernameInvalid.appendChild(errors)
    })

    // Check username validity on input
    username.addEventListener('input', function(){
      performUsernameValidation(this)
    })
    
    // Performs validation on password and generates associated errors
    function performPasswordValidation(passwordElement){
      form.classList.add('was-validated')
      // Reset Validity
      passwordElement.setCustomValidity("")
      // Validation Checks
      let errorList = document.createElement("ul")
      if(!passwordElement.checkValidity()){
        errorList.appendChild(createErrorElement("Password Missing"))
      }
      // Set validity
      if(!isEmpty(errorList)){
        passwordElement.setCustomValidity("Invalid Password")
        passwordInvalid.innerHTML = ""
      }
      else{
        resetValidity(passwordElement, passwordInvalid)
      }
      return errorList
    }

    // Check password validity on focus out and display errors
    password.addEventListener('focusout', function(){
      let errors = performPasswordValidation(this)
      passwordInvalid.appendChild(errors)
    })

    // Check password validity on input
    password.addEventListener('input', function(){
      performPasswordValidation(this)
    })


    // Prevent submission if not valid
    form.addEventListener('submit', function (event) {
        if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()
        }
        form.classList.add('was-validated')
        formList.forEach(function(element){
            let event = new Event('focusout', {
              bubbles: true,
              cancelable: true,
            })
          element.dispatchEvent(event)
        })
      }, false)

  })()
  