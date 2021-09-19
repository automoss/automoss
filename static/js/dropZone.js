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
		this.zoneInput.addEventListener('dragenter', () => this.setHighlighted(true));
		this.zoneInput.addEventListener('dragleave', () => this.setHighlighted(false));
		this.zoneInput.addEventListener('drop', () => this.setHighlighted(false));
		this.zoneInput.addEventListener("change", () => this.addFiles(this.zoneInput.files));
		this.zone.append(this.zoneInput);

		// Zone > Info
		this.zoneInfo = document.createElement("img");
		this.zoneInfo.id = "zone-info";
		this.zone.append(this.zoneInfo);
	}

	addFiles(files) {
		for (let file of files) {
			this.addFile(file);
		}
		this.zoneInput.value = '';
	}

	addFile(file) {
		if (!this.isValidFile(file)) {
			return;
		}

		let dropZoneFile = new DropZoneFile(file, this)
		this.files.push(dropZoneFile);
		this.fileList.append(dropZoneFile);

		this.onFileAdded(dropZoneFile);
	}

	removeFile(file) {
		const index = this.files.indexOf(file);
		if (index > -1) {
			this.files.splice(index, 1);
		}
		file.remove();
		
		this.onFileRemoved();
	}
	
	reset() {
		while (this.files.length > 0) {
			this.removeFile(this.files[0]);
		}
	}

	hasExtension(fileName, extensions){
		for (var extension of extensions){
			if (fileName.endsWith("."+extension)){
				return true;
			}
		}
		return false;
	}

	isValidFile(file) {
		if (!this.hasExtension(file.name, this.getAttribute("filetypes").split(","))) {
			this.onFileRejected("You must upload an archive.");
			return false;
		} else if (this.files.find(x => x.file.name == file.name)) {
			this.onFileRejected("That file has already been uploaded.");
			return false;
		} else {
			return true;
		}
	}

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

	onFileAdded(dropZoneFile){
	}

	onFileRemoved(){
	}

	onFileRejected(reason){
	}
}

customElements.define('drop-zone', DropZone);