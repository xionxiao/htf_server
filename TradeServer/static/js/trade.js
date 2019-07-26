var trade_host = "http://" + window.location.host;

function ExcuteBuyStock(id) {
	console.log("Buy");
	price = parseFloat($(id+"-buy-price").val());
	shares = parseFloat($(id+"-buy-shares").val());
	stock = $(id+"-stock-code").text();
	console.log(stock)
	if (price && shares) {
		params = {"stock":stock, "price":price, "share":shares};
		$.post(trade_host + "/buy",params, function(data){
			console.log(data);
			obj = eval("("+data+")");
			console.log(obj);
			if (obj.error) {
				text = obj.error;
			}
			if (obj.result) {
				text = obj.result["合同编号"];
			}
			$("#return-info .panel-body").prepend(text +  "<br>");
		});
	}
}

function ExcuteSellStock(id) {
	console.log("Sell");
	price = parseFloat($(id+"-sell-price").val());
	shares = parseFloat($(id+"-sell-shares").val());
	stock = $(id+"-stock-code").text();
	console.log(stock)
	if (price && shares) {
		params = {"stock":stock, "price":price, "share":shares};
		$.post(trade_host + "/sell",params, function(data){
			console.log(data);
			obj = eval("("+data+")");
			console.log(obj)
			if (obj.error) {
				text = obj.error;
			}
			if (obj.result) {
				text = obj.result["合同编号"];
			}
			$("#return-info .panel-body").prepend(text +  "<br>");
		});
	}
}

function ExcuteShortStock(id) {
	console.log("Short");
	price = parseFloat($(id+"-short-price").val());
	shares = parseFloat($(id+"-short-shares").val());
	stock = $(id+"-stock-code").text();
	console.log(stock)
	if (price && shares) {
		params = {"stock":stock, "price":price, "share":shares};
		$.post(trade_host + "/short",params, function(data){
			console.log(data);
			obj = eval("("+data+")");
			console.log(obj)
			if (obj.error) {
				text = obj.error;
			}
			if (obj.result) {
				text = obj.result["合同编号"];
			}
			$("#return-info .panel-body").prepend(text +  "<br>");
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
	$.get(trade_host + "/query",{"catalogues":"stockpool"}, function(data) {
		obj = eval("("+data+")");
		console.log(obj)
		$("#stock-pool .panel-body table tbody").empty();
		item_str = "";
		var color = "gray";
		obj =  obj["stockpool"]
		for ( i in obj) {
			item_str += "<tr id="+obj[i]+'" style="color:' + color +';"' + ">";
			item_str += "<td>"+i+"</td>";
			//item_str += "<td>"+obj[i]["证券名称"]+"</td>";
			//item_str += "<td>"+obj[i]["涨停价"]+"</td>";
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
