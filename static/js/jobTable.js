let jobsTable = document.getElementById('job-table');
let jobsSearchBar = document.getElementById('job-search-bar');

setupTableSearch(jobsTable, jobsSearchBar);

function addJob(job) {
    document.getElementById('no-jobs-message').style.display = 'none'

    let jobTableBody = jobsTable.getElementsByTagName('tbody')[0];

    let jobInfo = document.createElement("td");
    jobInfo.setAttribute("colspan", "4");
    jobInfo.style="padding: 0 !important;";

    let jobAccordion = document.createElement("div");
    jobAccordion.id = `job-accordion-${job.job_id}`;
    jobAccordion.classList.add("collapse");
    jobInfo.append(jobAccordion);


    // TEST
    let label = document.createElement("label");
    label.style.height = "200px";
    label.innerText = "Test";
    jobAccordion.append(label);

    
    jobTableBody.prepend(jobInfo);
    jobTableBody.prepend(new Job(job));
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
        document.getElementById('no-jobs-message').style.display = 'block'
    }
});

setInterval(async function() {
    if(unfinishedJobs.length == 0) {
        return;
    }
    let result = await fetch(
        GET_JOB_STATUSES_URL + "?" + new URLSearchParams({job_ids: unfinishedJobs})
    )

    let json = await result.json();

    for (let key in json) {
        var value = json[key];

        document.querySelector(`tr[job_id="${key}"]`).setStatus(value)
        if(isTerminalState(value)){
            unfinishedJobs = unfinishedJobs.filter(item => item !== key)
        }
    }
    
}, POLLING_TIME);