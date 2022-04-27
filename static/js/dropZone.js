class DropZone extends HTMLElement {
	files = []

	constructor() {
		super();

		// Zone
		this.zone = document.createElement("div");
		this.zone.id = "zone";
		this.append(this.zone);
		this.zone.classList.add("mb-2");

		// File List
		this.fileList = document.createElement("div");
		this.fileList.id = "file-list";
		this.fileList.classList.add("d-flex");
		this.fileList.classList.add("flex-column");
		this.append(this.fileList);

		// Zone > Icon
		this.zoneIcon = document.createElement("img");
		this.zoneIcon.id = "zone-icon";
		this.zoneIcon.src = "/static/img/upload.svg";
		this.zone.append(this.zoneIcon);

		// Zone > Text
		this.zoneText = document.createElement("label");
		this.zoneText.id = "zone-text";
		this.zoneText.innerHTML = this.getAttribute("text");
		this.zone.append(this.zoneText);

		// Zone > Input
		this.zoneInput = document.createElement("input");
		this.zoneInput.id = "zone-input";
		this.zoneInput.type = "file";
		this.zoneInput.multiple = true;
		this.zoneInput.title = "Supported File Formats: " + this.getAttribute("filetypes").split(",").join(", ");
		this.zoneInput.addEventListener('dragenter', () => this.setHighlighted(true));
		this.zoneInput.addEventListener('dragleave', () => this.setHighlighted(false));
		this.zoneInput.addEventListener('drop', () => this.setHighlighted(false));
		this.zoneInput.addEventListener("change", () => this.addFiles(this.zoneInput.files));
		this.zone.append(this.zoneInput);

		// Zone > Info
		//this.zoneInfo = document.createElement("img");
		//this.zoneInfo.id = "zone-info";
		//this.zone.append(this.zoneInfo);
	}

	/**
	 * Add multiple files at once to the file list.
	 */
	addFiles(files) {
		for (let file of files) {
			this.addFile(file);
		}
		this.zoneInput.value = '';
	}

	/**
	 * Add a file to the file list.
	 */
	addFile(file) {
		if (!this.isValidFile(file)) {
			return;
		}

		let dropZoneFile = new DropZoneFile(file, this)
		this.files.push(dropZoneFile);
		this.fileList.append(dropZoneFile);

		this.onFileAdded(dropZoneFile);
	}

	/**
	 * Remove a file from the file list.
	 */
	removeFile(file) {
		const index = this.files.indexOf(file);
		if (index > -1) {
			this.files.splice(index, 1);
		}
		file.remove();
		
		this.onFileRemoved();
	}
	
	/**
	 * Remove all files and clear the call to action text.
	 */
	reset() {
		while (this.files.length > 0) {
			this.removeFile(this.files[0]);
		}
		this.zoneInput.value = '';
		this.setC2A("");
	}

	/**
	 * Set the progress of all files to zero.
	 */
	resetProgress(){
		for (let file of this.files) {
			file.setProgress(0);
		}
	}

	/**
	 * Determines whether or not a file name ends with an extension from a list of given extensions.
	 */
	hasExtension(fileName, extensions){
		for (var extension of extensions){
			if (fileName.endsWith("."+extension)){
				return true;
			}
		}
		return false;
	}

	/**
	 * Determines whether or not a file dragged in is valid.
	 */
	isValidFile(file) {
		if (!this.hasExtension(file.name, this.getAttribute("filetypes").split(","))) {
			this.onFileRejected("File must be an archive.");
			return false;
		} else if (this.files.find(x => x.file.name == file.name)) {
			this.onFileRejected("File has already been uploaded.");
			return false;
		} else if (file.size > this.getAttribute("maxfilesize")) {
			this.onFileRejected("File size exceeds " + (this.getAttribute("maxfilesize") / 1000000) + "MB.");
			return false;
		} else {
			return true;
		}
	}

	/**
	 * Formats the size of a file given its size in bytes.
	 */
	getFileSize(fileSize) {
		let sizeKB = fileSize / 1024;
		let sizeMB = sizeKB / 1024;
		let sizeGB = sizeMB / 1024;

		let size = 0;
		let unit = "";

		if (sizeGB > 1) {
			size = sizeGB;
			unit = "GB";
		} else if (sizeMB > 1) {
			size = sizeMB;
			unit = "MB"
		} else {
			size = sizeKB;
			unit = "KB";
		}

		return `${Math.round(size * 100) / 100} ${unit}`;
	}

	/**
	 * Sets the call to action text message in the center of the drop zone.
	 */
	setC2A(message){
		this.zoneText.innerHTML = message;
	}

	/**
	 * Sets the highlighted state of the drop zone.
	 */
	setHighlighted(isHighlighted) {
		if (isHighlighted) {
			this.zone.style.backgroundColor = "#EEE";
			this.zone.classList.add("progress-bar-striped");
			this.zone.classList.add("progress-bar-animated");
		} else {
			this.zone.style.backgroundColor = "#FFF";
			this.zone.classList.remove("progress-bar-striped");
			this.zone.classList.remove("progress-bar-animated");
		}
	}

	/**
	 * Sets the interactable state of the drop zone and file list.
	 */
	setInteractable(isInteractable){
		this.zoneInput.disabled = !isInteractable;
		for (let file of this.files){
			file.setRemovable(isInteractable);
		}
	}

	/**
	 * Callback invoked on file added.
	 */
	onFileAdded(dropZoneFile){
	}

	/**
	 * Callback invoked on file removed.
	 */
	onFileRemoved(){
	}

	/**
	 * Callback invoked on file rejected.
	 */
	onFileRejected(reason){
	}
}
customElements.define("drop-zone", DropZone);