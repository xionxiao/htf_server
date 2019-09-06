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

function drawMinuteChart(mPrice, mVolume) {
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
            tickPixelInterval: 25,
            tickPositions: [16.42,16.56,16.70,16.84,16.98,17.12,17.26,17.4,],
            plotLines: [{
                width: 1,
                color: "#E0E0E0",
                value: 16.84,
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