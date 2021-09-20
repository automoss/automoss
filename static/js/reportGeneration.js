function downloadHTML(fileName, html) {
	var element = document.createElement('a');
	element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(html));
	element.setAttribute('download', fileName);
	element.click();
}

function addDependencies(html, styles, scripts){
	return styles.join("") + html + scripts.join("");
}

function downloadReport(){
	
	let styles = [];
	let scripts = [];
	

	downloadHTML("report.html", addDependencies(html, styles, scripts));
}