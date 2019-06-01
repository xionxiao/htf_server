function ExcuteBuyStock() {
	console.log("Buy");
	console.log($('#form-buy').serialize());
	params = $('#form-buy');
	console.log(params.val())
	$.post("http://localhost:8888/buy",$('#form-buy').serialize(), function(data){
		console.log(data)
		$("#result-panel .panel-body").append(data);
		$("#result-panel .panel-body").append("<br>");
		RefreshStockPool()
	})
}

function ExcuteSellStock() {
	console.log("Sell");
	params = $('#form-sell').serialize();
	console.log(params);
	price = $('#form-sell #sell_price').val();
	console.log(price);
	if (price) {
		$.post("http://localhost:8888/sell",params, function(data){
			$("#result-panel .panel-body").append(data);
			$("#result-panel .panel-body").append("<br>");
			RefreshStockPool();
		});
	} else {
		$.post("http://localhost:8888/instant_sell",params, function(data){
			$("#result-panel .panel-body").append(data);
			$("#result-panel .panel-body").append("<br>");
			RefreshStockPool();
		});
	}
}

function ExcuteCancelOrder() {
	console.log("Cancel");
	console.log($('#form-cancel').serialize());
	$.post("http://localhost:8888/cancel",$('#form-cancel').serialize(), function(data){
		$("#result-panel .panel-body").append(data);
		$("#result-panel .panel-body").append("<br>");
		RefreshStockPool()
	})
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
		$("#stock-pool .panel-body table tbody").append(item_str);
	})
}

function RefreshOrderList() {
	console.log("Refresh Order List")
}

function ClearResultPanel() {
	console.log("Clear Result Panel");
	$("#result-panel .panel-body").empty();
}

function KeyShortcuts(evt) {
	if (evt.altKey) {
		console.log(evt.keyCode)
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