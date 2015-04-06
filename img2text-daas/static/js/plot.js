$(function() {
	$('#upload_button').click(function(e) {
        var form_data = new FormData($('#upload_form')[0]);
        console.log(form_data);
        e.preventDefault();

        $.ajax({
            type: 'POST',
            url: '/upload',
            data: form_data,
            contentType: false,

            cache: false,
            processData: false,
            async: true,
            beforeSend: function() {
                $("#uploading").show();
                $("#plot").empty();
                $("perp").hide();
            },
            success: function(data){
            	$("#uploading").hide();
            	plot(data);
            	$("#perp").show();
            },
            error: function(){
                alert('Upload failed!');
                $("#uploading").hide();
            }
        });
	});

	$('#perplexity-button').click(function(e) {
		e.preventDefault();
		var perp = $('#perplexity-selector').val();
		console.log(perp);
		$.ajax({
            type: 'GET',
            url: '/plot',
            data: {perplexity: perp},
            processData: true,
            async: true,
            beforeSend: function() {
                $("#uploading").show();
                $("#plot").empty();
                $("perp").hide();
            },
            success: function(data){
            	$("#uploading").hide();
            	plot(data);
            	$("#perp").show();
            },
            error: function(){
                alert('Upload failed!');
                $("#uploading").hide();
            }
        });

	});

});


function perpUpdate(perp) {
	document.querySelector('#perp-value').value = perp;
};

function makeFileList() {
            var input = document.getElementById("file");
            var tbl = document.getElementById("fileList");
            while (tbl.hasChildNodes()) {
                tbl.removeChild(tbl.firstChild);
            }
            for (var i = 0; i < input.files.length; i++) {   
                $("#filesTxt").show();
                $("#btnUpdDiv").show();
                var li = document.createElement("tr");
                li.innerHTML = ("<td>"+input.files[i].name+"</td>");
                tbl.appendChild(li);
            }
            if(!tbl.hasChildNodes()) {
                $("#btnUpdDiv").hide();
                var li = document.createElement("tr");
                li.innerHTML = ("<td>No files Selected</td>");
                tbl.appendChild(li);
            }
        };

// $(function() {
//     $('#query_btn').click(function(event) {
//         event.preventDefault();
        
//         $.ajax({
//             type: 'GET',
//             url: '/plot',
//             dataType: 'json',
//             cache: false,
//             processData: false,
//             async: true,
//             beforeSend: function() {
//               $("#plot").empty();
//             },
//             success: function(data) {
//             	plot(data);
//               	console.log(data);
//             },

//         });
//     });
// });


function plot(data){

	var w = 800,
		h = 600;

	var padding = 40;

	var img_data = data.images;


	var txt_data = data.texts;


	var xScale = d3.scale.linear()
					.domain([d3.min(img_data, function(d) { return d.xy[0];}), 
						d3.max(img_data, function(d) { return d.xy[0];})])
					.range([padding, w - padding]);
	var yScale = d3.scale.linear()
					.domain([d3.min(img_data, function(d) { return d.xy[1];}), 
						d3.max(img_data, function(d) { return d.xy[1];})])
					.range([padding, h - padding]);

	var svgContainer = d3.select("#plot").append("svg")
				.attr("width", w)
				.attr("height", h)
				.style("border", "1px solid #B8D3E5")
				.append("g")
				.call(d3.behavior.zoom().x(xScale).y(yScale).scaleExtent([-1, 8]).on("zoom", zoom));

	svgContainer.append("rect") //this is necessary to enable the zoom
			    .attr("class", "overlay")
			    .attr("width", w)
			    .attr("height", h);

	var img_tooltip = d3.select("#plot")
				.append("img")
				.attr("id", "img_tooltip")
				.attr("width", "400")
				.attr("height", "300")
				.classed("hidden", true);

	var txt_tooltip = d3.select("#plot").append("text")
				.attr("id", "txt_tooltip")

	var img_points = svgContainer.selectAll("image")
				.data(img_data)
				.enter()
				.append("image")
				// .attr("x", function (d) {return xScale(d.x);})
				// .attr("y", function (d) {return yScale(d.y);})
				.attr("xlink:href", function (d) {return d.url;})
				.attr("width", "30px")
				.attr("height", "20px")
				.attr("opacity", .7)
				.attr("transform", transform)
				.on("mouseover", function (d) {
					//get x/y values of the point
					// var xPosition = parseFloat(d3.select(this).attr("x"));
					// var yPosition = parseFloat(d3.select(this).attr("y"));
					// var xPosition = w;
					// var yPosition = padding*2;
					img_tooltip
					   .attr("src", d.url)
					   .classed("hidden", false);
				})
				.on("mouseout", function (d) {
					img_tooltip.classed("hidden", true);
				});

	var txt_points = svgContainer.selectAll("text")
					.data(txt_data)
					.enter()
					.append("text")
					.text(function (d) {return d.label;})
					.attr("text-anchor", "middle")
					.attr("font-weight", "bold")
					// .attr("font-size", "18px")
					.attr("transform", transform)
					.on("mouseover", function (d) {
						// var xPosition = w;
						// var yPosition = padding*2;
						txt_tooltip
								// .style("left", xPosition + "px")
								// .style("top", yPosition + "px")
								.text(d.text)
								.attr("text-anchor", "middle")
								.classed("hidden", false);
					})
					.on("mouseout", function(){
						txt_tooltip.classed("hidden", true);
					});
				


	function zoom() {
		img_points.attr("transform", transform);
		txt_points.attr("transform", transform);
	};

	function transform(d) {
		return "translate(" + xScale(d.xy[0]) + "," + yScale(d.xy[1]) + ")";
	};

};

