class Job extends HTMLTableRowElement{
    constructor(job, jobCollapse) {
        super();
        Object.assign(this, job);

        this.id = `job-${this.job_id}`;
        this.setAttribute('job_id', this.job_id);
        this.setAttribute('status', this.status);
        this.style = "cursor: pointer;";

        let collapse = new bootstrap.Collapse(jobCollapse, { toggle: false });
        this.onclick = (e) => {
            if (!(e.target instanceof HTMLAnchorElement)){
                collapse.toggle();
            }
        };

        // Name
        this.tableComment = document.createElement('td');
        this.append(this.tableComment);
        this.tableComment.innerHTML = this.comment;
        
        // Language
        this.tableLanguage = document.createElement('td');
        this.append(this.tableLanguage);
        this.tableLanguage.innerHTML = SUPPORTED_LANGUAGES[this.language][0];

        // Students
        this.tableStudents = document.createElement('td');
        this.append(this.tableStudents);
        this.tableStudents.innerHTML = this.num_students;

        // Date Started
        this.tableStartDate = document.createElement('td');
        this.append(this.tableStartDate);
        this.tableStartDate.innerHTML = new Date(this.creation_date).toLocaleString();
        
        // Duration
        this.tableDuration = document.createElement('td');
        this.append(this.tableDuration);
        this.tableDuration.innerHTML = "00:00:00";

        // Status
        let tableStatusCell = document.createElement('td');
        this.append(tableStatusCell);
        this.tableStatus = document.createElement('span');
        tableStatusCell.append(this.tableStatus);
        
        this.setStatus(this.status);
        this.updateDuration();
    }

    updateDuration(){
        let completion_date = new Date();
        let creation_date = new Date(this.creation_date);
		if (isTerminalState(this.status)){
			completion_date = new Date(this.completion_date);
		}
		this.tableDuration.innerHTML = new Date(completion_date - creation_date).toLocaleTimeString('en-GB', {
			timeZone:'Etc/UTC',
			hour12: false,
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		});
    }

    setStatus(newStatus){
        this.status = newStatus;
        this.tableStatus.innerHTML = statuses[newStatus];
        if(newStatus == completedStatus){
            this.tableComment.innerHTML = `<a href="/jobs/${this.job_id}/result/" style="text-decoration: none;">${this.comment}</a>`;
        }
        this.tableStatus.className = ''; 
        
        let statusMapping = {};
        statusMapping[inQueueStatus] = 'bg-warning';
        statusMapping[uploadingStatus] = 'bg-secondary';
        statusMapping[processingStatus] = 'bg-info';
        statusMapping[parsingStatus] = 'bg-dark';
        statusMapping[completedStatus] = 'bg-success';
        statusMapping[failedStatus] = 'bg-danger';
        let classes = ['badge', statusMapping[newStatus]];

        this.tableStatus.classList.add(...classes);
    }
}
customElements.define('job-row', Job, { extends: 'tr' });