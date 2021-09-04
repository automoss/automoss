class Job extends HTMLTableRowElement
{
	constructor(obj) 
	{
		super()

		Object.assign(this, obj)
		
		this.setAttribute('job_id', obj.job_id)
		this.setAttribute('status', obj.status)

		this.tableComment = document.createElement('td')
		this.tableComment.innerHTML = this.comment;
		
		this.tableLanguage = document.createElement('td')
		this.tableLanguage.innerHTML = languages[this.language][0];

		this.tableStartDate = document.createElement('td')
		this.tableStartDate.innerHTML = new Date(this.start_date).toLocaleString();
		
		let tableStatusCell = document.createElement('td')
		this.tableStatus = document.createElement('span')
		tableStatusCell.append(this.tableStatus)
		
		this.append(this.tableComment)
		this.append(this.tableLanguage)
		this.append(this.tableStartDate)
		this.append(tableStatusCell)

		this.setStatus(this.status)
	}

	setStatus(newStatus)
	{
		this.tableStatus.innerHTML = statuses[newStatus]
		if(newStatus == completedStatus){
			this.tableComment.innerHTML = `<a href="/jobs/${this.job_id}/report/" style="text-decoration: none;">${this.comment}</a>`
		}

		this.tableStatus.className = '';
		
		let classes = ['badge'];
		switch(newStatus){
			case completedStatus:
				classes.push('bg-success')
				break;
			case processingStatus:
				classes.push('bg-info')
				break;
			case uploadingStatus:
				classes.push('bg-warning')
				break;
			
			default:
				classes.push('bg-danger')
				break;
		}

		this.tableStatus.classList.add(...classes)
	}
}

customElements.define('job-row', Job, { extends: 'tr' });