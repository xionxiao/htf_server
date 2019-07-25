var host = "http://" + window.location.host;

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
	$.get(host + "/query",{"catalogues":"quote10", "stocks":g_stock_1+','+g_stock_2}, function(data) {
		var obj = eval("("+data+")");
		console.log(obj);
		if (obj['error'] !== undefined) {
			return;
		}
		fill_quote_table("#left-quote", obj["quote10"][0]);
		fill_quote_table("#right-quote", obj["quote10"][1]);
	})
}

function RefreshTransactionDetail() {
	//console.log("Refresh Transaction");
	$.get(host + "/query",{"catalogues":"transaction_detail", "stock":g_stock_1}, function(data) {
		var obj = eval("("+data+")");
		console.log(obj);
		if (obj['error'] !== undefined) {
			console.log(obj['error']);
			return;
		}
		fill_transaction_table("#left-transaction", obj["transaction_detail"]);
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
		if (!data[i]) {
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

function KeyShortcuts(evt) {
	if (evt.altKey) {
		switch (evt.keyCode)
		{
		case 49: // Alt+1
			var item = $("#left-sell-price");
			item.val($("#left-quote-table tr:eq(10) td:eq(1)").text());
			item.focus()
			break;
		case 50:  // Alt+2
			var item = $("#left-buy-price");
			item.val($("#left-quote-table tr:eq(9) td:eq(1)").text());
			item.focus()
			break;
		case 51:  // Alt+3
			var item = $("#right-sell-price");
			item.val($("#right-quote-table tr:eq(10) td:eq(1)").text());
			item.focus()
			break;
		case 52:  // Alt+4
			var item = $("#right-buy-price");
			item.val($("#right-quote-table tr:eq(9) td:eq(1)").text());
			item.focus()
			break;
		}
	}
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

function AmountUp(evt) {
	var value = parseInt($(this).val());
	if (isNaN(value))
		value = 0;
	value += 100;
	$(this).val(value);
}

function AmountDown(evt) {
	var value = parseInt($(this).val());
	if (isNaN(value) || value <= 100)
		value = 200;
	value -= 100;
	$(this).val(value);
}

function PriceUp(evt) {
	var value = parseFloat($(this).val());
	if (isNaN(value))
		value = 0.00;
	value += 0.01;
	$(this).val(value.toFixed(2));
}

function PriceDown(evt) {
	var value = parseFloat($(this).val());
	if (isNaN(value) || value <= 0.01)
		value = 0.02;
	value -= 0.01;
	$(this).val(value.toFixed(2));
}

$(document).ready(function() {
	$('input').keyup(function(evt){
		if(evt.keyCode == 13) {// Enter
			$(this).trigger("OnEnter");
		}
		if(evt.keyCode == 38) {// Up
			$(this).trigger("OnKeyUp");
		}
		if(evt.keyCode == 40) {// Down
			$(this).trigger("OnKeyDown");
		}
		if(evt.keyCode == 27) {// ESC
			$(this).trigger("OnEsc");
		}
	});

	// 价格
	$("#left-sell-price").bind('OnKeyUp', PriceUp);
	$("#left-sell-price").bind('OnKeyDown', PriceDown);
	
	$("#left-buy-price").bind('OnKeyUp', PriceUp);
	$("#left-buy-price").bind('OnKeyDown', PriceDown);
	
	$("#right-sell-price").bind('OnKeyUp', PriceUp);
	$("#right-sell-price").bind('OnKeyDown', PriceDown);
	
	$("#right-buy-price").bind('OnKeyUp', PriceUp);
	$("#right-buy-price").bind('OnKeyDown', PriceDown);

	// 股数
	$("#left-sell-shares").bind('OnKeyUp', AmountUp);
	$("#left-sell-shares").bind('OnKeyDown', AmountDown);
	
	$("#left-buy-shares").bind('OnKeyUp', AmountUp);
	$("#left-buy-shares").bind('OnKeyDown', AmountDown);
	
	$("#right-sell-shares").bind('OnKeyUp', AmountUp);
	$("#right-sell-shares").bind('OnKeyDown', AmountDown);
	
	$("#right-buy-shares").bind('OnKeyUp', AmountUp);
	$("#right-buy-shares").bind('OnKeyDown', AmountDown);


	$('#left-input').bind('OnEnter', function(evt){
		g_stock_1 = $('#left-input').val();
		Refresh();
	});

	$('#right-input').bind('OnEnter', function(evt) {
		g_stock_2 = $('#right-input').val().slice(0,6);
		Refresh();
	});

	Refresh()
	setInterval("Refresh()", 5000);
})