(function () {
    'use strict'
    // Get registration form and elements
    let form = document.getElementById('register')
    let courseCode = document.getElementById('id_course_code')
    let courseInvalid = document.getElementById('course_invalid')
    let email = document.getElementById('id_email')
    let emailInvalid = document.getElementById('email_invalid')
    let mossID = document.getElementById('id_moss_id')
    let mossInvalid = document.getElementById('moss_id_invalid')
    let password1 = document.getElementById('id_password1')
    let password1Invalid = document.getElementById('password_1_invalid')
    let password2 = document.getElementById('id_password2')
    let password2Invalid = document.getElementById('password_2_invalid')
    let formList = document.querySelectorAll("form .form-control")

    // Reset element to valid state
    function resetValidity(element, invalidDiv){
      element.setCustomValidity("")
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

    // Performs validation on course code and generates associated errors
    function performCourseCodeValidation(courseElement){
      form.classList.add('was-validated')
      // Reset Validity
      courseElement.setCustomValidity("")
      // Validation Checks
      let errorList = document.createElement("ul")
      if(!courseElement.checkValidity()){
        errorList.appendChild(createErrorElement("Course Code Missing"))
      }
      // Set validity
      if(!isEmpty(errorList)){
        courseElement.setCustomValidity("Invalid Course Code")
        courseInvalid.innerHTML = ""
      }
      else{
        resetValidity(courseElement, courseInvalid)
      }
      return errorList
    }
    
    // Check course code validity on focus out and display errors
    courseCode.addEventListener('focusout', function(){
      let errors = performCourseCodeValidation(this)
      courseInvalid.appendChild(errors)
    })

    // Check course code validity on input
    courseCode.addEventListener('input', function(){
      performCourseCodeValidation(this)
    })

    // Email validation check (taken from: https://stackoverflow.com/questions/46155/how-to-validate-an-email-address-in-javascript)
    function validateEmail(email) {
      const emailFormat = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      return emailFormat.test(String(email).toLowerCase());
    }
    
    // Performs validation on email and generates associated errors
    function performEmailValidation(emailElement){
      form.classList.add('was-validated')
      // Reset Validity
      emailElement.setCustomValidity("")
      // Validation Checks
      let errorList = document.createElement("ul")
      if(emailElement.value === ""){
        errorList.appendChild(createErrorElement("Email Missing"))
      }
      else if(!emailElement.checkValidity() || !validateEmail(emailElement.value)){
        errorList.appendChild(createErrorElement("Email is invalid (should be of the form name@domain.xyz)"))
      }
      // Set validity
      if(!isEmpty(errorList)){
        emailElement.setCustomValidity("Invalid Email")
        emailInvalid.innerHTML = ""
      }
      else{
        resetValidity(emailElement, emailInvalid)
      }
      return errorList
    }

    // Check email validity on focus out and display errors
    email.addEventListener('focusout', function(){
      let errors = performEmailValidation(this)
      emailInvalid.appendChild(errors)
    })

    // Check email validity on input
    email.addEventListener('input', function(){
      performEmailValidation(this)
    })

    // Performs validation on MOSS ID and generates associated errors
    function performMOSSIDValidation(mossElement){
      form.classList.add('was-validated')
      // Reset Validity
      mossElement.setCustomValidity("")
      // Validation Checks
      let errorList = document.createElement("ul")
      if(!mossElement.checkValidity()){
        errorList.appendChild(createErrorElement("MOSS ID Missing"))
      }
      // Check field contains only digits
      if(!/^\d*$/.test(mossElement.value)){
        errorList.appendChild(createErrorElement("Must contain only digits"))
      }
      // Set validity
      if(!isEmpty(errorList)){
        mossElement.setCustomValidity("Invalid MOSS ID")
        mossInvalid.innerHTML = ""
      }
      else{
        resetValidity(mossElement, mossInvalid)
      }
      return errorList
    }

    // Check MOSS ID validity on input
    mossID.addEventListener('input', function(){
      performMOSSIDValidation(this)
    })

    // Check MOSS ID validity on out focus and display errors
    mossID.addEventListener('focusout', function(){
      let errors = performMOSSIDValidation(this)
      mossInvalid.appendChild(errors)
    })

    // Performs validation on 1st password input and generates associated errors
    function performPassword1Validation(passwordElement){
      form.classList.add('was-validated')
      // Reset Validity
      passwordElement.setCustomValidity("")
      // Validation Checks
      let errorList = document.createElement("ul")
      if(!passwordElement.checkValidity()){
        errorList.appendChild(createErrorElement("Password Missing"))
      }
      // Check field is long enough
      if(passwordElement.value.length < 8){
        errorList.appendChild(createErrorElement("Must be at least 8 characters long"))
      }
      // Check field contains a lowercase character
      if(passwordElement.value.search("[a-z]") == -1){
        errorList.appendChild(createErrorElement("Must contain a lowercase character"))
      }
      // Check field contains an uppercase character
      if(passwordElement.value.search("[A-Z]") == -1){
        errorList.appendChild(createErrorElement("Must contain an uppercase character"))
      }
      // Check field contains a digit
      if(passwordElement.value.search("[0-9]") == -1){
        errorList.appendChild(createErrorElement("Must contain a digit"))
      }
      // Check field contains a special character
      if(passwordElement.value.search("[^a-zA-Z0-9]") == -1){
        errorList.appendChild(createErrorElement("Must contain a special character"))
      }
      // Set validity
      if(!isEmpty(errorList)){
        passwordElement.setCustomValidity("Invalid MOSS ID")
        password1Invalid.innerHTML = ""
      }
      else{
        resetValidity(passwordElement, password1Invalid)
      }
      return errorList
    }

    // Validate password on input
    password1.addEventListener('input', function(){
      performPassword1Validation(this)
    })

    // Validate password on focus out and display errors
    password1.addEventListener('focusout', function(){
      let errors = performPassword1Validation(this)
      password1Invalid.appendChild(errors)
      let event = new Event('input', {
        bubbles: true,
        cancelable: true,
      })
      password2.dispatchEvent(event)
    })

    // Perform validation on 2nd password and generate errors
    function performPassword2Validation(passwordElement){
      form.classList.add('was-validated')
      // Reset Validity
      passwordElement.setCustomValidity("")
      // Validation Checks
      let errorList = document.createElement("ul")
      if(!passwordElement.checkValidity()){
        errorList.appendChild(createErrorElement("Password Missing"))
      }
      if(passwordElement.value !== password1.value){
        errorList.appendChild(createErrorElement("Passwords don't match"))
      }
      // Set validity
      if(!isEmpty(errorList)){
        passwordElement.setCustomValidity("Invalid MOSS ID")
        password2Invalid.innerHTML = ""
      }
      else{
        resetValidity(passwordElement, password2Invalid)
      }
      return errorList
    }

    // Validate password2 on input
    password2.addEventListener('input', function(){
      performPassword2Validation(this)
    })

    // Validate password2 on focus out and display errors
    password2.addEventListener('focusout', function(){
      let errors = performPassword2Validation(this)
      password2Invalid.appendChild(errors)
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
  