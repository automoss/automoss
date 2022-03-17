function onJobShow(job){
}

function onJobHide(job){
	job.hideInfo(true);
}

// Setup the jobs table for searching.
let jobsTable = document.getElementById('job-table');
let jobsSearchBar = document.getElementById('job-search-bar');
setupTableSearch(jobsTable, jobsSearchBar, onJobShow, onJobHide);

let jobsTableBody = jobsTable.getElementsByTagName('tbody')[0];
let noJobsMessage = document.getElementById('no-jobs-message');

const terminalStates = [completedStatus, failedStatus, cancelledStatus];
const timelineEventMapping = {
	"INQ": 1,
	"UPL": 2,
	"PRO": 3,
	"PAR": 4,
	"COM": 99 // Don't set to 5 as this implies the "completed" state can be "in progress".
};

/**
 * Determine whether a state provided is a terminal state (i.e., COMPLETED and FAILED) or not.
 */ 
function isTerminalState(state){
	return terminalStates.includes(state);
}

/**
 * Return the last event that completed before the job failed.
 */
function getLastCompletedEvent(jobId){
	let prevEvents = document.getElementById(`job-logs-${jobId}`).prevEvents;
	if (prevEvents != undefined){
		for (let i = prevEvents.length - 1; i >= 0; i--){
			if (Object.hasOwn(timelineEventMapping, prevEvents[i])){
				return timelineEventMapping[prevEvents[i]];
			}
		}
	}
	return 0; // No previous events, therefore job failed to be created.
}

/**
 * Update the status (badge and timeline) for a job in the table.
 */
function updateJobStatus(jobId, status){
	// Badge
	document.querySelector(`tr[job_id="${jobId}"]`).setStatus(status);
	if(isTerminalState(status)){
		unfinishedJobs = unfinishedJobs.filter(item => item !== jobId);
	}
	// Timeline
	let jobTimeline = document.getElementById(`job-timeline-${jobId}`);
	if (status == "FAI" || status == "CAN"){
		jobTimeline.setProgress(getLastCompletedEvent(jobId), false);
	}else{
		jobTimeline.setProgress(timelineEventMapping[status], true);
	}
	// Options
	updateJobOptions(jobId, status);
}

/**
 * Update the options for a job in the table.
 */
function updateJobOptions(jobId, status){
	var showCancel = false, showRetry = false, showRemove = false;
	if (isTerminalState(status)){
		if (status != completedStatus){
			showRetry = true;
		}
		showRemove = true;
	}else{
		showCancel = true;
	}
	document.getElementById(`job-cancel-button-${jobId}`).hidden = !showCancel;
	document.getElementById(`job-remove-button-${jobId}`).hidden = !showRemove;
	document.getElementById(`job-retry-button-${jobId}`).hidden  = !showRetry;
}

/**
 * Update the logs for a job in the table.
 */
function updateJobLogs(jobId, logs){
	let jobLogs = document.getElementById(`job-logs-${jobId}`);

	let tmpLogs = "";
	jobLogs.prevEvents = [];

	for (let log in logs){
		tmpLogs += logs[log].str + "\n";
		if (logs[log].type){
			jobLogs.prevEvents.push(logs[log].type); // Record previous events.
		}
	}
	tmpLogs = trimRight(tmpLogs, 1); // Remove last newline character.

	if (tmpLogs !== jobLogs.prevLogs){
		jobLogs.prevLogs = jobLogs.innerHTML = tmpLogs;
	}
}

/**
 * Retrieve a list of jobs (based on the list of ids provided) and perform an operation on each of them.
 */
async function performOperationOnJobs(url, jobIds, operation){
	let result = await fetch(url + "?" + new URLSearchParams({job_ids: jobIds}));
	let json = await result.json();
	for (let key in json){
		operation(key, json[key]);
	}
}

/**
 * Update all the jobs in the table.
 */
async function updateJobs(jobs){
	await performOperationOnJobs(GET_JOB_LOGS_URL, jobs, updateJobLogs);
	await performOperationOnJobs(GET_JOB_STATUSES_URL, jobs, updateJobStatus);
}

/**
 * Update the remove job modal.
 */
function updateRemoveJobModal(job){
	document.getElementById("remove-job-modal-label").innerHTML = `${job.comment}`;
	document.getElementById("remove-job-modal-button").onclick = () => removeJob(job);
}

/**
 * Cancel a job.
 */
function cancelJob(job){

	let cancelButton = document.getElementById(`job-cancel-button-${job.job_id}`);
	cancelButton.disabled = true;
	isCancelling = true;

	fetch(CANCEL_JOB_URL, {
		method: "POST",
		body: JSON.stringify({'job_id': `${job.job_id}`}),
		headers:{
			'Content-Type': 'application/json',
			'X-CSRFToken': csrftoken
		}
	}).then(() => {
		cancelButton.disabled = false;
		isCancelling = false;	
		updateJobs(unfinishedJobs);
	});
}

/**
 * Retry a job.
 */
function retryJob(job){
}

/**
 * Remove a job.
 */
 function removeJob(job){
	document.getElementById(`job-info-${job.job_id}`).remove();
	document.getElementById(`job-${job.job_id}`).remove();

	// TODO: Send POST to remove job
}

/**
 * Add a job to the jobs table. If force open is set, the job's info collapsible will be toggled
 * open by default. (Necessary when creating the job using the job submission modal).
 */
function addJob(job, forceOpen=false){
	noJobsMessage.style.display = 'none';

	// Info
	let jobInfo = document.createElement("td");
	jobInfo.id = `job-info-${job.job_id}`;
	jobInfo.setAttribute("colspan", "6");
	jobInfo.setAttribute("ignoreOnSearch", true);
	jobInfo.style = "padding: 0 !important;";

	// Info > Collapse
	let jobInfoCollapse = document.createElement("div");
	jobInfo.append(jobInfoCollapse);
	jobInfoCollapse.id = `job-info-${job.job_id}`;
	jobInfoCollapse.classList.add("collapse", "p-0", "border-bottom");
	
	let jobInfoWrapper = document.createElement("div");
	jobInfoCollapse.append(jobInfoWrapper);
	jobInfoWrapper.style.height = "200px";
	jobInfoWrapper.classList.add("d-flex");

	// Info > Collapse > Timeline
	let jobTimeline = new Timeline();
	jobInfoWrapper.append(jobTimeline);
	jobTimeline.id = `job-timeline-${job.job_id}`;
	jobTimeline.style.width = "50%";

	// Info > Collapse > Logs
	let jobLogs = document.createElement("textarea");
	jobInfoWrapper.append(jobLogs);
	jobLogs.id = `job-logs-${job.job_id}`;
	jobLogs.classList.add("my-4", "me-4", "container");
	jobLogs.style = "resize: none; background-color: white; border-radius: 10px; padding: 6px 10px; border-color: var(--bs-gray-300)";
	jobLogs.style.width = "40%";
	jobLogs.setAttribute("readonly", true);

	// Info > Collapse > Options
	let jobOptions = document.createElement("div");
	jobInfoWrapper.append(jobOptions);
	jobOptions.classList.add("my-4", "me-4", "container");
	jobOptions.style.width = "10%";

	// Info > Collapse > Options > Cancel
	let cancelButton = document.createElement("button");
	jobOptions.append(cancelButton);
	cancelButton.id = `job-cancel-button-${job.job_id}`;
	cancelButton.innerHTML = "Cancel";
	cancelButton.onclick = () => cancelJob(job);

	// Info > Collapse > Options > Retry
	let retryButton = document.createElement("button");
	jobOptions.append(retryButton);
	retryButton.id = `job-retry-button-${job.job_id}`;
	retryButton.innerHTML = "Retry";
	retryButton.hidden = true;
	retryButton.onclick = () => retryJob(job);

	// Info > Collapse > Options > Remove
	let removeButton = document.createElement("button");
	jobOptions.append(removeButton);	
	removeButton.id = `job-remove-button-${job.job_id}`;
	removeButton.innerHTML = "Remove";
	removeButton.hidden = true;
	removeButton.setAttribute("data-bs-toggle", "modal");
	removeButton.setAttribute("data-bs-target", "#remove-job-modal");
	removeButton.onclick = () => updateRemoveJobModal(job);


	jobTimeline.addEvent("Created");
	jobTimeline.addEvent("In Queue");
	jobTimeline.addEvent("Uploading");
	jobTimeline.addEvent("Processing");
	jobTimeline.addEvent("Parsing");
	jobTimeline.addEvent("Completed");
	jobTimeline.setProgress(1, true);

	let jobRow = new Job(job, jobInfo);
	if (forceOpen){
		jobRow.showInfo(true);
	}
	jobsTableBody.prepend(jobInfo);
	jobsTableBody.prepend(jobRow);
}

let unfinishedJobs = [];
let result = fetch(GET_JOBS_URL).then(async (response)=>{
	let json = await response.json();
	let jobIDs = [];
	json.forEach(item => {
		addJob(item);
		if (!isTerminalState(item.status)){
			unfinishedJobs.push(item.job_id);
		}
		jobIDs.push(item.job_id);
	});

	updateJobs(jobIDs); // Update all jobs on load.
	if(json.length == 0){
		noJobsMessage.style.display = 'block';
	}
});

var isCancelling = false;

// Update the status and event logs of all unfinished jobs in the table.
setInterval(async function(){
	if(unfinishedJobs.length != 0 && !isCancelling){		
		updateJobs(unfinishedJobs);
	}
}, POLLING_TIME);

// Update the duration of all unfinished jobs in the table every second.
setInterval(async function(){
	for (let jobId of unfinishedJobs){
		let job = document.getElementById(`job-${jobId}`);
		if (!isTerminalState(job.status)){
			job.updateDuration();
		}
	}
}, 1000);