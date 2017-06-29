module.exports = function(angularInstance){

	templateLeafletCtrl = 'synthese/templates/map.html';

	function mapCtrl($http, $scope, leafletData){
		mapCtrl = this;
		var selectLayer;

		layersDict = {};
		console.log(configuration.MAP.LAYERS);
		this.layers = configuration.MAP.LAYERS;


		mapCtrl.$onInit = function(){
			// variable pour le switcher entre point et polygone
			this.is_point_display = true;
			this.is_maille_display = true;
		}

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

	// ZOOM sur l'observation selectionnée depuis la liste
	function onCurrentObsChange(id){
		// get the object which contain all the geojson layer
		leafletData.getMap()
	        .then(function(map) {
	        	if (selectLayer != undefined){
					selectLayer.setStyle(originStyle)
				}
				selectLayer = layersDict[id];
				console.log('selectLayer');
				console.log(selectLayer);

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

	// Charge le nouveau geojson pour les passer à la directive-angular 'leaflet'
	mapCtrl.loadGeojsonPoint = function(currentGeojson){
		 console.log('on load les geojsons')
			this.geojsonToDirective = {
				'point' : {
					'data' : currentGeojson.point,
					 pointToLayer: function (feature, latlng) {
					 	var marker = L.circleMarker(latlng);
					 	//layersDict[feature.properties.id] = marker;
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

	var saveLayersObs;

	// Fonction pour afficher/masquer les points sur la carte
	mapCtrl.togglePoint = function(){
		// true on remove les point
		if (this.is_point_display){
			this.geojsonToDirective.point.data = null;
			this.is_point_display = false;
		}
		//false on remet les points
		else {
			this.geojsonToDirective.point.data = this.newGeojson.point;
			this.is_point_display = true;
		}
	}

	// Fonction pour afficher/masquer les mailles sur la carte
	mapCtrl.toggleMaille = function(){
		// true on remove les maille
		if (this.is_maille_display){
			this.geojsonToDirective.maille = {};
			this.is_maille_display = false;
		}
		//false on remet les mailles
		else {
			// si les points doivent être afficher, on supprime et on raffiche tout
			if(this.is_point_display){
				this.geojsonToDirective = null;
				this.loadGeojsonPoint(this.newGeojson);
			}
			// si les points ne doivent pas etre affichés, on supprimme et raffiche tout et on supprime les points
			// si on ne fait pas cette manip, les popup des mailles ne s'affiche pas.
			else{
				this.geojsonToDirective = null;
				this.loadGeojsonPoint(this.newGeojson);
				this.geojsonToDirective.point.data = null;
			}
		 this.is_maille_display = true;
		}
	}

	//initialisation de newGeojson en objet vide
	this.newGeojson = {};
	// lifecycle du composant a chaque fois que le bindings est changé
	mapCtrl.$onChanges = function(changes){
			// charge les geojson à la directive une fois qu'ils sont chargés en AJAX
			if (changes.geojson){
				// on remet à true les checkbox de le l'affichage maille / point
				this.is_maille_display = true;
				this.is_point_display = true;
				Array.from(document.getElementsByClassName('layer')).forEach(function(domEl){
					domEl.classList.add('active');
				});

				if(changes.geojson.currentValue != undefined){

				reduceGeojsonMaille = {'type': 'FeatureCollection',
						'features' : []
					}
				var i=0;
				var copyGeojson = changes.geojson.currentValue.maille.features.slice();
				// on boucle sur la liste triée des observations selon l'id maille pour ne construire qu'une feature par maille
				while(i<copyGeojson.length){
					currentFeature = copyGeojson[i];
					currentIdMaille = currentFeature.properties.id;
					geometry = currentFeature.geometry;

					properties = {'code_maille' : currentIdMaille,
								   'nb_observation' : 1,
								   'id' : currentFeature.properties.id,
								   'id_synthese': [currentFeature.properties.id_synthese],
								   'lb_nom': [currentFeature.properties.lb_nom],
								   'cd_nom': [currentFeature.properties.cd_nom],
								   'observateurs': [currentFeature.properties.observateur],
								   'date' : [currentFeature.properties.date]}
					var j = i+1;
					while(j < copyGeojson.length && copyGeojson[j].properties.id == currentIdMaille){
							properties.nb_observation++;
							properties.id_synthese.push(copyGeojson[j].properties.id_synthese);
							properties.lb_nom.push(copyGeojson[j].properties.lb_nom);
							properties.cd_nom.push(copyGeojson[j].properties.cd_nom); 
							properties.observateurs.push(copyGeojson[j].properties.observateur);
							properties.date.push(copyGeojson[j].properties.date);

							j = j+1;

					}
					reduceGeojsonMaille.features.push({
			          'type' : 'Feature',
			          'properties' : properties,
			          'geometry' : geometry   
					})
					// on avance jusqu'a j
					i = j;
				}

				this.newGeojson = {'point':changes.geojson.currentValue.point, 'maille': reduceGeojsonMaille}
				this.loadGeojsonPoint(this.newGeojson);
				console.log(this.newGeojson.maille);
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