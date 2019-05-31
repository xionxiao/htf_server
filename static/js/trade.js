function ExcuteBuyStock() {
	console.log("Buy")
	console.log($('#form-buy').serialize());
	$.post("http://localhost:8888/buy",$('#form-buy').serialize(), function(data){
		$("#result-panel .panel-body").empyt()
	})
}

function ExcuteSellStock() {
	console.log("Sell")
	console.log($('#form-sell').serialize());
	$.post("http://localhost:8888/sell",$('#form-sell').serialize())
}

function ExcuteCancelOrder() {
	console.log("Cancel")
	console.log($('#form-cancel').serialize());
	$.post("http://localhost:8888/cancel",$('#form-cancel').serialize())
}

function RefreshStockPool() {
	console.log("Refresh Stock Pool")
	$.get("http://localhost:8888/query",{"catalogues":"stockpool"}, function(data) {
		console.log(data);
		obj = eval("("+data+")");
		$("#stock-pool .panel-body table tbody").empty();
		item_str = ""
		for ( i in obj) {
			item_str += "<tr><td>"+i+"</td><td>"+obj[i]["融券数量"]+"</td></tr>";
		}
		item_str += "<tr><td></td><td></td></tr>";
		console.log(item_str);
		$("#stock-pool .panel-body table tbody").append(item_str);
	})
}

function RefreshOrderList() {
	console.log("Refresh Order List")
}

function ClearResultPanel() {
	console.log("Clear Result Panel");
	$("#result-panel .panel-body").empyt();
	
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