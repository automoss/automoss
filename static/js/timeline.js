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
		this.div = document.createElement("div");
		this.div.classList.add("position-absolute");
		this.div.classList.add("mx-5");
		this.div.style = "height:5px; right:0px; left:0px;";
		this.append(this.div);

		this.line = document.createElement("div");
		this.line.classList.add("progress-bar");
		this.line.style = "height:5px; width:100%; opacity: 50%; color: var(--bs-gray-300); background-color: var(--bs-gray-300);";
		this.div.append(this.line);
	}

	addEvent(name){
		let event = new TimelineEvent(name);
		this.events.push(event);
		this.append(event);
	}
	
	setProgress(progress){
		this.line.style.width = `${progress*100}%`;
		let t = progress*this.events.length;
		for (let i = 0; i < this.events.length; i++){
			this.events[i].setEnabled(i <= t);
		}
	}
}
customElements.define("time-line", Timeline);