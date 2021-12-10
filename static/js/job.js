class Job extends HTMLTableRowElement{
	constructor(job, jobInfo){
		super();
		Object.assign(this, job);

		this.jobInfo = jobInfo;
		this.id = `job-${this.job_id}`;
		this.setAttribute('job_id', this.job_id);
		this.setAttribute('status', this.status);
		this.style = "cursor: pointer;";

		this.collapse = new bootstrap.Collapse(jobInfo.firstChild, { toggle: false });
		this.onclick = (e) => {
			if (!(e.target instanceof HTMLAnchorElement)){ // Prevent collapsible region from toggling when job name is clicked.
				this.collapse.toggle();
			}
		};

		// Name
		this.jobName = document.createElement('td');
		this.append(this.jobName);
		this.jobName.innerHTML = this.comment;
		
		// Language
		this.jobLanguage = document.createElement('td');
		this.append(this.jobLanguage);
		this.jobLanguage.innerHTML = SUPPORTED_LANGUAGES[this.language][0];

		// Students
		this.jobNumStudents = document.createElement('td');
		this.append(this.jobNumStudents);
		this.jobNumStudents.innerHTML = this.num_students;

		// Date Started
		this.jobCreationDate = document.createElement('td');
		this.append(this.jobCreationDate);
		this.jobCreationDate.innerHTML = new Date(this.creation_date).toLocaleString();
		
		// Duration
		this.jobDuration = document.createElement('td');
		this.append(this.jobDuration);
		this.jobDuration.innerHTML = "00:00:00";

		// Status
		let jobStatusCell = document.createElement('td');
		this.append(jobStatusCell);
		this.jobStatus = document.createElement('span');
		jobStatusCell.append(this.jobStatus);
		
		this.setStatus(this.status);
		this.updateDuration();
	}

	showInfo(isImmediate=false){
		if (isImmediate){
			this.jobInfo.firstChild.classList.add("show");	
		}else{
			this.collapse.show();
		}
	}

	hideInfo(isImmediate=false){
		if (isImmediate){
			this.jobInfo.firstChild.classList.remove("show");	
		}else{
			this.collapse.hide();
		}	
	}

	/**
	 * Update the duration of the job depending on whether the job is in a terminal state or not. If in a terminal
	 * state, the completion date will be set to the completion date's date and time. Else, the current date and
	 * time will be used, and subtracted from the creation date.
	 * 
	 * This should be updated constantly every second, and reflected in the table.
	 */
	updateDuration(){
		let completion_date = new Date();
		let creation_date = new Date(this.creation_date);
		if (isTerminalState(this.status)){
			completion_date = new Date(this.completion_date);
		}

		// Display in hh:mm:ss format
		let total_seconds = new Date(completion_date - creation_date) / 1000;

		let hours = Math.floor(total_seconds / 3600);
		total_seconds %= 3600;
		let minutes = Math.floor(total_seconds / 60);
		let seconds = Math.floor(total_seconds % 60);

		minutes = String(minutes).padStart(2, "0");
		hours = String(hours).padStart(2, "0");
		seconds = String(seconds).padStart(2, "0");

		this.jobDuration.innerHTML = hours + ":" + minutes + ":" + seconds;
	}

	/**
	 * Set the status of a job.
	 */
	setStatus(newStatus){
		this.status = newStatus;

		this.jobStatus.innerHTML = statuses[newStatus];
		if(newStatus == completedStatus){
			this.jobName.innerHTML = `<a href="/jobs/${this.job_id}/result/" style="text-decoration: none;">${this.comment}</a>`;
		}
		this.jobStatus.className = ''; 

		let statusMapping = {};
        statusMapping[inQueueStatus] = 'bg-warning';
        statusMapping[uploadingStatus] = 'bg-secondary';
        statusMapping[processingStatus] = 'bg-info';
        statusMapping[parsingStatus] = 'bg-dark';
        statusMapping[completedStatus] = 'bg-success';
        statusMapping[failedStatus] = 'bg-danger';

        let classes = ['badge', statusMapping[newStatus]];
        this.jobStatus.classList.add(...classes);
	}
}
customElements.define('job-row', Job, { extends: 'tr' });