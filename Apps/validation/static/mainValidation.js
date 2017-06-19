
/*DATATABLE*/

$(window).resize(function() {
  // change datatable height
  $('.dataTables_scrollBody').css('height', ($(window).height() - 300));
  // change map height
  $('#map').css('height', ($(window).height() - 100));  
});


$(document).ready( function () {

	// tooltip initialization
	  $('[data-toggle="tooltip"]').tooltip();

	// uncheck all checkbox
	$(".check").prop('checked', false);

	// dataTable
    	$('#table_id').DataTable({
    			responsive: true,
    			"lengthChange": false,
    			"sScrollY": ($(window).height() - 300),
		    	"pageLength": 50,
		        "oLanguage": {
		           "sSearch": "Rechercher",
		            "sInfo": "",
		            "sInfoEmpty": "",
		            "sInfoFiltered": "",
		            "sZeroRecords": "Aucune espèce trouvée",
			        "oPaginate": {
			           "sPrevious": "Précedent",
			           "sNext" : "Suivant"
					} 
				}
			})
    	});


  /*LEAFLET*/

 var selectLayer;
 var dictLayer = {};

 var originStyle = {
		    "color": "#3388ff",
		    "fill": true,
		    "fillOpacity": 0.2,
		    "weight":3
		};

var selectedStyle = {
		  'color':'#ff0000',
		   'weight':3
		};

 
 function generateLayerFromGeojson(observations){
 	currentGeojsonLayer = L.geoJson(observations, {
          pointToLayer: function (feature, latlng) {
/*          					var layer = L.circleMarker(latlng);
          					dictLayer[feature.properties.id_synthese] = layer;
          					return layer;*/
          					return L.circleMarker(latlng);
                           },
          onEachFeature: bindMarkers,
	   });
 	return currentGeojsonLayer;
 }


function bindMarkers(feature, layer){
	dictLayer[feature.properties.id_synthese] = layer;
	layer.on({
		click: function(e){
			if (selectLayer != undefined){
				selectLayer.setStyle(originStyle);
			}
				e.target.setStyle(selectedStyle);

				// higlight the row

				id_synthese = e.target.feature.properties.id_synthese;
				row = $("[idSynthese="+id_synthese+"]")
				$(row).siblings().removeClass('currentRow');
         		$(row).addClass('currentRow');
			selectLayer = e.target;
		}
	})
}


var baseMaps = {
            OpenStreetMap: L.tileLayer('http://{s}.tile.opencyclemap.org/cycle/{z}/{x}/{y}.png', {
                // tslint:disable-next-line:max-line-length
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, Tiles courtesy of <a href="http://hot.openstreetmap.org/" target="_blank">Humanitarian OpenStreetMap Team</a>'
            }),
            Satelite: L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v9/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoidGhlb2xlY2hlbWlhIiwiYSI6ImNpa29lODhvejAwYTl3MGxzZGY0aHc0NXIifQ.fEujW2fUlRuUk9PHfPdKIg', {
                // tslint:disable-next-line:max-line-length
                attribution: 'MapBox'
            }),
            OpenStreetMap2: L.tileLayer('http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
                // tslint:disable-next-line:max-line-length
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
            })
};

var currentGeoJson;
var map = L.map('map', {
	'center': [configuration.MAP.COORD_CENTER.Y, configuration.MAP.COORD_CENTER.X],
	'zoom': configuration.MAP.ZOOM_LEVEL,
	'layers': [baseMaps.OpenStreetMap]
});

L.control.layers(baseMaps).addTo(map);


  	// display geojson
  	  currentGeoJson = observations;
  	  currentGeoJsonLayer = generateLayerFromGeojson(currentGeoJson);
  	  currentGeoJsonLayer.addTo(map);
	  

     // interaction list - map 
      $('.search').click(function(){
      	// back to origin style
      	if (selectLayer != undefined){
	      	 selectLayer.setStyle(originStyle);
      	}

      	row = this.parentElement;
      	id_synthese = $(row).attr("idSynthese");
         $(row).siblings().removeClass('currentRow');
         $(row).addClass('currentRow');

        selectLayer = dictLayer[id_synthese];

        if (selectLayer != undefined) {
	        selectLayer.setStyle(selectedStyle);

	        if (selectLayer instanceof L.Polygon) {
	        	current_lat_lng = selectLayer._bounds._northEast;
	        }
	        else{
	        	current_lat_lng = selectLayer._latlng;
	        }
	        if(map.getZoom() > 13){
				map.setView(current_lat_lng);
			} else {
				map.setView(current_lat_lng, 13);
			}
  		}

  	});


function findInArray(tab_id, id_observation){	
  i = 0 ;
  while (i < tab_id.length && tab_id[i] != id_observation){
    i = i+1
  }
  return i == tab_id.length
}



function deletePoint(arrayDelete){
	console.log(arrayDelete);
      	
	    currentGeoJson.features = currentGeoJson.features.filter(function(point){
	    	return findInArray(arrayDelete, point.properties.id_synthese);

	    })
	    map.removeLayer(currentGeoJsonLayer);
	    currentGeoJsonLayer = generateLayerFromGeojson(currentGeoJson)
  	    currentGeoJsonLayer.addTo(map);
}


$('.validate').click(function(){
	row = this.parentElement;
	$(row).addClass("validate_ok")
	$(row).removeClass('currentRow');
    $(row).hide( "slow" );
    id = $(row).attr("idSynthese");
    protocole = $(row).attr("protocole");
	
	data = {'validate': [id], 'protocole': protocole}
	console.log(data);
	data = JSON.stringify(data)
	$.ajax({
	  type: "POST",
	  url: configuration.URL_APPLICATION+'validation/validate/',
	  contentType: 'application/json; charset=utf-8',
	  data: data,
	  dataType: "json"
	})
	idArray = [];
	idArray.push(id)
	deletePoint(idArray);
});

var id;
$('.delete').click(function(){
	row = this.parentElement;
	id = $(row).attr("idSynthese");
	protocole = $(row).attr("protocole");
	$('#confirmDelete').click(function(){
			$.ajax({
			  type: "GET",
			  url: configuration.URL_APPLICATION+"validation/delete/"+id+"/"+protocole
			})
		$('.modal').modal('hide');
		$(row).addClass("delete_ok");
		$(row).hide( "slow" );
		idArray = [];
		idArray.push(id);
		deletePoint(idArray);
	})		
});





// set de ID
var checkList = new Set();
$('.check').change(function(){	
	
	// enable or disable the validate button
	

		row = this.parentElement.parentElement;
		id = $(row).attr('idsynthese')
		if(this.checked){
			checkList.add(id)
		}else{
			checkList.delete(id)
		}
		if(checkList.size>0){
			$('#lauchValidateModal').removeClass('disabled')
			$('#lauchValidateModal').addClass('enable')
		}else{
			$('#lauchValidateModal').removeClass('enable')
			$('#lauchValidateModal').addClass('disabled')
		}
})



$('#globalValidate').click(function(){
	
	var rows = [];
	var checked = $( "input:checked" );
	var len = checked.length
	i = 0;
	while(i<len){
		rows.push(checked[i].parentElement.parentElement)
		i++
	}

	 rows.forEach(function(row){
	 	$('.modal').modal('hide');
	 	$(row).removeClass('currentRow');
	 	$(row).addClass("validate_ok")
	 	$(row).hide( "slow" );

	 })


	arrayCheckList = Array.from(checkList)
	jsonData = {'validate' : arrayCheckList, 'protocole': PROTOCOLE}
	jsonData = JSON.stringify(jsonData)
	$.ajax({
	  type: "POST",
	  url: configuration.URL_APPLICATION+"validation/validate/",
	  contentType: 'application/json; charset=utf-8',
	  data: jsonData,
	  dataType: "json"
	  
	}).done(function(response){
		deletePoint(response.id_synthese);
		console.log(checkList);
		//checkList.clear();
	})	


})
// fill the modal with the number of observations
$('#lauchValidateModal').click(function(){
	$('#insertHTML').html("Valider les "+ checkList.size+" observations selectionnées ?");
})

// cancel close the modal

$('.cancel').click(function(){
		$('.modal').modal('hide');
})



/*geojsonArray = geojsonArray.filter(function(id){
	return (deleteArray.find(id) != -1)
})*/