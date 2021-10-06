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

function addStr(str, index, stringToAdd){
	return str.substring(0, index) + stringToAdd + str.substring(index, str.length);
}

async function downloadReport(){
	let extractions = [extract("link", onExternalLink), extract("style"), extract("script", onExternalScript)];	
	let [links, styles, scripts] = await Promise.all(extractions);

	let title = "<div class=\"d-flex justify-content-center\">" + document.getElementById("title").outerHTML + "</div>";
	let matches = document.getElementById("matches").innerHTML;
	matches = addStr(matches, matches.indexOf("100vh"), "200px + "); // Extend height of matches element to fit to document.

	let report = "<div class=\"p-4\">" + title + matches + "</div>";
	let html = links + styles + report + scripts
	generate("report.html", html);
}