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
		params = {"type":"frompool", "stock":stock, "price":price, "share":shares};
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
		RefreshStockPool();
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
	c1 = Date.parse(today + t1["委托时间"]);
	c2 = Date.parse(today + t2["委托时间"]);
	return c2 - c1
}

function RefreshOrderList() {
	console.log("Refresh Order List")
	$.get(trade_host + "/query",{"catalogues":"orderlist"}, function(data) {
		obj = eval("("+data+")");
		//console.log(JSON.stringify(obj));
		obj = obj.orderlist;
		obj_array = []
		for (i in obj) {
			obj_array.push(obj[i]);
		}
		obj = obj_array.sort(compareDate);
		$("#order-list table tbody").empty();
		item_str = "<tr> <th>时间</th> <th>单号</th> <th>名称</th> <th>代码</th> <th>价格</th> <th>数量</th> <th>买卖</th> </tr>"
		for ( i in obj) {
			var color = 'blue'
			if (obj[i]["买卖标志"] == "买入担保品") {
					var color = 'red'
			} 
			item_str += "<tr id="+i+'" style="color:' + color +';"' + ">";
			item_str += "<td>"+obj[i]["委托时间"]+"</td>";
			item_str += "<td>"+obj[i]["合同编号"]+"</td>";
			item_str += "<td>"+obj[i]["证券名称"]+"</td>";
			item_str += "<td>"+obj[i]["证券代码"]+"</td>";
			item_str += "<td>"+obj[i]["委托价格"]+"</td>";
			item_str += "<td>"+obj[i]["委托数量"]+"</td>";
			item_str += "<td>"+obj[i]["买卖标志"]+"</td>";
			item_str += "</tr>";
		}
		$("#order-list table tbody").append(item_str);
		//RefreshOrderList();
	})
}

function RefreshPosition() {
	console.log("Refresh Stock Position")
	$.get(trade_host + "/query",{"catalogues":"position"}, function(data) {
		obj = eval("("+data+")");
		//console.log(obj.position)
		//console.log(JSON.stringify(obj));
		obj = obj.position
		$("#stock-position table tbody").empty();
		item_str = "<tr> <th>名称</th> <th>代码</th> <th>可卖</th> <th>持仓均价</th> <th>持仓数量</th> <th>参考盈亏</th></tr>"
		for ( i in obj) {
			var color = 'blue'
			item_str += "<tr id="+i+'" style="color:' + color +';"' + ">";
			item_str += "<td>"+obj[i]["证券名称"]+"</td>";
			item_str += "<td>"+obj[i]["证券代码"]+"</td>";
			item_str += "<td>"+obj[i]["可卖数量"]+"</td>";
			item_str += "<td>"+obj[i]["盈亏成本价"]+"</td>";
			item_str += "<td>"+obj[i]["证券数量"]+"</td>";
			item_str += "<td>"+obj[i]["浮动盈亏"]+"</td>";
			item_str += "</tr>";
		}
		$("#stock-position table tbody").append(item_str);
		//RefreshOrderList();
	})
}

function ClearResultPanel() {
	console.log("Clear Result Panel");
	$("#result-panel .panel-body").empty();
}
