class DropZoneFile extends HTMLElement {

    constructor(file, dropZone) {
        super();
        this.file = file;

		this.classList.add("position-relative");
		this.classList.add("d-flex");
		this.classList.add("w-100");
		this.classList.add("mt-1");

		// Progress Bar
		this.progressBar = document.createElement("div");
        this.progressBar.id = "progress-bar";
        this.progressBar.classList.add("position-absolute");
		this.progressBar.classList.add("progress-bar");
		this.progressBar.classList.add("progress-bar-striped");
		this.progressBar.classList.add("progress-bar-animated");
		this.progressBar.classList.add("bg-success");
		this.append(this.progressBar);

		// Info
		this.info = document.createElement("div");
        this.info.id = "info";
		this.info.classList.add("d-flex");
		this.info.classList.add("w-100");
		this.info.classList.add("p-2");
		this.append(this.info);

		// Info > Name
		this.name = document.createElement("label");
        this.name.id = "name";
		this.name.textContent = file.name + ` (${dropZone.getFileSize(file.size)})`;
		this.name.classList.add("flex-fill");
		this.info.append(this.name);

		// Info > Remove Button
		this.removeButton = document.createElement("button");
        this.removeButton.id = "remove-button";
        this.removeButton.type = "button";
		this.removeButton.addEventListener("click", () => dropZone.removeFile(this));
		this.info.append(this.removeButton);

        // Info > Remove Button > Icon
        this.removeButtonIcon = document.createElement("img");
        this.removeButton.append(this.removeButtonIcon);
    }

    setProgress(progress) {
        this.progressBar.style.width = progress;
    }
}

customElements.define('drop-zone-file', DropZoneFile);