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
		this.line.style = "height:4px; right:0px; left:0px; color: var(--bs-gray-300); background-color: var(--bs-gray-300);";
		this.append(this.line);

		// Line > Fill
		this.lineFill = document.createElement("div");
		this.lineFill.classList.add("progress-bar");
		this.lineFill.style = "height:100%; width:0%; color: var(--bs-success); background-color: var(--bs-success);";
		this.line.append(this.lineFill);
	}

	addEvent(name){
		let event = new TimelineEvent(name);
		this.events.push(event);
		this.append(event);
	}

	setCompleted(index){

		let progress = ((index == -1) ? 1 : (index / (this.events.length - 1)));
		this.lineFill.style.width = `${progress * 100}%`;

		for (let i = 0; i < this.events.length; i++){
			let status = "";
			if(i < index || index == -1){
				status = "Completed";
			}else if(i == index){
				status = "In Progress";
			}else{
				status = "Incompleted";
			}
			this.events[i].setStatus(status);
		}
	}

	setFailed(index){
		this.events[index].setStatus("Failed");
	}
}
customElements.define("time-line", Timeline);