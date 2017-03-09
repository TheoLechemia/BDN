
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
	  console.log('tooltip it')

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

 console.log(observations)
 
 function generateLayerFromGeojson(observations){
 	currentGeojsonLayer = L.geoJson(observations, {
          pointToLayer: function (feature, latlng) {
                           return L.circleMarker(latlng);
                           },
          onEachFeature: bindMarkers,
	   });
 	return currentGeojsonLayer;
 }


function bindMarkers(features, layer){
	layer.on({
		click: function(e){
			if (selectLayer != undefined){
				selectLayer.setStyle({
					color: '#3388ff',
	            	fillColor: '#3388ff'
				})
			}
				e.target.setStyle({
					color: '#ff0000',
		            fillColor: '#ff0000'
				})

				// higlight the row

				id_synthese = e.target.feature.properties.id_synthese;
				row = $("[idSynthese="+id_synthese+"]")
				$(row).siblings().removeClass('currentRow');
         		$(row).addClass('currentRow');

			selectLayer = e.target;
		}
	})
}


var currentGeoJson;
var map = L.map('map').setView([16.2412500, -61.5361400],11 );
L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v9/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoidGhlb2xlY2hlbWlhIiwiYSI6ImNpa29lODhvejAwYTl3MGxzZGY0aHc0NXIifQ.fEujW2fUlRuUk9PHfPdKIg').addTo(map);


  	// display geojson
  	  currentGeoJson = observations;
  	  currentGeoJsonLayer = generateLayerFromGeojson(currentGeoJson);
  	  currentGeoJsonLayer.addTo(map);
	

     // interaction list - map 
      $('.search').click(function(){
      	console.log('click')
      	// back to origin style
      	if (selectLayer != undefined){
	      	 selectLayer.setStyle({
	            color: '#3388ff',
	            fillColor: '#3388ff'
	        });
      	}

      	row = this.parentElement;
      	id_synthese = $(row).attr("idSynthese");
         $(row).siblings().removeClass('currentRow');
         $(row).addClass('currentRow');
        var id_observation = $(this).attr('idSynthese');
        p = (currentGeoJsonLayer._layers);
        
        for (var key in p) {
          if (p[key].feature.properties.id_synthese == id_synthese){
            selectLayer = p[key];
			}
          }
         //selectLayer.openPopup();

        if (selectLayer != undefined) {
	        selectLayer.setStyle({
	            color: '#ff0000',
	            fillColor: '#ff0000'
	        });
	        if(map.getZoom() > 12){
				map.setView(selectLayer._latlng);
			} else {
				map.setView(selectLayer._latlng, 12);
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
	    	//return (idArray.find(point.properties.id_synthese) != -1);
	    	return findInArray(arrayDelete, point.properties.id_synthese);
/*	    	return arrayDelete.find(function(del){
	    		return del != point.properties.id_synthese
	    	})*/
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
	
	data = {'validate': id}
	data = JSON.stringify(data)
	$.ajax({
	  type: "POST",
	  url: URL_APPLICATION+'validation/validate',
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
	$('#confirmDelete').click(function(){
			$.ajax({
			  type: "GET",
			  url: URL_APPLICATION+"validation/delete/"+id
			})
		$('.modal').modal('hide');
		$(row).addClass("delete_ok");
		$(row).hide( "slow" );
		arrayID = [];
		arrayID.push(id);
		deletePoint(arrayID);
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
	jsonData = {'validate' : arrayCheckList}
	jsonData = JSON.stringify(jsonData)
	$.ajax({
	  type: "POST",
	  url: URL_APPLICATION+"/validation/validate",
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