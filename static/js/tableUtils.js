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
function show(row, onShow){
	row.style.display = "table-row";
	onShow(row);
}

/**
 * Hide a table row.
 */
function hide(row, onHide){
	row.style.display = "none";
	onHide(row);
}

/**
 * Setup a table and search bar to allow for searching.
 */
function setupTableSearch(table, searchBar, onShow, onHide){
	searchBar.oninput = function(){
		for (let row of table.tBodies[0].children){
			if (row.hasAttribute("ignoreOnSearch")){
				continue;
			}
			if(contains(row, searchBar.value)){
				show(row, onShow);
			}else{
				hide(row, onHide);
			}
		}
	}
}
window.setupTableSearch = setupTableSearch;