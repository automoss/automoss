/**
 * Determines whether or not a file has an extension from a list of given extensions.
 */
function hasExtension(fileName, extensions){
	for (var extension of extensions){
		if (fileName.endsWith("."+extension)){
			return true;
		}
	}
	return false;
}

const ARCHIVE_EXTENSIONS = ["tar", "tar.gz", "tar.xz", "zip"]
function isArchive(fileName){
	return hasExtension(fileName, ARCHIVE_EXTENSIONS);
}

const PROGRAM_EXTENSIONS = {
	"PY": ["py"], 
	"JA": ["java"], 
	"CP": ["C", "cc", "cpp", "cxx", "c++", "h", "H", "hh", "hpp", "hxx", "h++"], 
	"CX": ["c", "h"], 
	"CS": ["cs", "csx"], 
	"JS": ["js"], 
	"PL": ["pl", "plx", "pm", "xs", "t", "pod"], 
	"MP": ["asm", "s"]
};
function isSource(fileName, language){
	return hasExtension(fileName, PROGRAM_EXTENSIONS[language]);
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
 * Loops through all files and checks if it contains at least 1 source file (for a specific
 * programming language).
 */
async function isSingleSubmission(files){
	for (var file of files){
		for (var language of Object.keys(PROGRAM_EXTENSIONS)){
			if (isSource(file.name, language)){
				return true;
			}
		}
	}
	return false;
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

// Extend scope of functions to rest of WebApp
window.isArchive = isArchive;
window.isSource = isSource;
window.isSingleSubmission = isSingleSubmission;
window.extractSingle = extractSingle;
window.extractBatch = extractBatch;