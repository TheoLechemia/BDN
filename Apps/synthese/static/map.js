module.exports = function(angularInstance){

	templateLeafletCtrl = 'synthese/templates/map.html';

	function mapCtrl($http, $scope, leafletData){
		mapCtrl = this;
		var selectLayer;
		layersDict = {};
		console.log("ohohhhhhhhhhhhhhhhhhh")
		console.log(configuration.MAP.LAYERS);
		this.layers = configuration.MAP.LAYERS;


		mapCtrl.center = {
			'lat': configuration.MAP.COORD_CENTER.Y, 
			'lng': configuration.MAP.COORD_CENTER.X,
			'zoom': configuration.MAP.ZOOM_LEVEL
		};

		mapCtrl.onEachFeature = function(feature, layer){
		// build the dict of layers
		layersDict[feature.properties.id] = layer;
		layer.on({
			click : function(){
				// update the properties in the app controller
				mapCtrl.mainController.updateCurrentListObs(feature.properties);
				// set the style and popup
				if (selectLayer != undefined){
						selectLayer.setStyle(originStyle)
					}
				selectLayer = layer;
				styleAndPopup(selectLayer);	
			}
		});
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

		function styleAndPopup(selectLayer){
				console.log(selectLayer);
				// set the style
				selectLayer.setStyle(selectedStyle);
				//bind the popup
				if(selectLayer instanceof L.Polygon){
					table = "<p>"+selectLayer.feature.properties.nb_observation+" observation(s)</p><table class='table'><thead><tr> <th>Observateur </th> <th>Nom </th>  <th>Date</th></tr></thead> <tbody>"
					selectLayer.feature.properties.id_synthese.forEach(function(obs, index){
						table+="<tr> <td>"+selectLayer.feature.properties.observateurs[index]+" </td> <td>"+selectLayer.feature.properties.lb_nom[index]+" </td> <td> "+selectLayer.feature.properties.date[index]+"</td> </tr>"
					})
					table+="</tbody> </table>"
					selectLayer.bindPopup(table).openPopup();

				}else{
					selectLayer.bindPopup("<b>Observateur: </b> "+selectLayer.feature.properties.observateur+"<br> <b> Nom sc. : </b>  "+selectLayer.feature.properties.lb_nom+" <br> <b> Date: </b>  "+selectLayer.feature.properties.date+" <br>").openPopup();
				}
		      	
		      	selectLayer.setStyle(selectedStyle);
			};


	function onCurrentObsChange(id){
		// get the object which contain all the geojson layer
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
		        if(selectLayer instanceof L.Polygon){
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

	mapCtrl.loadGeojsonPoint = function(currentGeojson){
			this.geojsonToDirective = {
				'point' : {
					'data' : currentGeojson.point,
					 pointToLayer: function (feature, latlng) {
					 	var marker = L.circleMarker(latlng);
					 	layersDict[feature.properties.id] = marker;
			    		return marker;
					},
					'onEachFeature': this.onEachFeature,
				},
				'maille': {
					'data': currentGeojson.maille,
					'onEachFeature' : this.onEachFeature,
					}
		 	}
		}
		 	

			

	mapCtrl.$onChanges = function(changes){

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
					currentIdMaille = currentFeature.properties.id;
					geometry = currentFeature.geometry;
					console.log('current feature');
					console.log(currentFeature);

					properties = {'code_maille' : currentIdMaille,
								   'nb_observation' : 1,
								   'id' : currentFeature.properties.id,
								   'id_synthese': [currentFeature.properties.id_synthese],
								   'lb_nom': [currentFeature.properties.lb_nom],
								   'cd_nom': [currentFeature.properties.cd_nom],
								   'observateurs': [currentFeature.properties.observateur],
								   'date' : [currentFeature.properties.date]}
					var j = 0;
					while(j < copyGeojson.length){
						if (i != j && copyGeojson[j].properties.id === currentIdMaille){

							properties.nb_observation++;
							properties.id_synthese.push(copyGeojson[j].properties.id_synthese);
							properties.lb_nom.push(copyGeojson[j].properties.lb_nom);
							properties.cd_nom.push(copyGeojson[j].properties.cd_nom); 
							properties.observateurs.push(copyGeojson[j].properties.observateur);
							properties.date.push(copyGeojson[j].properties.date);
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
	   require: {
	  	mainController : '^app',
	  },
	  bindings : {
	  	'geojson' : '<',
	  	'currentListObs' : '<',
	  	'currentLeafletObs': '<'
	  }

	});

}