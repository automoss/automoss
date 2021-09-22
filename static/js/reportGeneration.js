function generateHTML(fileName, html) {
	var element = document.createElement('a');
	element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(html));
	element.setAttribute('download', fileName);
	element.click();
}

async function getElementsByTagNameText(tagName, ref){
	let elements = document.getElementsByTagName(tagName);
	let elements_text = "";
	for (let element of elements){
		if (element.innerHTML == "" && false){ // TODO: Download external text and add that instead of the link!
			elements_text += await getExternalText(element[ref]);
		}else{
			elements_text += element.outerHTML.replace("/static/", "http://localhost:8000/static/"); // TODO: Change to templated.
		}
		elements_text += "\n";
	}
	return elements_text;
}

async function getExternalText(url){
	let response = await fetch(url, {
		method: "GET"
	});
	return await response.text();
}

async function downloadReport(){
	let links = await getElementsByTagNameText("link", "href");
	let styles = await getElementsByTagNameText("style");
	let scripts = await getElementsByTagNameText("script", "src");
	let report = document.getElementById("report").innerHTML;
	let html = links + styles + report + scripts
	generateHTML("report.html", html);
}