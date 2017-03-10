module.exports = function(angularInstance){
	console.log('exectuteds ???')

	templateLeafletCtrl = 'synthese/templates/map.html';

	function mapCtrl($http, $scope, leafletData){
		ctrl = this;
		ctrl.center = {
			lat: 16.2412500, 
			lng: -61.5361400,
			zoom: 10
		};

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

		var mailleStyle = {
	    "color": "#000000",
	    "weight": 1,
	    "fillOpacity": 0
		};

		var selectLayer;
		function onCurrentObsChange(id){
			// get the object which contain all the geojson layer
			console.log(id)
			leafletData.getMap()
		        .then(function(map) {
		        	if (selectLayer != undefined){
						selectLayer.setStyle(originStyle)
					}
					selectLayer = layersDict[id];

					styleAndPopup(selectLayer);

			        zoom = map.getZoom();
			        // latlng is different between polygons and point
			        var latlng;
			        if(selectLayer.feature.geometry.type == "MultiPolygon"){
			        	latlng = selectLayer._bounds._northEast;
			        }
			        else {
			        	latlng = selectLayer._latlng;
			        }

			        if (zoom>=12) {

			        	map.setView(latlng, zoom);
		    		}
		    		else{
		    			map.setView(latlng, 12);
		    		}
			        
		    });
	}


	function styleAndPopup(selectLayer){
				// set the style
				selectLayer.setStyle(selectedStyle);
				//bind the popup
				if(selectLayer.feature.geometry.type == 'MultiPolygon'){
					table = "<p>"+selectLayer.feature.properties.nb_observation+" observation(s)</p><table class='table'><thead><tr><th>Nom </th><th>Date</th></tr></thead> <tbody>"
					selectLayer.feature.properties.listIdSyn.forEach(function(obs, index){
						table+="<tr> <td> mon nom </td> <td> "+selectLayer.feature.properties.listIdSyn[index]+"</td> </tr>"
					})
					table+="</tbody> </table>"
					selectLayer.bindPopup(table).openPopup();

				}else{
					selectLayer.bindPopup("<b>"+selectLayer.feature.properties.id_synthese+"<br> </a> <b> Le: </b> "+selectLayer.feature.properties.code_maille+" <br>").openPopup();
				}
		      	
		      	selectLayer.setStyle(selectedStyle);
	}


layersDict = {};

	function onEachFeature(feature, layer){
		// build the dict of layers
		layersDict[feature.properties.id] = layer;
		layer.on({
			click : function(){
				console.log("click");
				// update the propertie in the app controller
				console.log(feature.properties.id);
				ctrl.mainController.updateCurrentListObs(feature.properties.id);
				// set the style and popup
				if (selectLayer != undefined){
						selectLayer.setStyle(originStyle)
					}
				selectLayer = layer;
				styleAndPopup(selectLayer);	
			}
		});
	}


		 ctrl.loadGeojsonPoint = function(currentGeojson){
			this.geojsonToDirective = {
				'point' : {
					'data' : currentGeojson.point,
					 pointToLayer: function (feature, latlng) {
					 	var marker = L.circleMarker(latlng);
					 	layersDict[feature.properties.id] = marker;
			    		return marker;
					},
					'onEachFeature': onEachFeature,
				},
				'maille': {
					'data': currentGeojson.maille,
					'onEachFeature' : onEachFeature,
					}
		 	}
		}
		 	console.log(layersDict);
		 	

			

		ctrl.$onChanges = function(changes){
			// charge les geojson à la directive une fois qu'ils sont chargés en AJAX
			if (changes.geojson){
				if(changes.geojson.currentValue != undefined){
					console.log(changes.geojson.currentValue);
				reduceGeojsonMaille = {'type': 'FeatureCollection',
						'features' : []
					}
				var i=0;
				var copyGeojson = changes.geojson.currentValue.maille.features.slice();

				while(i<copyGeojson.length){
					currentFeature= copyGeojson[i];
					currentIdMaille = currentFeature.properties.id;
					geometry = currentFeature.geometry;
					properties = {'code_maille' : currentIdMaille, 'nb_observation' : 1, 'id' : currentFeature.properties.id, 'listIdSyn': [currentFeature.properties.id_synthese]}
					var j = 0;
					while(j < copyGeojson.length){
						if (i != j && copyGeojson[j].properties.id === currentIdMaille){

							properties.nb_observation++;
							properties.listIdSyn.push(copyGeojson[j].properties.id_synthese);
							//si il y etait deja on peut le remover
							copyGeojson.splice(j,1);
						}
						j = j+1;
					}
					reduceGeojsonMaille.features.push({
			          'type' : 'Feature',
			          'properties' : properties,
			          'geometry' : geometry   
					})
					i = i+1;
				}

				newGeojson = {'point':changes.geojson.currentValue.point, 'maille': reduceGeojsonMaille}

				this.loadGeojsonPoint(newGeojson);
				}
			}
			// if change from the list, zoom on the selected layers
			if(changes.currentLeafletObs){
				if(changes.currentLeafletObs.currentValue != undefined){
					onCurrentObsChange(changes.currentLeafletObs.currentValue);
				}
			}
		}


	} // END controller


	angularInstance.component('map', {

	  controller : mapCtrl,
	  templateUrl : templateLeafletCtrl,
	  bindings : {
	  	'geojson' : '<',
	  	'currentListObs' : '<',
	  	'currentLeafletObs': '<'
	  }

	});

}