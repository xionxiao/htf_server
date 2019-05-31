function Buy() {
}

function Sell() {
}

function Cancel() {
}

function RefreshStockPool() {
	console.log("Refresh Stock Pool")
	$('#stock-pool .panel-body').empty();
}

function RefreshOrderList() {
	console.log("Refresh Order List")
	$('#order-list .panel-body').empty();
}

function ClearResultPanel() {
	console.log("Clear Result Panel")
	$('#result-panel .panel-body').empty();
}

function KeyShortcuts(evt) {
	console.log(evt.keyCode)
	console.log(evt.altKey)
	if (evt.altKey) {
		switch (evt.keyCode)
		{
		case 49:
			var item = document.getElementById("buy_stock");
			item.focus()
			break;
		case 50:
			var item = document.getElementById("sell_stock");
			item.focus()
			item.vaule=""
			break;
		case 51:
			var item = document.getElementById("cancel_order");
			item.focus()
			break;
		}
	}
}