module.exports = function(angularInstance){
	console.log('exectuteds ???')

	templateLeafletCtrl = 'synthese/templates/map.html';

	function mapCtrl($http, $scope, leafletData){
		ctrl = this;

		ctrl.center = {
			lat: 16.2412500, 
			lng: -61.5361400,
			zoom: 10
		}

		var originStyle = {
		    "color": "#3388ff",
		    "fill": true,
		    "fillOpacity": 0.2,
		    "weight":3
		};

		var selectedStyle = {
		  'color':'#ff0000',
		   'weight':3
		}

		var mailleStyle = {
	    "color": "#000000",
	    "weight": 1,
	    "fillOpacity": 0
	};

		var selectLayer;
		function onCurrentObsChange(id_synthese){

			leafletData.getMap()
		        .then(function(map) {
		        	// get the object which contain all the geojson layer

		            layerObject = map._layers;
		            if (selectLayer != undefined){
						selectLayer.setStyle(originStyle)
					}
			        for (var key in layerObject) {
			        	//check if its a point or a maille (could be a map layer)
			        	if(layerObject[key].feature){
			        		// check if the properties id_synthese is a array or just a string

			        			i = 0;
			        			while(i<layerObject[key].feature.properties.id_synthese.length && layerObject[key].feature.properties.id_synthese[i] != id_synthese ){
			        				i=i+1
			        			}
			        			if (i<layerObject[key].feature.properties.id_synthese.length){
			        				selectLayer = layerObject[key]
			        			}
			      	        		
			        	}
			          }
		        if (selectLayer != undefined){
			        selectLayer.setStyle(selectedStyle);

			        selectLayer.bindPopup("<b>"+selectLayer.feature.properties.nom_vern+"<br> </a> <b> Le: </b> "+selectLayer.feature.properties.date+" <br>").openPopup();
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
			        }
		    });
	}

		 ctrl.loadGeojsonPoint = function(currentGeojson){
			this.geojsonToDirective = {
				'point' :{
					'data' : currentGeojson.point,
					 pointToLayer: function (feature, latlng) {
			    		return L.circleMarker(latlng)
					}
				},
				'maille': {
					'data': currentGeojson.maille,
				}
		 	}
		}

			

		ctrl.$onChanges = function(changes){
			// charge les geojson à la directive une fois qu'ils sont chargés en AJAX
			if (changes.geojson){
				if(changes.geojson.currentValue != undefined){
				reduceGeojsonMaille = {'type': 'FeatureCollection',
						'features' : []
					}
				var i=0;
				var copyGeojson = changes.geojson.currentValue.maille.features.slice();

				while(i<copyGeojson.length){
					currentFeature= copyGeojson[i];
					currentIdMaille = currentFeature.properties.code_maille;
					geometry = currentFeature.geometry;
					properties = {'code_maille' : currentIdMaille, 'nb_observation' : 1, 'id_synthese' : [currentFeature.properties.id_synthese[0]]}
					var j = 0;
					while( j < copyGeojson.length  ){
						if (i != j && copyGeojson[j].properties.code_maille === currentIdMaille){

							properties.nb_observation++;
							properties.id_synthese.push(copyGeojson[j].properties.id_synthese[0]);
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
				console.log('changes');
				onCurrentObsChange(changes.currentLeafletObs.currentValue);
			}
		}


		//EVENT
		$scope.$on('leafletDirectiveGeoJson.click', function(e, args) {
	      	//if its a maille, just open the popup

	      	// Update CurrentList pour hilighter la liste
	      	ctrl.mainController.updateCurrentListObs(args.model.properties.id_synthese);

	      	// bind les popup + met le style
	      	console.log(selectLayer);
	       	if (selectLayer != undefined){
					selectLayer.setStyle(originStyle)
				}
			selectLayer = args.leafletObject;

			if(args.model.geometry.type == 'MultiPolygon'){
				table = "<p>"+args.model.properties.nb_observation+" observation(s)</p><table class='table'><thead><tr><th>Nom </th><th>Date</th></tr></thead> <tbody>"
				console.log(args.model)
				args.model.properties.id_synthese.forEach(function(obs, index){
					table+="<tr> <td> mon nom </td> <td> "+args.model.properties.id_synthese[index]+"</td> </tr>"
				})
				table+="</tbody> </table>"
				args.leafletObject.bindPopup(table).openPopup();

			}else{
				args.leafletObject.bindPopup("<b>"+args.model.properties.id_synthese+"<br> </a> <b> Le: </b> "+args.model.properties.code_maille+" <br>").openPopup();
			}
	      	
	      	args.leafletObject.setStyle(selectedStyle);
	      	
		});



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