let jobsTable = document.getElementById('job-table');
let jobsSearchBar = document.getElementById('job-search-bar');
setupTableSearch(jobsTable, jobsSearchBar);

let jobsTableBody = jobsTable.getElementsByTagName('tbody')[0];
let noJobsMessage = document.getElementById('no-jobs-message');

const terminalStates = [completedStatus, failedStatus];
function isTerminalState(state){
	return terminalStates.includes(state);
}


let eventMapping = { 
	"INQ": 1,
	"UPL": 2,
	"PRO": 3,
	"PAR": 4,
	"COM": 6
};

function getLastCompletedEvent(jobId){
	let prevEvents = document.getElementById(`job-logs-${jobId}`).prevEvents;
	if (prevEvents != undefined){
		for (let i = prevEvents.length - 1; i >= 0; i--){
			if (Object.hasOwn(eventMapping, prevEvents[i])){
				return eventMapping[prevEvents[i]];
			}
		}
	}
	return 0;
}

function updateJobStatus(jobId, status){
	document.querySelector(`tr[job_id="${jobId}"]`).setStatus(status);
	if(isTerminalState(status)){
		unfinishedJobs = unfinishedJobs.filter(item => item !== jobId);
	}

	let jobTimeline = document.getElementById(`job-timeline-${jobId}`);
	if (status != "FAI"){
		jobTimeline.setCompleted(eventMapping[status]);
	}else{
		jobTimeline.setFailed(getLastCompletedEvent(jobId));
	}
}

function updateJobLogs(jobId, logs){
	let jobLogs = document.getElementById(`job-logs-${jobId}`);

	let tmpLogs = "";
	jobLogs.prevEvents = [];

	for (let log in logs){
		tmpLogs += logs[log].str + "\n";

		if (logs[log].type){
			jobLogs.prevEvents.push(logs[log].type);
		}
	}
	tmpLogs = trimRight(tmpLogs, 1);

	if (tmpLogs !== jobLogs.prevLogs){
		jobLogs.prevLogs = jobLogs.innerHTML = tmpLogs;
	}
}

function updateJobs(jobs){
	updateJobsTable(GET_JOB_STATUSES_URL, jobs, updateJobStatus);
	updateJobsTable(GET_JOB_LOGS_URL, jobs, updateJobLogs);
}

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
	jobInfoCollapse.classList.add("border");

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
		}else{
			updateJobs([item.job_id]);
		}
	});
	if(json.length == 0){
		noJobsMessage.style.display = 'block';
	}
});

async function updateJobsTable(url, jobs, f){
	let result = await fetch(url + "?" + new URLSearchParams({job_ids: jobs}));
	let json = await result.json();
	for (let key in json){
		f(key, json[key]);
	}
}

setInterval(async function(){
	if(unfinishedJobs.length != 0){		
		updateJobs(unfinishedJobs);
	}
}, POLLING_TIME);

setInterval(async function(){
	for (let jobId of unfinishedJobs){
		let job = document.getElementById(`job-${jobId}`);
		if (!isTerminalState(job.status)){
			job.updateDuration();
		}
	}
}, 1000);