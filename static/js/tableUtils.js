/**
 * Get all nested text from a node and its children.
 */
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

/**
 * Check if a table row contains the specified text.
 */
function contains(row, text){
	return getText(row).toLowerCase().includes(text.toLowerCase());
}

/**
 * Show a table row.
 */
function show(row){
	row.style.display = "table-row";
}

/**
 * Hide a table row.
 */
function hide(row){
	row.style.display = "none";
}

/**
 * Setup a table and search bar to allow for searching.
 */
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