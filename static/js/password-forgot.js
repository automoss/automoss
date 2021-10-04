(function () {
		'use strict'
		// Get registration form and elements
		let form = document.getElementById('forgotten-password')
		let courseCode = document.getElementById('id_course_code')
		let courseInvalid = document.getElementById('course_code_invalid')
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
	