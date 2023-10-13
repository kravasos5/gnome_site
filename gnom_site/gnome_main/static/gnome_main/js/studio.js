document.addEventListener('DOMContentLoaded', function () {
    if (data.length === 0) {
        $('#graph-container').append($('<p>').text(g_title + ' не обнаружены'));
        $('#graph-container').css({
            'color': '#fff',
            'height': 'auto',
            'text-align': 'center'
        })
    } else if (data.length !== 0) {
        if (ld_indicator === false) {
            Highcharts.stockChart('graph-container', {
                title: {
                    text: '' + g_title,
                    style: {
                        color: '#fff'
                    }
                },

                navigator: {
                    series: {
                        accessibility: {
                            exposeAsGroupOnly: true
                        }
                    }
                },

                plotOptions: {
                    series: {
                        color: 'red' // Установите желаемый цвет линии
                    },
                    area: {
                        fillColor: {
                            linearGradient: { x1: 0, x2: 1, y1: 0, y2: 1 },
                            stops: [
                                [0, 'rgba(245, 23, 1, 0.7)'], // start
                                [1, 'rgba(245, 23, 1, 0.2)'] // end
                            ]
                        }
                    }
                },

                rangeSelector: {
                    buttons: [{
                        type: 'month',
                        count: 1,
                        text: '1m',
                        title: '1 месяц'
                    }, {
                        type: 'month',
                        count: 3,
                        text: '3m',
                        title: '3 месяца'
                    }, {
                        type: 'all',
                        count: 1,
                        text: 'All'
                    }],
                    selected: 1,
                },

                series: [{
                    name: '' + g_title,
                    type: 'area',
                    data: data,
                    gapSize: null,
                    tooltip: {
                        valueDecimals: 2
                    },
                    threshold: null
                }]
            });

        } else if (ld_indicator === true) {
            let series_data = []
            for (let i = 0; i < data.length; i++) {
                series_data.push(
                {
                    name: data[i]['name'],
                    y: data[i]['y'],
                    count: data[i]['count']
                })
                if (data[i]['y'] > 50) {
                    series_data.slice(-1).sliced = true
                    series_data.slice(-1).selected = true
                };
            };
            Highcharts.chart('graph-container', {
                chart: {
                    plotBackgroundColor: null,
                    plotBorderWidth: null,
                    plotShadow: false,
                    type: 'pie'
                },
                title: {
                    text: '' + g_title,
                    align: 'left'
                },
                tooltip: {
                    pointFormat: '{series.name}: <b>{point.count}</b>'
                },
                accessibility: {
                    point: {
                        valueSuffix: '%'
                    }
                },
                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        dataLabels: {
                            enabled: true,
                            format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                        }
                    }
                },
                series: [{
                    name: 'Likes',
                    colorByPoint: true,
                    data: series_data
                }]
            });
        };
    };
});
