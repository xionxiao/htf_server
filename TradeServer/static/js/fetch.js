var market_host = "http://" + window.location.hostname  + ":80";

(function Init() {
	g_stock_1 = '600036';
	g_stock_2 = '000625';

	var num = ["十","九","八","七","六","五","四","三","二","一"];
	pr = [];
	qu = [];
	for (var i=0; i<20; i++) {
		if (i<10) {
			pr.push("卖"+num[i]+"价");
			qu.push("卖"+num[i]+"量");
		} else {
			pr.push("买"+num[19-i]+"价");
			qu.push("买"+num[19-i]+"量");
		}
	}
}());

function RefreshQuote10() {
	//console.log("Refresh Quote", g_stock_1, g_stock_2);
	$.get(market_host + "/query",{"catalogues":"quote10", "stocks":g_stock_1+','+g_stock_2}, function(data) {
		var obj = eval("("+data+")");
		//console.log(obj);
		if (obj['error'] !== undefined) {
			return;
		}
		fill_quote_table("#left-quote", obj["quote10"][0]);
		fill_quote_table("#right-quote", obj["quote10"][1]);
		RefreshQuote10()
	})
}

function RefreshTransactionDetail() {
	//console.log("Refresh Transaction");
	$.get(market_host + "/query",{"catalogues":"transaction_detail", "stock":g_stock_1}, function(data) {
		var obj = eval("("+data+")");
		//console.log(obj);
		if (obj['error'] !== undefined) {
			console.log(obj['error']);
			return;
		}
		fill_transaction_table("#left-transaction", obj["transaction_detail"]);
		RefreshTransactionDetail()
	})
}

function fill_quote_table(id, quote) {
	$(id).find("#name").text(quote["名称"]);
	$(id).find("#code").text(quote["代码"]);
	var table = $(id).find("table").eq(0);
	var rows = table.find('tr');
	var color = "blue";
	for (var i=0; i<10; i++) {
		var tr = rows.eq(i);
		var td = tr.find('td');
		td.eq(1).text(quote[pr[i]].slice(0,-4)).attr("align","right").css('color','blue');
		td.eq(2).text(quote[qu[i]]).attr("align","right").css('color','black');
	}
	for (i=10; i<20; i++) {
		var tr = rows.eq(i);
		var td = tr.find('td');
		td.eq(1).text(quote[pr[i]].slice(0,-4)).attr("align","right").css('color','blue');
		td.eq(2).text(quote[qu[i]]).attr("align","right").css('color','black');
	}
}

function fill_transaction_table(id, data) {
	var table = $(id).find("table").eq(0);
	var rows = table.find('tr');
	for (var i=0; i<20; i++) {
		var tr = rows.eq(i);
		var td = tr.find('td');
		if ( !data || !data[i]) {
			td.eq(3).text("__:__:__");
			td.eq(0).text("_____");
			td.eq(1).text("____");
			td.eq(2).text("_");
		} else {
			if (data[i]["性质"] == 'S')
				tr.css('color','darkgreen')
			else
				tr.css('color','red')
			td.eq(3).text(data[i]["成交时间"]).css('color','gray');
			td.eq(0).text(data[i]["价格"].slice(0,-4));
			td.eq(1).text(data[i]["成交量"].split('.')[0]);
			td.eq(2).text(data[i]["性质"]);
		}
	}
}

function Refresh() {
	RefreshQuote10()
	RefreshTransactionDetail()
}

function clearInput(evt) {
	$("#left-sell-price").val("");
	$("#left-buy-price").val("");
	$("#right-sell-price").val("");
	$("#right-buy-price").val("");
	$("#left-sell-shares").val("");
	$("#left-buy-shares").val("");
	$("#right-sell-shares").val("");
	$("#right-buy-shares").val("");
}