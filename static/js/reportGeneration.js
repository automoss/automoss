function generate(fileName, html) {
	let element = document.createElement('a');
	element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(html));
	element.setAttribute('download', fileName);
	element.click();
}

async function extract(tagName, onExternal){
	let elements = document.getElementsByTagName(tagName);
	let elements_text = "";
	for (let element of elements){
		if (element.hasAttribute("ignoreOnExtract")){
			continue;
		}
		if (element.innerHTML.trim() === ""){
			elements_text += await onExternal(element);
		}else{
			elements_text += element.outerHTML;
		}
		elements_text += "\n";
	}
	return elements_text;
}

async function getExternalText(url){
	let response = await fetch(url, {
		mode: "no-cors"
	});
	return await response.text();
}
async function onExternalLink(element){
	let innerHTML = element.innerHTML;
	if (element.rel === "stylesheet"){
		innerHTML = await getExternalText(element["href"]);
	}
	return `<style>\n${innerHTML}\n</style>`;
}
async function onExternalScript(element){
	return `<script>\n${await getExternalText(element["src"])}\n</script>`;
}

async function downloadReport(){

	let extractions = [extract("link", onExternalLink), extract("style"), extract("script", onExternalScript)];	
	let [links, styles, scripts] = await Promise.all(extractions);

	let report = document.getElementById("report").innerHTML;
	let html = links + styles + report + scripts
	generate("report.html", html);
}