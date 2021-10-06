class Timeline extends HTMLElement{
	events = [];

	constructor(){
		super();

		this.classList.add("position-relative");
		this.classList.add("d-flex");
		this.classList.add("justify-content-between");
		this.classList.add("align-items-center");
		this.classList.add("px-5");

		// Line
		this.line = document.createElement("div");
		this.line.classList.add("position-absolute");
		this.line.classList.add("mx-5");
		this.line.style = "height: 3px; right: 0px; left:0px; color: var(--bs-gray-300); background-color: var(--bs-gray-300);";
		this.append(this.line);

		// Line > Fill
		this.lineFill = document.createElement("div");
		this.lineFill.classList.add("progress-bar");
		this.lineFill.style = "height: 100%; width: 0%; color: var(--bs-success); background-color: var(--bs-success);";
		this.line.append(this.lineFill);
	}

	/**
	 * Add an event to the timeline.
	 */
	addEvent(name){
		let event = new TimelineEvent(name);
		this.events.push(event);
		this.append(event);
	}

	/**
	 * Sets the progress (i.e., "In Progress" or "Failed") of an event on the timeline. All events prior to the current event
	 * are assumed to be completed, while those posterior are assumed to be incompleted.
	 */
	setProgress(index, isInProgress=true){
		let progress = ((index >= this.events.length) ? 1 : (index / (this.events.length - 1)));
		this.lineFill.style.width = `${progress * 100}%`;
		for (let i = 0; i < this.events.length; i++){
			let status = "";
			if(i < index){
				status = "Completed";
			}else if(i == index){
				status = isInProgress ? "In Progress" : "Failed";
			}else{
				status = "Incompleted";
			}
			this.events[i].setStatus(status);
		}
	}
}
customElements.define("time-line", Timeline);