module.exports = function(angularInstance){

	templateLeafletCtrl = 'synthese/templates/map.html';

	function mapCtrl($http, $scope, leafletData){
		mapCtrl = this;
		var selectLayer;
		layersDict = {};


	mapCtrl.$onInit = function(){
	console.log("INIT");

	console.log(this.mainController);

	this.onEachFeature = function(feature, layer){
		// build the dict of layers
		layersDict[feature.properties.id] = layer;
		layer.on({
			click : function(){
				console.log("clickkkkkk");
				// update the propertie in the app controller
				mapCtrl.mainController.updateCurrentListObs(feature.properties.id);
				// set the style and popup
				if (selectLayer != undefined){
						selectLayer.setStyle(originStyle)
					}
				selectLayer = layer;
				styleAndPopup(selectLayer);	
			}
		});
	};


	}//end onINIT

			this.center = {
			lat: configuration.MAP.COORD_CENTER.Y, 
			lng: configuration.MAP.COORD_CENTER.X,
			zoom: configuration.MAP.ZOOM_LEVEL
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
				if(selectLayer.feature.geometry.type == 'MultiPolygon'){
					table = "<p>"+selectLayer.feature.properties.nb_observation+" observation(s)</p><table class='table'><thead><tr><th>Nom </th><th>Date</th></tr></thead> <tbody>"
					selectLayer.feature.properties.listIdSyn.forEach(function(obs, index){
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
								   'listIdSyn': [currentFeature.properties.id_synthese],
								   'lb_nom': [currentFeature.properties.lb_nom],
								   'observateurs': [currentFeature.properties.observateur],
								   'date' : [currentFeature.properties.date]}
					var j = 0;
					while(j < copyGeojson.length){
						if (i != j && copyGeojson[j].properties.id === currentIdMaille){

							console.log("copyGeojson")
							console.log(copyGeojson);
							properties.nb_observation++;
							properties.listIdSyn.push(copyGeojson[j].properties.id_synthese);
							properties.lb_nom.push(copyGeojson[j].properties.lb_nom); 
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