let jobsTable = document.getElementById('job-table');
let jobsSearchBar = document.getElementById('job-search-bar');
setupTableSearch(jobsTable, jobsSearchBar);

let jobsTableBody = jobsTable.getElementsByTagName('tbody')[0];

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
	jobInfoWrapper.append(jobTimeline);
	jobTimeline.classList.add("w-75");

	jobTimeline.addEvent("Created");
	jobTimeline.addEvent("In Queue");
	jobTimeline.addEvent("Uploading");
	jobTimeline.addEvent("Processing");
	jobTimeline.addEvent("Parsing");
	jobTimeline.addEvent("Completed");

	// Info > Collapse > Wrapper > Logs
	let jobLogs = document.createElement("textarea");
	jobInfoWrapper.append(jobLogs);
	jobLogs.classList.add("w-25");
	jobLogs.classList.add("my-4");
	jobLogs.classList.add("me-4");
	jobLogs.style = "resize: none; background-color: white; border-radius: 10px; border-color: var(--bs-gray-300)";
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

setInterval(async function(){
	for (let row of jobsTable.tBodies[0].children){
		if (row instanceof Job){
			if (!isTerminalState(row.status)){
				row.updateDuration();
			}
		}
	}
}, 1000);