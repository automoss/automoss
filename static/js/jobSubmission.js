function hasValidExtension(fileName, validExtensions){
	for (var extension of validExtensions){
		if (fileName.endsWith("."+extension)){
			return true;
		}
	}
	return false;
}

function getFileNameFromPath(filePath){
    var dirSepIndex = filePath.lastIndexOf("/");
    if (dirSepIndex != -1){
        return filePath.substring(dirSepIndex+1);
    }
    return filePath;
}

const ARCHIVE_EXTENSIONS = ["tar", "tar.gz", "tar.xz", "rar", "zip"]
function isArchive(fileName){
	return hasValidExtension(fileName, ARCHIVE_EXTENSIONS)
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
	return hasValidExtension(fileName, PROGRAM_EXTENSIONS[language]);
}

async function isSingleSubmission(files, language){
	for (var file of files){
		if (isSource(file.name, language)){
			return true;
		}
	}
	return false;
}

// https://stackoverflow.com/a/32858679/7840247
function findFirstDiffIndex(a, b){
	var longerLength = Math.max(a.length, b.length);
	for (var i = 0; i < longerLength; i++){
		if (a[i] !== b[i]) return i;
	}
	return -1;
}

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
				return same.lastIndexOf("/")+1;
			}
		}
		if (isArchive(name)){
			prevPath = path;
		}
	}
	return -1;
}

async function getArchiveFiles(archive){
	let extractedArchive = await JSZip.loadAsync(archive);
	const files = [];
	extractedArchive.forEach(function (relativePath, file) {
		files.push(file);
	});
	Promise.all(files);
	return files;
}

async function extractSingle(files, language){
	var buffer = "";
	for (var file of files){
		if (isSource(file.name, language)){
			buffer += ">>> " + file.name + " <<<\n";
			let blob = await file.async('blob');
			let text = await new Response(blob).text();
			buffer += (text + "\n\n");
		}
	}
	return buffer;
}

async function extractMultiple(archives, language){
	var buffer = "";
	for (var archive of archives){
		var blob = await archive.async("blob");
		var file = new File([blob], archive.name, { type: 'application/zip' }); // must convert zipped archive to a file before unzipping
		buffer += await extractSingle(await getArchiveFiles(file), language);
	}
	return buffer;
}

async function extractBatch(files, language, onExtract){
	var prevStudent = "";
	var rootIndex = getRootIndex(files);
	var studentArchives = [];
	for (var file of files){
		if (isArchive(file.name)){
			var pathFromStudent = file.name.substring(rootIndex);
			var pathSepIndex = pathFromStudent.indexOf("/");
			var student = pathFromStudent;
			if (pathSepIndex != -1){
				student = pathFromStudent.substring(0, pathSepIndex);
			}
			if (student != prevStudent){
				if (prevStudent != ""){
					onExtract(prevStudent, await extractMultiple(studentArchives, language));
					studentArchives = [];
				}
				prevStudent = student;
			}
			studentArchives.push(file);
		}
	}
	if (studentArchives.length > 0){
		onExtract(student, await extractMultiple(studentArchives, language));
	}
}

// Extend scope of functions to rest of WebApp
window.isArchive = isArchive;
window.isSource = isSource;
window.extractBatch = extractBatch;
window.extractSingle = extractSingle;
window.isSingleSubmission = isSingleSubmission;
window.getArchiveFiles = getArchiveFiles;
window.getRootIndex = getRootIndex;