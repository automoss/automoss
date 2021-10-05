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
		this.line.style = "height:5px; right:0px; left:0px; color: var(--bs-gray-300); background-color: var(--bs-gray-300);";
		this.append(this.line);

		// Line > Fill
		this.lineFill = document.createElement("div");
		this.lineFill.classList.add("progress-bar");
		this.lineFill.style = "height:100%; width:0%; color: black; background-color: black;";
		this.line.append(this.lineFill);
	}

	addEvent(name){
		let event = new TimelineEvent(name);
		this.events.push(event);
		this.append(event);
	}
	
	setProgress(index){
		this.lineFill.style.width = `${(index / (this.events.length - 1)) * 100}%`;
		for (let i = 0; i < this.events.length; i++){
			let status = "";
			if(i < index){
				status = "completed";
			}else if(i == index){
				status = "inprogress";
			}else{
				status = "incompleted";
			}
			this.events[i].setStatus(status);
		}
	}
}
customElements.define("time-line", Timeline);