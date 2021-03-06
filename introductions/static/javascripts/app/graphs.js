$(document).ready(function () {
    // slider
    $("#feedback-stats").noUiSlider({
        range: [1, 1000],
        start: 200,
        handles: 1,
        step: 1
    }).noUiSlider("disabled",true);

    //slider-small
    $(".slider-small").noUiSlider({
        range: [1, 1000],
        start: 400,
        handles: 1,
        step: 1
    }).noUiSlider("disabled",true);
 });

var lineChartData = { labels : ["","","","","","","", "", ""],
    datasets : [

        {
            fillColor : "rgba(252,235,171,0.5)",
            strokeColor : "rgba(248,205,46,1)",
            pointColor : "rgba(248,205,46,1)",
            pointStrokeColor : "#fff",
            data : [48, 48, 26, 50, 48, 51, 48, 56, 50]
        }
    ]

}


var lineChartDefaults = {
    //Boolean - If we show the scale above the chart data
    scaleOverlay : false,
    //Boolean - If we want to override with a hard coded scale
    scaleOverride : false,
    //** Required if scaleOverride is true **
    //Number - The number of steps in a hard coded scale
    scaleSteps : null,
    //Number - The value jump in the hard coded scale
    scaleStepWidth : null,
    //Number - The scale starting value
    scaleStartValue : null,
    //String - Colour of the scale line
    scaleLineColor : "rgba(0,0,0,.0)",
    //Number - Pixel width of the scale line
    scaleLineWidth : 1,
    //Boolean - Whether to show labels on the scale
    scaleShowLabels : false,
    //Interpolated JS string - can access value
    scaleLabel : "<%=value%>",
    //String - Scale label font declaration for the scale label
    scaleFontFamily : "'Arial'",
    //Number - Scale label font size in pixels
    scaleFontSize : 12,
    //String - Scale label font weight style
    scaleFontStyle : "normal",
    //String - Scale label font colour
    scaleFontColor : "#666",
    ///Boolean - Whether grid lines are shown across the chart
    scaleShowGridLines : false,
    //String - Colour of the grid lines
    scaleGridLineColor : "rgba(0,0,0,.05)",
    //Number - Width of the grid lines
    scaleGridLineWidth : 1,
    //Boolean - Whether the line is curved between points
    bezierCurve : false,
    //Boolean - Whether to show a dot for each point
    pointDot : true,
    //Number - Radius of each point dot in pixels
    pointDotRadius : 3,
    //Number - Pixel width of point dot stroke
    pointDotStrokeWidth : 1,
    //Boolean - Whether to show a stroke for datasets
    datasetStroke : true,
    //Number - Pixel width of dataset stroke
    datasetStrokeWidth : 2,
    //Boolean - Whether to fill the dataset with a colour
    datasetFill : true,
    //Boolean - Whether to animate the chart
    animation : true,
    //Number - Number of animation steps
    animationSteps : 60,
    //String - Animation easing effect
    animationEasing : "easeOutQuart",
    //Function - Fires when the animation is complete
    onAnimationComplete : null
};
