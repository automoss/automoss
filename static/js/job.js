class Job extends HTMLTableRowElement{
    constructor(obj) {
        super()
        Object.assign(this, obj)

        this.setAttribute('job_id', obj.job_id)
        this.setAttribute('status', obj.status)
        this.setAttribute('data-bs-toggle', 'collapse');
        this.setAttribute('data-bs-target', `#job-accordion-${obj.job_id}`);
        this.style="cursor: pointer;";

        // Comment
        this.tableComment = document.createElement('td')
        this.tableComment.innerHTML = this.comment;
        
        // Language
        this.tableLanguage = document.createElement('td')
        this.tableLanguage.innerHTML = SUPPORTED_LANGUAGES[this.language][0];

        // Start Date
        this.tableStartDate = document.createElement('td')
        this.tableStartDate.innerHTML = new Date(this.creation_date).toLocaleString();
        
        // Status
        let tableStatusCell = document.createElement('td')
        this.tableStatus = document.createElement('span')
        tableStatusCell.append(this.tableStatus)
        
        this.append(this.tableComment)
        this.append(this.tableLanguage)
        this.append(this.tableStartDate)
        this.append(tableStatusCell)

        this.setStatus(this.status)
    }

    setStatus(newStatus){
        this.tableStatus.innerHTML = statuses[newStatus]
        if(newStatus == completedStatus){
            this.tableComment.innerHTML = `<a href="/jobs/${this.job_id}/result/" style="text-decoration: none;">${this.comment}</a>`
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

        this.tableStatus.classList.add(...classes)
    }
}
customElements.define('job-row', Job, { extends: 'tr' });