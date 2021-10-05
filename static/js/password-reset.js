(function () {
		'use strict'
		// Get registration form and elements
		let form = document.getElementById('password-reset')
		let password1 = document.getElementById('id_password1')
		let password1Invalid = document.getElementById('password_1_invalid')
		let password2 = document.getElementById('id_password2')
		let password2Invalid = document.getElementById('password_2_invalid')
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
			else if(passwordElement.value.length < 8){
				errorList.appendChild(createErrorElement("Must be at least 8 characters long"))
			}
			// Check field contains both uppercase and lowercase characters
			if(passwordElement.value.search("[a-z]") == -1 || passwordElement.value.search("[A-Z]") == -1){
				errorList.appendChild(createErrorElement("Must contain both upper and lowercase letters"))
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
				passwordElement.setCustomValidity("Invalid Password")
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
				passwordElement.setCustomValidity("Invalid Password")
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
	