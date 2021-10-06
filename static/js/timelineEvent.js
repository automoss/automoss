class TimelineEvent extends HTMLElement{
	constructor(name){
		super();

		this.setAttribute("data-bs-toggle", "tooltip");
		this.setAttribute("data-bs-placement", "bottom");
		this.setAttribute("title", "");
		new bootstrap.Tooltip(this);

		// Event
		this.event = document.createElement("div");
		this.append(this.event);
		this.event.classList.add("position-relative");
		this.event.style.height = this.event.style.width = "50px";

		// Event > Icon
		this.iconDiv = document.createElement("div");
		this.event.append(this.iconDiv);
		this.iconDiv.classList.add("position-absolute");
		this.iconDiv.style.height = this.iconDiv.style.width = "50px";

		// Event > Ping
		this.ping = document.createElement("div");
		this.iconDiv.append(this.ping);
		this.ping.classList.add("position-absolute");
		this.ping.classList.add("translate-middle");
		this.ping.classList.add("start-50");
		this.ping.classList.add("top-50");
		this.ping.hidden = false;

		this.pingOuter = document.createElement("div");
		this.ping.append(this.pingOuter);
		this.pingOuter.classList.add("ping");
		this.pingOuter.style = "width: 90px; height: 90px; border-radius: 50%; background-color: #06BDFC;";

		// Event > Icon
		this.icon = document.createElement("span");
		this.iconDiv.append(this.icon);
		this.icon.classList.add("timeline-event-image");
		this.icon.classList.add("position-absolute");
		this.icon.classList.add("translate-middle");
		this.icon.classList.add("start-50");
		this.icon.classList.add("top-50");
		this.icon.style = "height: 50px; width: 50px;";

		// Event > Name
		this.name = document.createElement("label");
		this.event.append(this.name);
		this.name.classList.add("position-absolute");
		this.name.classList.add("text-nowrap");
		this.name.classList.add("translate-middle-x");
		this.name.classList.add("start-50");
		this.name.style = "margin-top: -25px"
		this.name.innerHTML = name;

		this.setStatus("Incompleted"); // Default to "Incompleted" state.
	}

	/**
	 * Sets the status (icon, tooltip and ping) of the event.
	 */
	setStatus(status){
		this.icon.setAttribute("status", `${status}`);
		this.setAttribute("data-bs-original-title", status);
		
		this.ping.hidden = status != "In Progress";
	}
}
customElements.define("time-line-event", TimelineEvent);