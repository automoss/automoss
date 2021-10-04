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
	return numSourceFiles > numArchives;
}

/**
 * Trims the end of a string by n characters.
 */
 function trimRight(str, n){
	return str.slice(0, str.length - n)
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
		var path = trimRight(pathWithName, name.length);
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
			buffer += (await new Response(new File([await readFileData(file)], file.name)).text() + "\n\n");
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
	
	// Archive must be a file
	if (!(archive instanceof File)){
		archive = new File([await readFileData(archive)], archive.name); // Convert "uncompress file" to a file
	}

	// Wait until archived file has been opened
	let openArchivePromise = new Promise((resolve, reject) => {
		archiveOpenFile(archive, "", (opened) => {
			resolve(opened);
		});
	});
	let opened = await openArchivePromise;

	// Add all file entries in the archive to a list of files
	let files = [];
	opened.entries.forEach(function(file) {
		if(file.is_file){
			files.push(file);
		}
	});
	return files;
}

/**
 * Extracts multiple archives from a single student.
 * This is necessary, as students may include multiple submission attachments that contain code.
 */
async function extractMultiple(archives, language){
	var buffer = "";
	for (var archive of archives){
		buffer += await extractSingle(await extractFiles(archive), language);
	}
	return buffer;
}

/**
 * Extract and perform an operation a batch of student submissions.
 * 
 * The following assumptions must be made:
 * - There exists a root folder that divides all students in a batch.
 * - Archives submitted are one of the accepted file types.
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
			var student = pathFromStudent; // Batch could just be a folder containing archives.
			if (pathSepIndex != -1){
				student = pathFromStudent.substring(0, pathSepIndex); // Student's folder name.
			}
			if (student != prevStudent){
				if (prevStudent != ""){
					onExtract(prevStudent, await extractMultiple(studentArchives, language));
					studentArchives = []; // Clear current student's archives.
				}
				prevStudent = student;
			}
			studentArchives.push(file); // Record this file as a student's archive.
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
let createJobModalElement = document.getElementById("create-job-modal");
let createJobModal = new bootstrap.Modal(createJobModalElement);
let createJobForm = document.getElementById("create-job-form");
let jobDropZone = document.getElementById("job-drop-zone");
let jobName = document.getElementById("job-name");
let jobLanguage = document.getElementById("job-language");
let jobMaxMatchesUntilIgnored = document.getElementById("job-max-until-ignored");
let jobMaxMatchesDisplayed = document.getElementById("job-max-displayed-matches");
let jobAttachBaseFiles = document.getElementById("job-attach-base-files");
let jobErrorMessage = document.getElementById("job-error-message");
let createJobButton = document.getElementById("create-job-button");

let isDisplayingError = false;
function displayError(message){
	if (isDisplayingError){
		return;
	}
	jobErrorMessage.textContent = message;
	createJobModalElement.classList.add("animate__animated", "animate__shakeX");
	isDisplayingError = true;

	setTimeout(function(){
		jobErrorMessage.textContent = "";
		createJobModalElement.classList.remove("animate__animated", "animate__shakeX");
		isDisplayingError = false;
	}, 3000);
}

function updateDropZoneTarget(){
	jobDropZone.zoneText.innerHTML = `Drag and drop <b>${jobAttachBaseFiles.checked ? "base" : "student"}</b> files here!`;
}

function setEnabled(isEnabled){
	jobDropZone.setInteractable(isEnabled);
	createJobButton.disabled = !isEnabled;
}

createJobForm.onsubmit = async (e) => {

	e.preventDefault();
	setEnabled(false);

	try{
		// Create a new form (and capture name, language, max matches until ignored and max matches displayed)
		let jobFormData = new FormData(createJobForm);
		
		function appendFilesToForm(name, data, isBaseFile){
			jobFormData.append(isBaseFile ? BASE_FILES_NAME : FILES_NAME, new Blob([data]), name);
		}

		let numStudents = 0;
		for (let jobDropZoneFile of jobDropZone.files){
			let archive = jobDropZoneFile.file;
			let languageId = jobLanguage.options[jobLanguage.selectedIndex].getAttribute("language-id");
			let isBaseFile = jobDropZoneFile.isBaseFile;

			let files = await extractFiles(archive, languageId);

			if (await isSingleSubmission(files, languageId) || isBaseFile){
				appendFilesToForm(archive.name, await extractSingle(files, languageId), isBaseFile);
				if (!isBaseFile){
					numStudents++;
				}
			}else{
				let counter = 0;
				await extractBatch(files, languageId, (name, data) => {
					appendFilesToForm(name, data, false);
					jobDropZoneFile.setProgress(++counter / files.length);
				});
				numStudents += counter;
			}
			jobDropZoneFile.setProgress(1);
		}

		// Submit a new job with the created form
		let result = await fetch(NEW_JOB_URL, {
			method: "POST",
			body: jobFormData
		});

		// Obtain job as json data and add to the jobs table
		let json = await result.json();
		addJob(json);
		unfinishedJobs.push(json["job_id"]);

		// Hide and reset the form and dropzone
		createJobModal.hide();
		setTimeout(() => {
			createJobForm.reset();
			jobDropZone.reset();
			updateDropZoneTarget();
		}, 200);

	}catch (err){
		console.err(err);
	}
	finally{
		setEnabled(true);
	}
};

jobDropZone.onFileAdded = async (jobDropZoneFile) => {
	
	let archive = jobDropZoneFile.file;
	let files = await extractFiles(archive);

	function getExtension(name){
		return name.split(".").pop();
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

	// Type
	let isSingle = await isSingleSubmission(files);

	// Programming Language
	let langTestFiles = [...files];
	if (!isSingle){
		let counter = 0;
		let maxArchives = 3;
		for (let file of files){
			if (isArchive(file.name)){
				let tmpArchive = await extractFiles(file);
				for (let tmpFile of tmpArchive){
					langTestFiles.push(tmpFile);
				}
				counter++;
			}
			if (counter > maxArchives) break; // Only check three archives
		}
	}
	let languageId = getProgrammingLanguageId(langTestFiles);
	let language = SUPPORTED_LANGUAGES[languageId][0];

	// Tags
	if (jobAttachBaseFiles.checked){
		jobDropZoneFile.addTag("Base", "var(--bs-dark)");
		jobDropZoneFile.isBaseFile = true;
	}else{
		jobDropZoneFile.addTag(isSingle ? "Single" : `Batch (${files.length})`, "var(--bs-dark)");
	}

	if (jobDropZone.files.length >= 1){
		jobName.value = jobName.value || trimRight(archive.name, getExtension(archive.name).length+1);
		jobLanguage.value = language;
		createJobButton.disabled = false;
	}
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