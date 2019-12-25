$(function(){
	Highcharts.setOptions({
        global: {
            useUTC: false
        },
        chart : {
                marginTop: 3,
                marginRight: 1,
                marginLeft: 1,
				spacing: [1,1,1,1],
                //panning: true,
                //panKey: 'shift',
                //zoomType: 'x',
			},
        rangeSelector : {
                enabled : false,
            },
        title : {
            text: null,
        },
        navigator : {
            enabled : false
        },
        legend : {
        	enabled: false
        },
        scrollbar : {
            enabled : false
        },
        credits : {
        	enabled : false
        },
        legend : {
        	enabled : false
        },
    });
}());

function drawCandleStickChart() {
    var data = []
    for (var i=0; i<sh000001.length; i++) {
        var x = sh000001[i];
        var d = Date.parse(x['date'].substr(0, 4)+'/'+x['date'].substr(4, 2) + '/' + x['date'].substr(6, 2));
        var open = parseFloat(x['open']);
        var high = parseFloat(x['high']);
        var low = parseFloat(x['low']);
        var close = parseFloat(x['close']);
        data.push([d, open, high, low, close])
    }

    function by_date(a, b) {
        return parseInt(a[0]) - parseInt(b[0]);
    }

    var datae = data.sort(by_date);
    // create the chart
    $('#candle-stick-chart').highcharts('StockChart', {
        rangeSelector : {
            selected : 0,
            inputEnabled : false,
        },

        title : {
            enabled : false
        },

        navigator : {
            enabled : false,
        },

        scrollbar : {
            enabled : false
        },
        
        series : [{
            type : 'candlestick',
            name : 'AAPL Stock Price',
            data : datae,
            dataGrouping : {
                enabled : false,
                units : [
                    [
                        'day', // unit name
                        [1], // allowed multiples
                    ], [
                        'week',
                        [1, 2, 3, 4, 6],
                    ],
                ]
            },
            colors : [/*'#2f7ed8'*/'red', 'red', 'red', 'red', '#1aadce', 
   '#492970', '#f28f43', '#77a1e5', '#c42525', '#a6c96a'],
        }]
    });
}

function drawMinuteChart(mPrice, mVolume, mAxis) {
    console.log(mAxis);
	$('#minute-chart').highcharts({
		tooltip: {
            valueDecimals: 2,
            formatter: function() {
            	var newDate = new Date();
                var i = this.x;
                i < 120 ? newDate.setHours(9, i+30, 0, 0) : newDate.setHours(13, i-120, 0, 0);
                mm = Highcharts.dateFormat("%H:%M", newDate);
                return  '<b">' + mm + "</b><br>price: " + this.y
            },
            crosshairs: true,
        },

        series : [{
        	type : 'line',
            data : mPrice,
            color: 'red',
            lineWidth: 1,
        }],

        xAxis : [{
        	lineWidth: 1,
        	minPadding: 0,
        	maxPadding: 0,
			min: 0,
			max: 240,
            startOnTick: true,
            endOnTick: true,
        	gridLineWidth: 1,
        	gridLineDashStyle: "dash",
        	minorGridLineWidth: 1,
            minorTickInterval: 120,
        	minorTickLength: 0,
            tickInterval: 60,
        	tickLength: 0,
        	labels : {
        		enabled : false,
        	},
        },{
        	lineWidth: 1,
        	opposite: true,
        	title : {
        		enabled: false,
        	},
        }],

        yAxis : [{
        	lineWidth: 1,
        	tickAmount: 9,
            //tickPixelInterval: 25,
			tickPositions: mAxis,
            plotLines: [{
                width: 1,
                color: "#E0E0E0",
                value: mAxis[4],
            }],
        	gridLineDashStyle: "dash",
        	labels : {
        		enabled: true,
        		align : 'left',
        		formatter : function(){
                    return this.value;
                    /*
                    if(this.value == 16.84)
                        return 16.84
                    return ((this.value-16.84)/16.84*100) + "%";
                    */
                },
        		x: 5,
        		y: -5,
        		step: 1,
        	},
        },{
        	lineWidth: 1,
        	opposite: true,
        }]
    });

	$('#minute-chart-volume').highcharts({
		tooltip: {
            valueDecimals: 2,
            formatter: function() {
            	var newDate = new Date();
                var i = this.x;
                i < 120 ? newDate.setHours(9, i+30, 0, 0) : newDate.setHours(13, i-120, 0, 0);
                mm = Highcharts.dateFormat("%H:%M", newDate);
                return  mm + "<br>volume: " + this.y
            },
            crosshairs: true,
        },

        series : [{
        	type : 'column',
            data : mVolume,
            borderWidth: 0,
            pointWidth: 1,
            pointPlacement: 'on',
            color: 'green',
            tooltip: {
                valueDecimals: 2
            },
            keys: ['y', 'color'],
        }],

        xAxis : [{
        	lineWidth: 1,
        	minPadding: 0,
        	maxPadding: 0,
        	startOnTick: true,
        	endOnTick: true,
			min:0,
			max:240,
        	gridLineWidth: 1,
        	gridLineDashStyle: "dash",
        	minorGridLineWidth: 1,
        	minorTickLength: 0,
            tickInterval: 60,
            minorTickInterval: 120,
            tickLength: 0,
        	labels : {
        		enabled : true,
                formatter: function() {
                    var newDate = new Date();
                    var i = this.value;
                    i < 120 ? newDate.setHours(9, i+30, 0, 0) : newDate.setHours(13, i-120, 0, 0);
                    return Highcharts.dateFormat("%H:%M", newDate);
                }
        	},
        },{
        	lineWidth: 1,
        	opposite: true,
        	title : {
                enabled: false,
        	},
        }],

        yAxis : [{
        	lineWidth: 1,
        	title : {
        		enabled: false,
        	},
            tickAmount : 5,
            tickPixelInterval: 25,
            gridLineDashStyle: "dash",
            labels : {
                enabled: true,
                align: 'left',
                formatter : function(){
                    return this.value / 1000 + 'k';
                },
                x: 5,
                y: -5,
            },
        },{
        	lineWidth: 1,
        	opposite: true,
        	title : {
        		enabled: false,
        	},
        	
        }]
    });
}