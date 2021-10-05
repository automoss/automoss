class TimelineEvent extends HTMLElement{

	constructor(name){
		super();

		this.setAttribute("data-bs-toggle", "tooltip");
		this.setAttribute("data-bs-placement", "bottom");
		this.setAttribute("title", "");
		new bootstrap.Tooltip(this);

		// Icon
		this.div = document.createElement("div");
		this.div.classList.add("position-relative");
		this.div.style.height = this.div.style.width = "50px";
		this.append(this.div);

		// Icon
		this.icon = document.createElement("img");
		this.div.append(this.icon);
		this.icon.style.height = this.icon.style.width = "50px";

		// Name
		this.name = document.createElement("label");
		this.div.append(this.name);
		this.name.classList.add("position-absolute");
		this.name.classList.add("text-nowrap");
		this.name.classList.add("translate-middle-x");
		this.name.classList.add("start-50");
		this.name.style = "margin-top: -25px"
		this.name.innerHTML = name;

		this.setStatus("incompleted");
	}

	setTooltip(text){
		this.setAttribute("data-bs-original-title", text);
	}

	setStatus(status){
		this.icon.className = `timeline-${status}`;
		if (status == "inprogress"){
			this.icon.classList.add("animate__animated");
			this.icon.classList.add("animate__pulse");
		}
	}
}
customElements.define("time-line-event", TimelineEvent);