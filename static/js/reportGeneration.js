/**
 * Generate and download an html file for a given string of html text.
 */
function generate(fileName, html) {
	let element = document.createElement('a');
	element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(html));
	element.setAttribute('download', fileName);
	element.click();
}

/**
 * Extract all elements in a document with a given tag, except those with "ignoreOnExtract".
 */
async function extract(tagName, onExternal){
	let elements = document.getElementsByTagName(tagName);
	let elements_text = "";
	for (let element of elements){
		if (element.hasAttribute("ignoreOnExtract")){
			continue;
		}
		if (element.innerHTML.trim() === ""){ // No inner text, therefore an external link/script.
			elements_text += await onExternal(element);
		}else{
			elements_text += element.outerHTML;
		}
		elements_text += "\n";
	}
	return elements_text;
}

/**
 * Fetch a document from a URL and return it as plain text.
 */
async function getExternalText(url){
	let response = await fetch(url, {
		mode: "no-cors" // https://developer.mozilla.org/en-US/docs/Web/API/Request/mode
	});
	return await response.text();
}

/**
 * External stylesheet links should surround elements with "style" tags.
 */
async function onExternalLink(element){
	let innerHTML = element.innerHTML;
	if (element.rel === "stylesheet"){
		innerHTML = await getExternalText(element["href"]);
	}
	return `<style>\n${innerHTML}\n</style>`;
}

/**
 * External scripts should surround elements with "script" tags.
 */
async function onExternalScript(element){
	return `<script>\n${await getExternalText(element["src"])}\n</script>`;
}

/**
 * Insert a string into another at a specified index.
 */
function addStr(str, index, stringToAdd){
	return str.substring(0, index) + stringToAdd + str.substring(index, str.length);
}

/**
 * Download the matches report as an html file. All external links and scripts should be included in the file, sothat
 * it can be viewed offline.
 */
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