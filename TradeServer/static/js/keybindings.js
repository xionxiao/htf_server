// 全局快捷键
function KeyShortcuts(evt) {
	// 组合键
	if (evt.altKey) {
		switch (evt.keyCode)
		{
		case 49: // Alt+1
			var item = $("#left-short-price");
			item.val($("#left-quote-table tr:eq(10) td:eq(1)").text());
			item.focus()
			break;
		case 50:  // Alt+2
			var item = $("#left-buy-price");
			item.val($("#left-quote-table tr:eq(9) td:eq(1)").text());
			item.focus()
			break;
		case 51:  // Alt+3
			var item = $("#left-sell-price");
			item.val($("#left-quote-table tr:eq(10) td:eq(1)").text());
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

(function(){
	

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

	// 绑定输入框消息
	function BindInputBoxMessage() {
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
	}

	$(document).ready(function() {
		// 全局热键
		$("body").onkeyUp = KeyShortcuts

		// 绑定输入框消息
		BindInputBoxMessage();

		// 交易
		$('#left-buy-price').bind('OnEnter', function(evt) {
			ExcuteBuyStock("#left");
		});
		$('#left-buy-shares').bind('OnEnter', function(evt) {
			ExcuteBuyStock("#left");
		});
		/*
		$('#right-buy-price').bind('OnEnter', function(evt) {
			ExcuteBuyStock("#right");
		});
		$('#right-buy-shares').bind('OnEnter', function(evt) {
			ExcuteBuyStock("#right");
		});
		*/
		$('#left-sell-price').bind('OnEnter', function(evt) {
			ExcuteSellStock("#left");
		});
		$('#left-sell-shares').bind('OnEnter', function(evt) {
			ExcuteSellStock("#left");
		});
		/*
		$('#right-buy-price').bind('OnEnter', function(evt) {
			ExcuteBuyStock("#right");
		});
		$('#right-buy-shares').bind('OnEnter', function(evt) {
			ExcuteBuyStock("#right");
		});
		*/

		// 行情
		$('#left-input').bind('OnEnter', function(evt){
			Refresh();
		});

		$('#right-input').bind('OnEnter', function(evt) {
			Refresh();
		});

		// 调整价格
		$("#left-sell-price").bind('OnKeyUp', PriceUp);
		$("#left-sell-price").bind('OnKeyDown', PriceDown);
		
		$("#left-buy-price").bind('OnKeyUp', PriceUp);
		$("#left-buy-price").bind('OnKeyDown', PriceDown);
		
		$("#right-sell-price").bind('OnKeyUp', PriceUp);
		$("#right-sell-price").bind('OnKeyDown', PriceDown);
		
		$("#right-buy-price").bind('OnKeyUp', PriceUp);
		$("#right-buy-price").bind('OnKeyDown', PriceDown);

		// 调整股数
		$("#left-sell-shares").bind('OnKeyUp', AmountUp);
		$("#left-sell-shares").bind('OnKeyDown', AmountDown);
		
		$("#left-buy-shares").bind('OnKeyUp', AmountUp);
		$("#left-buy-shares").bind('OnKeyDown', AmountDown);
		
		$("#right-sell-shares").bind('OnKeyUp', AmountUp);
		$("#right-sell-shares").bind('OnKeyDown', AmountDown);
		
		$("#right-buy-shares").bind('OnKeyUp', AmountUp);
		$("#right-buy-shares").bind('OnKeyDown', AmountDown);

		fill_transaction_table("#left-transaction");
		fill_transaction_table("#right-transaction");

		RefreshTransactionDetail();
		RefreshQuote10();
		//Refresh()
		//setInterval("Refresh()", 5000);
	});
})();
