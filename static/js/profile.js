(function () {
		'use strict'
		// Password change elements
		let passwordChangeForm = document.getElementById('password-change-form')
		let oldPassword = document.getElementById('id_old_password')
		let oldPasswordInvalid = document.getElementById('old_password_invalid')
		let password1 = document.getElementById('id_new_password1')
		let password1Invalid = document.getElementById('new_password1_invalid')
		let password2 = document.getElementById('id_new_password2')
		let password2Invalid = document.getElementById('new_password2_invalid')
		let passwordFormList = document.querySelectorAll("form#password-change-form .form-control")

		// Email list elements
		let email = document.getElementById('id_email_input')
		let emailInvalid = document.getElementById('id_email_invalid')
		let emailAddButton = document.getElementById('id_add_email')
		let emailAddForm = document.getElementById('id_email_add_form')
		// let emailUpdateButton = document.getElementById('id_update_emails')
		let emailForm = document.getElementById('id_email_add_form')
		let emailList = document.getElementById('id_email_list')
		let emailRemoveButtons = document.querySelectorAll('button.remove-email')
		let emailFeedback = document.getElementById('id_email_list_invalid')
		let emailsChanged = false

		function clearEmailList(){
			// Removes all emails from the email list
			emailList.innerHTML = ""
		}

		function createEmailComponent(emailAddress, verified=false){
			// Email and icon
			let emailImg = document.createElement('img')
			emailImg.src = "/static/img/email-icon.svg"
			emailImg.classList.add("mx-2")
			let emailSpan = document.createElement('span')
			emailSpan.classList.add('email-span', 'ms-1')
			emailSpan.innerText = emailAddress
			let emailDiv = document.createElement('div')
			emailDiv.appendChild(emailImg)
			emailDiv.appendChild(emailSpan)

			// Badge and close button
			let badge = document.createElement('span')
			badge.classList.add("badge", "badge-pill", verified ? "bg-success" : "bg-danger")
			badge.innerText=verified ? "Verified" : "Unverified"
			let closeButton = document.createElement('button')
			closeButton.classList.add("btn-close", "ms-3", "remove-email")
			closeButton.addEventListener('click', function(event){
				closeButton.parentElement.parentElement.remove()
				emailsChanged = true
				// emailUpdateButton.disabled = false
			})

			// Add to div
			let badgeDiv = document.createElement('div')
			badgeDiv.classList.add("d-flex", "flex-row", "justify-content-between", "align-items-center")
			badgeDiv.appendChild(badge)
			badgeDiv.appendChild(closeButton)

			// Surrounding div
			let outerDiv = document.createElement('div')
			outerDiv.classList.add("d-flex", "p-2", "flex-row", "justify-content-between", "mb-2", "bg-light", "border", "border-dark", "border-2", "rounded-3")
			outerDiv.appendChild(emailDiv)
			outerDiv.appendChild(badgeDiv)

			// Add to list
			emailList.appendChild(outerDiv)
		}

		function getEmails(){
			// Return list of emails
			return Array.from(emailList.querySelectorAll('span.email-span'), span => span.innerText)
		}

		function addEmail(){
			// Check email form is valid
			if (!emailForm.checkValidity()) {
				// Prevent adding to list
				emailForm.classList.add('was-validated')
				let focusEvent = new Event('focusout', {
					bubbles: true,
					cancelable: true,
				})
				email.dispatchEvent(focusEvent)
			}
			else{
				// Add to list of emails
				createEmailComponent(email.value)
				email.value = ""
				emailsChanged = true
				// emailUpdateButton.disabled = false
			}
		}

		// Trigger email add on form submit
		emailAddForm.addEventListener('submit', function(event){
			// Prevent submission
			event.preventDefault();
			event.stopPropagation();
			// Add email
			addEmail()
		})

		// Add email to list when Add Email clicked
		emailAddButton.addEventListener('click', function(event){
			addEmail();
			updateMailingList();
		})

		// POST data when Update List clicked
		// emailUpdateButton.addEventListener('click',
		async function updateMailingList(){

			// List has changed/been modified
			if(emailsChanged){
				let emails = getEmails()
				let data = new FormData()
				data.append("emails", emails)
				data.append("form", "mail-list-change")
				data.append("csrfmiddlewaretoken", document.querySelector('input[name="csrfmiddlewaretoken"]').getAttribute('value'))
				// Post email data
				let result = await fetch("", {
					method: 'POST',
					credentials: 'same-origin',
					body: data
				})
				// Clear email list
				clearEmailList()
				let jsonEmails = await result.json()
				// Add new emails
				for(let email of jsonEmails["emails"]){
					createEmailComponent(...email)
				}
				// Reset changed to false
				emailsChanged = false
				// emailUpdateButton.disabled = true
				// Add status to status div
				// emailFeedback.innerText = "Email list updated!"
				// emailFeedback.classList.remove("text-danger")
				// emailFeedback.classList.add("text-success")
				// // Remove feedback after 2 seconds
				// setTimeout(function(){
				// 	emailFeedback.innerText = ""
				// 	emailFeedback.classList.add("text-danger")
				// 	emailFeedback.classList.remove("text-success")
				// }, 2000)
			}
			else{
				// emailFeedback.innerText = "The email list hasn't changed!"
			}
		}

		// Remove email element on click
		emailRemoveButtons.forEach(function(button){
			button.addEventListener('click', function(event){
				button.parentElement.parentElement.remove()
				emailsChanged = true
				// emailUpdateButton.disabled = false
				updateMailingList();
			})
		})


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

		// Email validation check (taken from: https://stackoverflow.com/questions/46155/how-to-validate-an-email-address-in-javascript)
		function validateEmail(email) {
			const emailFormat = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
			return emailFormat.test(String(email).toLowerCase());
		}
		
		// Performs validation on email and generates associated errors
		function performEmailValidation(emailElement){
			emailForm.classList.add('was-validated')
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
			else if(getEmails().indexOf(emailElement.value) !== -1){
				errorList.appendChild(createErrorElement("Email already in list"))
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
		
		// Performs validation on old password input and generates associated errors
		function performOldPasswordValidation(passwordElement){
			passwordChangeForm.classList.add('was-validated')
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
				oldPasswordInvalid.innerHTML = ""
			}
			else{
				resetValidity(passwordElement, oldPasswordInvalid)
			}
			return errorList
		}

		// Validate old password on input
		oldPassword.addEventListener('input', function(){
			performOldPasswordValidation(this)
		})

		// Validate old password on focus out and display errors
		oldPassword.addEventListener('focusout', function(){
			let errors = performOldPasswordValidation(this)
			oldPasswordInvalid.appendChild(errors)
		})

		// Performs validation on 1st password input and generates associated errors
		function performPassword1Validation(passwordElement){
			passwordChangeForm.classList.add('was-validated')
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
			passwordChangeForm.classList.add('was-validated')
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
		passwordChangeForm.addEventListener('submit', function (event) {
				if (!this.checkValidity()) {
					// Prevent submission
					event.preventDefault()
					event.stopPropagation()
					this.classList.add('was-validated')
					passwordFormList.forEach(function(element){
							let event = new Event('focusout', {
								bubbles: true,
								cancelable: true,
							})
						element.dispatchEvent(event)
					})
				}
				
		}, false)

	})()
	