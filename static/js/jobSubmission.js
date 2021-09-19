/**
 * Determines whether or not a file name ends with an extension from a list of given extensions.
 */
function hasExtension(fileName, extensions){
	for (var extension of extensions){
		if (fileName.endsWith("."+extension)){
			return true;
		}
	}
	return false;
}

/**
 * Determines whether or not a file is an archive.
 */
function isArchive(fileName){
	return hasExtension(fileName, SUPPORTED_ARCHIVES);
}

/**
 * Determines whether or not a file is a source file. If a programming language code is specified,
 * this will return if it is a source file for that particular language.
 */
function isSource(fileName, language){
	let extensions = [];
	if (language != null){
		extensions = SUPPORTED_LANGUAGES[language];
	}else{
		for (let key of Object.keys(SUPPORTED_LANGUAGES)){
			extensions = extensions.concat(SUPPORTED_LANGUAGES[key][3]);
		}
	}
	return hasExtension(fileName, extensions);
}

/**
 * Returns a file's name when given its path.
 */ 
function getFileNameFromPath(filePath){
    var dirSepIndex = filePath.lastIndexOf("/");
    if (dirSepIndex != -1){
        return filePath.substring(dirSepIndex+1);
    }
    return filePath;
}

/**
 * Renames a given file and returns it.
 */
 function renameFile(file, newName){
	return new File([file], newName, {
		type: file.type,
		lastModified: file.lastModified,
	});
}

/**
 * Loops through all files and counts the number of archives and source files.
 * Single submissions will contain more source files than archives, while
 * batches will contain more archives than source files.
 */
async function isSingleSubmission(files){
	let numSourceFiles = 0;
	let numArchives = 0;
	for (var file of files){
		if (isSource(file.name)){
			numSourceFiles++;
		}else if (isArchive(file.name)){
			numArchives++;
		}
	}
	console.log(numSourceFiles + " - " + numArchives)
	return numSourceFiles > numArchives;
}

/**
 * Find the first difference between two strings, and return the index of that character.
 * Credit: https://stackoverflow.com/a/32858679/7840247
 */
function findFirstDiffIndex(a, b){
	var longerLength = Math.max(a.length, b.length);
	for (var i = 0; i < longerLength; i++){
		if (a[i] !== b[i]) return i;
	}
	return -1;
}

/** 
 * Job submission relies on the crucial assumption that there exists a single folder (i.e., root)
 * with a list of files/folders that divide all students in a batch.
 * 
 * The following function returns the index of the root folder in a path for a list of files from
 * a common directory. The algorithm works as follows:
 * Find two different student archives and then compare their paths to determine the root.
 */
function getRootIndex(files){
	var prevPath = "";
	for (var file of files){
		var pathWithName = file.name;
		var name = getFileNameFromPath(pathWithName);
		var path = pathWithName.trimRight(name.length);
		if (prevPath != ""){
			if (path != prevPath){
				var diff = findFirstDiffIndex(path, prevPath);
				var same = path.substring(0, diff);
				return same.lastIndexOf("/")+1; // shift left in path to beginning of contained folder
			}
		}
		if (isArchive(name)){
			prevPath = path;
		}
	}
	return -1;
}

/**
 * Reads the data from a file and returns it.
 */
async function readFileData(file){
	return new Promise((resolve, reject) => {
		file.readData(function(data){
			resolve(data);
		});
	});
}

/**
 * Extracts all the source files from a single student's archive, and "stitches" them together.
 */
async function extractSingle(files, language){
	var buffer = "";
	for (var file of files){
		if (isSource(file.name, language)){
			buffer += ">>> " + file.name + " <<<\n";
			buffer += (await new Response(file).text() + "\n\n");
		}
	}
	return buffer;
}

/**
 * Extract and return a list of files.
 */
async function extractFiles(archive) {

	// Wait until formats have been loaded
	await loadFormatsPromise;

	// Wait until archived file has been opened
	let openArchivePromise = new Promise((resolve, reject) => {
		archiveOpenFile(archive, '', (opened) => {
			resolve(opened);
		});
	});
	let opened = await openArchivePromise;

	// Wait until all the files have been added to a list
	let files = [];
	opened.entries.forEach(function(file) {
		if(file.is_file){
			files.push(file);
		}
	});
	return files;
}

/**
 * Extracts all a student's archives into one. This is necessary, as students may have multiple
 * archives in their submission attachments which contain code that needs to be checked.
 */
async function extractMultiple(archives, language){
	var buffer = "";
	for (var archive of archives){
		buffer += await extractSingle(await extractFiles(archive), language);
	}
	return buffer;
}

/**
 * When provided an archive containing a list of students with no particular format, extract and
 * perform an operation on each of the stiched student submissions.
 * 
 * The following assumptions must be made:
 * - There exists a root folder that divides all students in a batch.
 * - Archives submitted are one of the accepted file types (i.e., tar, tar.gz, tar.xz or zip).
 * - Students cannot submit folders, and so once an archive is found, it is considered to be in
 *   a "terminal" directory.
 * 
 * The algorithm works as follows:
 * - Loop through each file until you encounter a student's archive.
 * - Continue looping through files, and maintain a list of all the current student's archives.
 * - Once a new student is detected, extract the previous student's files.
 * - Repeat until there are no files left.
 * - Finally, check if the last student had files that weren't extracted (since extractions
 *   only take place on the event of a student change).
 */
async function extractBatch(files, language, onExtract){
	var prevStudent = "";
	var rootIndex = getRootIndex(files);
	var studentArchives = [];
	for (var file of files){
		if (isArchive(file.name)){
			var pathFromStudent = file.name.substring(rootIndex);
			var pathSepIndex = pathFromStudent.indexOf("/");
			var student = pathFromStudent; // batch could just be a folder containing archives
			if (pathSepIndex != -1){
				student = pathFromStudent.substring(0, pathSepIndex); // student's folder name
			}
			if (student != prevStudent){
				if (prevStudent != ""){
					onExtract(prevStudent, await extractMultiple(studentArchives, language));
					studentArchives = []; // clear current student's archives
				}
				prevStudent = student;
			}
			studentArchives.push(file); // record this file as a student's archive
		}
	}
	if (studentArchives.length > 0){
		onExtract(student, await extractMultiple(studentArchives, language));
	}
}

// Extend scope of submission functions to rest of WebApp
window.isArchive = isArchive;
window.isSource = isSource;
window.isSingleSubmission = isSingleSubmission;
window.extractSingle = extractSingle;
window.extractFiles = extractFiles;
window.extractBatch = extractBatch;




// Load all supported archive format types
let loadFormatsPromise = new Promise((resolve, reject) => {
	loadArchiveFormats(["zip", "tar", "rar"], () => {
		resolve();
	});
});


// Document references to job submission elements
let createJobModalElement = document.getElementById('create-job-modal');
let createJobModal = new bootstrap.Modal(createJobModalElement);
let createJobForm = document.getElementById('create-job-form');
let jobDropZone = document.getElementById('job-drop-zone');
let jobName = document.getElementById('job-name');
let jobLanguage = document.getElementById('job-language');
let jobMaxMatchesUntilIgnored = document.getElementById('job-max-until-ignored');
let jobMaxMatchesDisplayed = document.getElementById('job-max-displayed-matches');
let jobErrorMessage = document.getElementById("job-error-message");
let createJobButton = document.getElementById('create-job-button');

let isDisplayingError = false;
function displayError(message){
	if (isDisplayingError){
		return;
	}
	jobErrorMessage.textContent = message;
	createJobModalElement.classList.add("animated", "shake");
	isDisplayingError = true;

	setTimeout(function(){
		jobErrorMessage.textContent = "";
		createJobModalElement.classList.remove("animated", "shake");
		isDisplayingError = false;
	}, 3000);
}

function overwriteJobData(jobDropZoneFile, name, data){
	jobDropZoneFile.data.push({name: name, data: data});
}

createJobForm.onsubmit = async (e) => {

	e.preventDefault();

	// Create a new form (and capture name, language, max matches until ignored and max matches displayed)
	let jobFormData = new FormData(createJobForm);
	let counter = 0;
	for (let jobDropZoneFile of jobDropZone.files){
		for (let data of jobDropZoneFile.data){
			jobFormData.append(FILES_NAME, new Blob([data.data]), data.name);
			counter++;
		}
	}

	// Can't submit only 1 student
	if (counter <= 1){
		displayError("Please submit more than 1 students' files.");
		return;
	}

	// Submit a new job with the created form
	let result = await fetch(NEW_JOB_URL, {
		method: 'POST',
		body: jobFormData,
	});

	// Receive the result as a json object and add it to the jobs table
	let json = await result.json();
	addJob(json);
	unfinishedJobs.push(json['job_id']);

	// Hide and reset the form data and dropzone
	createJobModal.hide();
	createJobForm.reset();
	jobDropZone.reset();
};

jobDropZone.onFileAdded = async (jobDropZoneFile) => {

	createJobButton.disabled = true;

	function getExtension(name){
		return name.split('.').pop();
	}

	function getProgrammingLanguageId(files){
		let d = {};
		for (let key in SUPPORTED_LANGUAGES){
			d[key] = 0;
		}
		for (let file of files){
			let extension = getExtension(file.name);
			for (let key in SUPPORTED_LANGUAGES){
				if(SUPPORTED_LANGUAGES[key][2].includes(extension)){
					d[key] += 1;
				}
			}
		}
		return Object.entries(d).reduce((a, b) => a[1] > b[1] ? a : b)[0]
	}

	let archive = jobDropZoneFile.file;
	let files = await extractFiles(archive);
	console.log("0");

	let length = files.length * 2;
	let counter = 0;

	// Type
	let single = await isSingleSubmission(files);

	let t0 = performance.now();
	let langTestFiles = [...files];
	if (!single){
		for (let file of files){
			if (isArchive(file.name)){
				let tmpArchive = await extractFileNames(file);
				for (let tmpFile of tmpArchive){
					langTestFiles.push(tmpFile);
				}
				counter++;
				jobDropZoneFile.setProgress(counter / length);
			}
		}
	}

	let t1 = performance.now();
	console.log('Took', t1-t0)

	// Programming Language
	let languageId = getProgrammingLanguageId(langTestFiles);
	let language = SUPPORTED_LANGUAGES[languageId][0];

	console.log(language)
	// 
	if (single){
		overwriteJobData(jobDropZoneFile, archive.name, await extractSingle(files, languageId));
		jobDropZoneFile.setProgress(1);

	}else{
		await extractBatch(files, languageId, (name, data) => {
			overwriteJobData(jobDropZoneFile, name, data);
			counter++;
			jobDropZoneFile.setProgress(counter / length);
		});
	}

	// Tags
	jobDropZoneFile.addTag(single ? "Single" : "Batch", "var(--bs-dark)");
	jobDropZoneFile.addTag(language, "var(--bs-dark)");

	jobName.value = jobName.value || archive.name.slice(0, archive.name.length - 4);
	jobLanguage.value = language;
	createJobButton.disabled = false;
};

jobDropZone.onFileRemoved = () => {
	if (jobDropZone.files.length == 0) {
		jobName.value = "";
		jobLanguage.selectedIndex = 0;
		jobMaxMatchesUntilIgnored.value = DEFAULT_MOSS_SETTINGS.max_until_ignored;
		jobMaxMatchesDisplayed.value = DEFAULT_MOSS_SETTINGS.max_displayed_matches;

		createJobButton.disabled = true;
	}
};

jobDropZone.onFileRejected = (reason) => {
	displayError(reason);
}