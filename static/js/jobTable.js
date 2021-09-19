let jobTable = document.getElementById('job-table')
function addJob(job) {
    document.getElementById('no-jobs-message').style.display = 'none'
    jobTable.getElementsByTagName('tbody')[0].prepend(new Job(job))
}

let jobSearch = document.getElementById('job-search')
jobSearch.oninput = function(){
    for (let child of jobTable.tBodies[0].children){
        if(child.contains(jobSearch.value)){
            child.show()
        }else{
            child.hide()
        }
    }
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
        GET_JOB_STATUES_URL + "?" + new URLSearchParams({job_ids: unfinishedJobs})
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