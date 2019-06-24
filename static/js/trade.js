var host = "http://" + window.location.host;

function ExcuteBuyStock() {
	console.log("Buy");
	console.log($('#form-buy').serialize());
	params = $('#form-buy');
	console.log(params.val());
	$.post(host + "/buy",$('#form-buy').serialize(), function(data){
		console.log(data)
		$("#result-panel .panel-body").prepend(data +  "<br>");
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
		$.post(host + "/sell",params, function(data){
			$("#result-panel .panel-body").prepend(data +  "<br>");
			RefreshStockPool();
		});
	} else {
		$.post(host + "instant_sell",params, function(data){
			$("#result-panel .panel-body").prepend(data +  "<br>");
			RefreshStockPool();
		});
	}
}

function ExcuteCancelOrder() {
	console.log("Cancel");
	console.log($('#form-cancel').serialize());
	$.post(host + "/cancel",$('#form-cancel').serialize(), function(data){
		$("#result-panel .panel-body").prepend(data +  "<br>");
		RefreshStockPool();
	})
}

function RefreshStockPool() {
	console.log("Refresh Stock Pool");
	$.get(host + "/query",{"catalogues":"stockpool"}, function(data) {
		obj = eval("("+data+")");
		$("#stock-pool .panel-body table tbody").empty();
		item_str = "";
		var color = "gray";
		for ( i in obj) {
			item_str += "<tr id="+i+'" style="color:' + color +';"' + ">";
			item_str += "<td>"+i+"</td>";
			item_str += "<td>"+obj[i]["证券名称"]+"</td>";
			item_str += "<td>"+obj[i]["涨停价"]+"</td>";
			item_str += "<td>"+obj[i]["融券数量"]+"</td>";
			item_str += "</tr>";
		}
		$("#stock-pool .panel-body table tbody").prepend(item_str);
	})
}

function CompareFactory(propertyName) {
	return function(object1, object2) {
		var value1 = object1[propertyName];
		var value2 = object2[propertyName];
		if (value1 < value2) {
			return -1;
		} else if (value1 > value2) {
			return 1;
		} else {
			return 0;
		}
	}
}

function compareDate(t1, t2) {
	now = new Date();
	today = now.toDateString() + " ";
	c1 = Date.parse(today + t1["成交时间"]);
	c2 = Date.parse(today + t2["成交时间"]);
	return c2 - c1
}

function RefreshOrderList() {
	console.log("Refresh Order List")
	$.get(host + "/query",{"catalogues":"orderlist"}, function(data) {
		//console.log(data);
		obj = eval("("+data+")");
		obj_array = []
		for (i in obj) {
			obj_array.push(obj[i]);
		}
		obj = obj_array.sort(compareDate);
		$("#order-list .panel-body table tbody").empty();
		item_str = ""
		for ( i in obj) {
			var color = 'blue'
			if (obj[i]["买卖标志"] == "买入") {
					var color = 'red'
			} 
			item_str += "<tr id="+i+'" style="color:' + color +';"' + ">";
			item_str += "<td>"+obj[i]["证券代码"]+"</td>";
			item_str += "<td>"+obj[i]["证券名称"]+"</td>";
			item_str += "<td>"+obj[i]["买卖标志"]+"</td>";
			item_str += "<td>"+obj[i]["成交价格"]+"</td>";
			item_str += "<td>"+obj[i]["成交数量"]+"</td>";
			item_str += "<td>"+obj[i]["成交时间"]+"</td>";
			item_str += "</tr>";
		}
		$("#order-list .panel-body table tbody").append(item_str);
	})
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
		case 49: // Alt+1
			var item = document.getElementById("buy_stock");
			item.focus()
			break;
		case 50:  // Alt+2
			var item = document.getElementById("sell_stock");
			item.focus()
			item.vaule=""
			break;
		case 51:  // Alt+3
			var item = document.getElementById("cancel_order");
			item.focus()
			break;
		}
		return
	}
	if ($("#sell_price").is(":focus"))
	{
		evt.preventDefault()
		var val = parseFloat($("#sell_price").val());
		console.log(val);
		if (isNaN(val))
			val = 0.01;
		switch (evt.keyCode)
		{
		case 38: // UP
			val += 0.01;
			console.log(val);
			$("#sell_price").val(val.toFixed(2));
			evt.preventDefault();
			break
		case 40: // DOWN
			val -= 0.01;
			if (val < 0)
			{
				val = 0.01;
			}
			console.log(val)
			$("#sell_price").val(val.toFixed(2));
			evt.preventDefault();
			break
		}
	}
}


function Refresh() {
	RefreshStockPool();
	RefreshOrderList();
}

$(document).ready(function() {
	Refresh()
	setInterval("Refresh()", 5000);
})
