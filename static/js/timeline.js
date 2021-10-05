class Timeline extends HTMLElement{
    events = {};

    constructor(){
        super();

        this.classList.add("position-relative");
        this.classList.add("d-flex");
        this.classList.add("justify-content-between");
        this.classList.add("align-items-center");
        this.classList.add("px-5");

        // Line
        this.line = document.createElement("hr");
        this.line.classList.add("position-absolute");
        this.line.classList.add("mx-5");
        this.line.style = "height:10px; right:0px; left:0px; opacity: 50%; color: var(--bs-gray-300); background-color: var(--bs-gray-300);";
        this.append(this.line);
    }

    addEvent(name){
        this.events[name] = new TimelineEvent(name);
        this.append(this.events[name]);
    }
    
    setProgress(event){
        
    }
}
customElements.define("time-line", Timeline);