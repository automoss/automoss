let jobsTable = document.getElementById('job-table');
let jobsSearchBar = document.getElementById('job-search-bar');
setupTableSearch(jobsTable, jobsSearchBar);

let jobsTableBody = jobsTable.getElementsByTagName('tbody')[0];

function addJob(job) {
	document.getElementById('no-jobs-message').style.display = 'none'

	// let jobInfo = document.createElement("td");
	// jobInfo.setAttribute("colspan", "6");
	// jobInfo.style="padding: 0 !important;";

	// let jobInfoCollapse = document.createElement("div");
	// jobInfoCollapse.id = `job-info-${job.job_id}`;
	// jobInfoCollapse.classList.add("collapse");
	// jobInfo.append(jobInfoCollapse);

	// Info
	// let jobStatusMap = document.createElement("div");
	// jobStatusMap.classList.add("d-flex");
	// jobStatusMap.classList.add("flex-column");
	// jobInfoCollapse.append(jobStatusMap);

	// jobsTableBody.prepend(jobInfo);
	jobsTableBody.prepend(new Job(job));
}

const terminalStates = [completedStatus, failedStatus];
function isTerminalState(state){
	return terminalStates.includes(state)
}

let unfinishedJobs = [];
let result = fetch(GET_JOBS_URL).then(async (response)=>{
	let json = await response.json()
	json.forEach(item => {
		addJob(item);
		if (!isTerminalState(item.status)){
			unfinishedJobs.push(item.job_id)
		}
	});
	if(json.length == 0){
		document.getElementById('no-jobs-message').style.display = 'block';
	}
});

setInterval(async function(){
	if(unfinishedJobs.length == 0) {
		return;
	}
	let result = await fetch(GET_JOB_STATUSES_URL + "?" + new URLSearchParams({job_ids: unfinishedJobs}));
	let json = await result.json();
	for (let key in json) {
		var value = json[key];
		document.querySelector(`tr[job_id="${key}"]`).setStatus(value);
		if(isTerminalState(value)){
			unfinishedJobs = unfinishedJobs.filter(item => item !== key);
		}
	}
}, POLLING_TIME);