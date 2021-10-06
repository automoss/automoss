// Setup the jobs table for searching.
let jobsTable = document.getElementById('job-table');
let jobsSearchBar = document.getElementById('job-search-bar');
setupTableSearch(jobsTable, jobsSearchBar);

let jobsTableBody = jobsTable.getElementsByTagName('tbody')[0];
let noJobsMessage = document.getElementById('no-jobs-message');

const terminalStates = [completedStatus, failedStatus];
const timelineEventMapping = {
	"INQ": 1,
	"UPL": 2,
	"PRO": 3,
	"PAR": 4,
	"COM": 6 // Don't set to 5 as this implies the "completed" state can be "in progress".
};

/**
 * Determine whether a status provided is a terminal status or not.
 * The terminal states are listed above (i.e., COMPLETED and FAILED).
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
		for (let i = prevEvents.length - 1; i >= 0; i--){ // Look for the first "valid" completed event.
			if (Object.hasOwn(timelineEventMapping, prevEvents[i])){
				return timelineEventMapping[prevEvents[i]];
			}
		}
	}
	return 0; // If no previous events, then the job failed to be created.
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
	if (status != "FAI"){
		jobTimeline.setCompleted(timelineEventMapping[status]);
	}else{
		jobTimeline.setFailed(getLastCompletedEvent(jobId));
	}
}

/**
 * Update the logs for a job in the table.
 */
function updateJobLogs(jobId, logs){
	let jobLogs = document.getElementById(`job-logs-${jobId}`);

	let tmpLogs = "";
	jobLogs.prevEvents = [];

	// Format the logs, which were retrieved as a json object.
	for (let log in logs){
		tmpLogs += logs[log].str + "\n";
		if (logs[log].type){
			jobLogs.prevEvents.push(logs[log].type); // Record the previous events (for status update above).
		}
	}
	tmpLogs = trimRight(tmpLogs, 1); // Remove the last newline character.

	// Set the logs only if they changed.
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
function updateJobs(jobs){
	performOperationOnJobs(GET_JOB_STATUSES_URL, jobs, updateJobStatus);
	performOperationOnJobs(GET_JOB_LOGS_URL, jobs, updateJobLogs);
}

/**
 * Add a job to the jobs table. If force open is set, the job's info collapsible will be toggled
 * open by default. (Necessary when creating the job using the job submission modal).
 */
function addJob(job, forceOpen=false){
	noJobsMessage.style.display = 'none';

	// Info
	let jobInfo = document.createElement("td");
	jobInfo.setAttribute("colspan", "6");
	jobInfo.style = "padding: 0 !important;";

	// Info > Collapse
	let jobInfoCollapse = document.createElement("div");
	jobInfo.append(jobInfoCollapse);
	jobInfoCollapse.id = `job-info-${job.job_id}`;
	jobInfoCollapse.classList.add("collapse");
	jobInfoCollapse.classList.add("p-0");
	jobInfoCollapse.classList.add("border-bottom");

	let jobInfoWrapper = document.createElement("div");
	jobInfoCollapse.append(jobInfoWrapper);
	jobInfoWrapper.style.height = "200px";
	jobInfoWrapper.classList.add("d-flex");

	// Info > Collapse > Timeline
	let jobTimeline = new Timeline();
	jobInfoWrapper.append(jobTimeline);
	jobTimeline.id = `job-timeline-${job.job_id}`;
	jobTimeline.style.width = "60%";

	// Info > Collapse > Logs
	let jobLogs = document.createElement("textarea");
	jobInfoWrapper.append(jobLogs);
	jobLogs.id = `job-logs-${job.job_id}`;
	jobLogs.classList.add("my-4");
	jobLogs.classList.add("me-4");
	jobLogs.classList.add("container");
	jobLogs.style = "resize: none; background-color: white; border-radius: 10px; padding: 6px 10px; border-color: var(--bs-gray-300)";
	jobLogs.style.width = "40%";
	jobLogs.setAttribute("readonly", true);

	jobTimeline.addEvent("Created");
	jobTimeline.addEvent("In Queue");
	jobTimeline.addEvent("Uploading");
	jobTimeline.addEvent("Processing");
	jobTimeline.addEvent("Parsing");
	jobTimeline.addEvent("Completed");

	if (forceOpen){
		jobInfoCollapse.classList.add("show");
	}
	jobTimeline.setCompleted(1);

	jobsTableBody.prepend(jobInfo);
	jobsTableBody.prepend(new Job(job, jobInfo));
}

let unfinishedJobs = [];
let result = fetch(GET_JOBS_URL).then(async (response)=>{
	let json = await response.json();
	json.forEach(item => {
		addJob(item);
		if (!isTerminalState(item.status)){
			unfinishedJobs.push(item.job_id);
		}
		updateJobs([item.job_id]); // Immediately update all job logs and statuses on load.
	});
	if(json.length == 0){
		noJobsMessage.style.display = 'block';
	}
});

// Update the status and logs of unfinished jobs in the table.
setInterval(async function(){
	if(unfinishedJobs.length != 0){		
		updateJobs(unfinishedJobs);
	}
}, POLLING_TIME);

// Update the duration of unfinished jobs in the table every second.
setInterval(async function(){
	for (let jobId of unfinishedJobs){
		let job = document.getElementById(`job-${jobId}`);
		if (!isTerminalState(job.status)){
			job.updateDuration();
		}
	}
}, 1000);