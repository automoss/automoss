let jobsTable = document.getElementById('job-table');
let jobsSearchBar = document.getElementById('job-search-bar');
setupTableSearch(jobsTable, jobsSearchBar);

let jobsTableBody = jobsTable.getElementsByTagName('tbody')[0];

function updateJobStatus(jobId, status){
	document.querySelector(`tr[job_id="${jobId}"]`).setStatus(status);
	if(isTerminalState(status)){
		unfinishedJobs = unfinishedJobs.filter(item => item !== jobId);
	}

	let jobTimeline = document.getElementById(`job-timeline-${jobId}`);
	let statusIndexMapping = {
		"INQ": 1,
		"UPL": 2,
		"PRO": 3,
		"PAR": 4,
		"COM": -1,
		"FAI": -1 // TODO: Don't keep a record of which event we failed on?
	};
	jobTimeline.setCompleted(statusIndexMapping[status]);
}

function updateJobLogs(jobId, logs){
	let jobLogs = document.getElementById(`job-logs-${jobId}`);
	jobLogs.innerHTML = "";
	for (let log in logs){
		jobLogs.innerHTML += logs[log] + "\n";
	}
	jobLogs.innerHTML = trimRight(jobLogs.innerHTML, 1);
}

function addJob(job){
	document.getElementById('no-jobs-message').style.display = 'none'

	// Info
	let jobInfo = document.createElement("td");
	jobInfo.setAttribute("colspan", "6");
	jobInfo.style="padding: 0 !important;";

	// Info > Collapse
	let jobInfoCollapse = document.createElement("div");
	jobInfoCollapse.id = `job-info-${job.job_id}`;
	jobInfoCollapse.classList.add("collapse");
	jobInfoCollapse.classList.add("p-0");
	jobInfoCollapse.classList.add("border");
	jobInfo.append(jobInfoCollapse);

	// Info > Collapse > Wrapper
	let jobInfoWrapper = document.createElement("div");
	jobInfoCollapse.append(jobInfoWrapper);
	jobInfoWrapper.style.height = "200px";
	jobInfoWrapper.classList.add("d-flex");

	// Info > Collapse > Wrapper > Timeline
	let jobTimeline = new Timeline();
	jobTimeline.id = `job-timeline-${job.job_id}`;
	jobInfoWrapper.append(jobTimeline);
	jobTimeline.style.width = "60%";

	jobTimeline.addEvent("Created");
	jobTimeline.addEvent("In Queue");
	jobTimeline.addEvent("Uploading");
	jobTimeline.addEvent("Processing");
	jobTimeline.addEvent("Parsing");
	jobTimeline.addEvent("Completed");

	// Info > Collapse > Wrapper > Logs
	let jobLogs = document.createElement("textarea");
	jobInfoWrapper.append(jobLogs);
	jobLogs.id = `job-logs-${job.job_id}`;
	jobLogs.classList.add("my-4");
	jobLogs.classList.add("me-4");
	jobLogs.classList.add("me-4");
	jobLogs.style = "resize: none; background-color: white; border-radius: 10px; padding: 6px 10px; border-color: var(--bs-gray-300)";
	jobLogs.style.width = "40%";
	jobLogs.setAttribute("readonly", true);

	jobsTableBody.prepend(jobInfo);
	jobsTableBody.prepend(new Job(job));
}

const terminalStates = [completedStatus, failedStatus];
function isTerminalState(state){
	return terminalStates.includes(state);
}

let unfinishedJobs = [];
let result = fetch(GET_JOBS_URL).then(async (response)=>{
	let json = await response.json();
	json.forEach(item => {
		addJob(item);
		if (!isTerminalState(item.status)){
			unfinishedJobs.push(item.job_id);
		}else{
			updateJobs(GET_JOB_STATUSES_URL, [item.job_id], updateJobStatus);
			updateJobs(GET_JOB_LOGS_URL, [item.job_id], updateJobLogs);
		}
	});
	if(json.length == 0){
		document.getElementById('no-jobs-message').style.display = 'block';
	}
});

async function updateJobs(url, jobs, f){
	let result = await fetch(url + "?" + new URLSearchParams({job_ids: jobs}));
	let json = await result.json();
	for (let key in json){
		f(key, json[key]);
	}
}

setInterval(async function(){
	if(unfinishedJobs.length == 0){
		return;
	}
	updateJobs(GET_JOB_STATUSES_URL, unfinishedJobs, updateJobStatus);
	updateJobs(GET_JOB_LOGS_URL, unfinishedJobs, updateJobLogs);
}, POLLING_TIME);

setInterval(async function(){
	for (let row of jobsTable.tBodies[0].children){
		if (row instanceof Job){
			if (!isTerminalState(row.status)){
				row.updateDuration();
			}
		}
	}
}, 1000);