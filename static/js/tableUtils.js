function getText(node){
	let text = '';
	if (node.nodeType === document.TEXT_NODE){
		text += node.nodeValue + ' ';
	}else{
		for (let child of node.childNodes){
			text += this.getText(child);
		}
	}
	return text;
}
function contains(row, text){
	return getText(row).toLowerCase().includes(text.toLowerCase());
}
function show(row){
	row.style.display = "table-row";
}
function hide(row){
	row.style.display = "none";
}

function setupTableSearch(table, searchBar){
	searchBar.oninput = function(){
		for (let row of table.tBodies[0].children){
			if(contains(row, searchBar.value)){
				show(row);
			}else{
				hide(row);
			}
		}
	}
}
window.setupTableSearch = setupTableSearch;