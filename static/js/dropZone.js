class DropZone extends HTMLElement {
	files = []

	constructor() {
		super();

		// Zone
		this.zone = document.createElement("div");
		this.zone.id = "zone";
		this.append(this.zone);

		// File List
		this.fileList = document.createElement("div");
		this.fileList.id = "file-list";
		this.fileList.classList.add("d-flex");
		this.fileList.classList.add("flex-column");
		this.append(this.fileList);


		// Zone > Icon
		this.zoneIcon = document.createElement("img");
		this.zoneIcon.id = "zone-icon";
		this.zoneIcon.src = this.getAttribute('uploadImgURL');
		this.zone.append(this.zoneIcon);

		// Zone > Text
		this.zoneText = document.createElement("label");
		this.zoneText.id = "zone-text";
		this.zoneText.textContent = "Drag and drop assignment files here!";
		this.zone.append(this.zoneText);

		// Zone > Input
		this.zoneInput = document.createElement("input");
		this.zoneInput.id = "zone-input";
		this.zoneInput.type = "file";
		this.zoneInput.multiple = false;
		this.zoneInput.addEventListener('dragenter', () => this.setZoneHighlight(true));
		this.zoneInput.addEventListener('dragleave', () => this.setZoneHighlight(false));
		this.zoneInput.addEventListener('drop', () => this.setZoneHighlight(false));
		this.zoneInput.addEventListener("change", () => this.addFile(this.zoneInput.files[0]));
		this.zone.append(this.zoneInput);

		// Zone > Info
		// this.zoneInfo = document.createElement("input");
		// this.zoneInfo.id = "zone-info";
		// this.zoneInfo.type = "image";
		// this.zoneInfo.src = this.getAttribute('infoImgURL');
		// this.zone.append(this.zoneInfo);
	}

	addFile(file) {
		this.zoneInput.value = '';

		if (!this.isValidFile(file)) {
			return;
		}
		this.files.push(file);
		this.updateSpacing(this.zone);

		// File
		let listedFile = document.createElement("div");
		listedFile.classList.add("position-relative");
		listedFile.classList.add("d-flex");
		listedFile.classList.add("w-100");
		listedFile.classList.add("mb-1");
		listedFile.style.height = "40px";
		listedFile.style.borderColor = "#CCC";
		listedFile.style.borderRadius = "10px";
		listedFile.style.borderWidth = "2px";
		this.fileList.append(listedFile);

		// File > Progress Bar
		let progressBar = document.createElement("div");
		progressBar.classList.add("progress");
		progressBar.classList.add("position-absolute");
		progressBar.classList.add("w-100");
		progressBar.style.height = "40px";
		progressBar.value = 0;
		listedFile.append(progressBar);

		let bar = document.createElement("div");
		bar.classList.add("progress-bar");
		bar.classList.add("progress-bar-striped");
		bar.classList.add("progress-bar-animated");
		bar.classList.add("bg-success");
		bar.role = "progressbar";
		bar.style.width = "50%";
		progressBar.append(bar);

		// File > Info
		let fileInfoDiv = document.createElement("div");
		fileInfoDiv.classList.add("d-flex");
		fileInfoDiv.classList.add("w-100");
		fileInfoDiv.classList.add("p-2");
		fileInfoDiv.style.zIndex = 1;
		listedFile.append(fileInfoDiv);

		// File > Info > Name
		let fileName = document.createElement("label");
		fileName.classList.add("flex-fill");
		fileName.textContent = file.name + ` (${this.getFileSize(file.size)})`;
		fileInfoDiv.append(fileName);

		// File > Info > Remove Button
		let fileRemoveButton = document.createElement("input");
		fileRemoveButton.type = "image";
		fileRemoveButton.src = this.getAttribute('removeImgURL');
		fileRemoveButton.style.height = "25px";
		fileRemoveButton.addEventListener("click", () => {
			const index = this.files.indexOf(file);
			if (index > -1) {
				this.files.splice(index, 1);
			}

			this.fileList.removeChild(listedFile);
			this.updateSpacing(this.zone);
		});
		fileInfoDiv.append(fileRemoveButton);

		// Update job form values.
		let jobName = document.getElementById('job-name');
		jobName.value = jobName.value || file.name.slice(0, file.name.length - 4);
	}

	isValidFile(file) {
		if (this.getFileExtension(file.name) != "zip") {
			return false; // Must upload a zip file.
		} else if (this.files.find(x => x.name == file.name)) {
			return false; // Can't upload the same file more than once.
		} else {
			return true;
		}
	}

	getFileExtension(fileName) {
		return fileName.split('.').pop();
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

	setZoneHighlight(isHighlighted) {
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

	updateSpacing() {
		if (this.files.length == 0) {
			this.zone.classList.remove("mb-2");
			document.getElementById("create-job-button").disabled = true;
		} else {
			this.zone.classList.add("mb-2");
			document.getElementById("create-job-button").disabled = false;
		}
	}
}

customElements.define('drop-zone', DropZone);