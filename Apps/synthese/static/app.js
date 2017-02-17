var app = angular.module("app", ['ui.bootstrap', 'leaflet-directive', 'ngRoute']);

console.log(URL_APPLICATION);

//####################################################################
// ######################## PROXY #######################
//####################################################################

/*proxy = app.factory('proxy', function proxy($http) {
		return{
			lastObs: function(){
	            return $http.get(URL_APPLICATION+"synthese/lastObs");
				},
			sendData : function(data){
				return $http.post(URL_APPLICATION+"getObs", data)
			},

			loadTaxons: function(protocole){
				return $http.get(URL_APPLICATION+"loadTaxons/"+protocole)
			},
			loadCommunes: function(){
				return $http.get(URL_APPLICATION+"loadCommunes")
			},
			loadForets: function(){
				return $http.get(URL_APPLICATION+"loadForets")
			},

			exportShapeFile : function(data){
				return $http.post(URL_APPLICATION+"export", data)
			},
			loadTaxonomyHierachy : function(rang_fils, rang_pere, rang_grand_pere, value_rang_grand_pere, value){
				return $http.get(URL_APPLICATION +"loadTaxonomyHierachy/"+rang_fils+"/"+rang_pere+"/"+rang_grand_pere+"/"+value_rang_grand_pere+"/"+value)
			}			
		}
	  });*/


//####################################################################
// ######################## APP MAIN #################################
//####################################################################

app.controller("headerCtrl", function($scope){

 })


template = 'synthese/templates/app.html';

function appCtrl (proxy){
	var ctrl = this;
	ctrl.geojsonToLeaflet = {};
	ctrl.geojson;
	// Arrays of id_synthese
	ctrl.currentListObs = [];
  	ctrl.currentLeafletObs=[];
	
	ctrl.nbObs = "Les 50 dernieres observations";

	proxy.lastObs().then(function(response){
			ctrl.geojson = response.data;
			console.log(ctrl.geojson.maille.features.length);
			ctrl.geojson.maille.features.forEach(function(i){
				console.log(i.geometry);
			})

		});
	


	proxy.loadTaxons('Tout').then(function(response){
	  	ctrl.taxonslist = response.data;
	  	ctrl.TaxonsFaune = ctrl.taxonslist.filter(function(t){
	  		return t.regne ='Animalia'
	  	})
	  	ctrl.TaxonsFlore = ctrl.taxonslist.filter(function(t){
	  		return t.regne ='Plantae'
	  	})
  	})

	proxy.loadCommunes().then(function(response){
  		ctrl.communesList = response.data;
	})
	proxy.loadForets().then(function(response){
  		ctrl.foretsList = response.data;
	})

	ctrl.formSubmit = function(form){
		ctrl.form = form;
		proxy.sendData(form).then(function(response){
			ctrl.geojson = response.data;
			ctrl.nbObs = ctrl.geojson.features.length+' observation(s)'
		});
	}

	ctrl.changeProtocole = function(protocole){
		proxy.loadTaxons(protocole).then(function(response){
			ctrl.taxonslist = response.data;
		})
	}


	ctrl.updateCurrentListObs = function(id_synthese){
		
		ctrl.currentListObs = id_synthese;
	}

	ctrl.updateCurrentLeafletObs = function(id_synthese){
		console.log("update with: "+ id_synthese);
		ctrl.currentLeafletObs = id_synthese;
	}



	ctrl.exportShape = function(geojson){
		proxy.exportShapeFile(geojson).then(function(response){
			window.location =URL_APPLICATION+'uploads/'+response.data;	     
		})
	}
}

app.component('app', {

  controller : appCtrl,
  templateUrl : template

});


//####################################################################
// ######################## MAIN FORMULAIRE #######################
//####################################################################



templateForm = 'synthese/templates/formObs.html';


function formCtrl(proxy, $http, $scope){
	ctrl = this;

	// Modele du formulaire
	ctrl.form = {
		who : null,
		lb_nom : {'lb_nom': null, 'cd_nom' : null },
		nom_vern : {'nom_vern': null, 'cd_nom' : null }, 
		where : {'code_insee': null, 'nom': null},
		when : {'first': null, 'last': null},
		foret : {'ccod_frt': null, 'lib_frt': null},
		taxonomie : {'rang': null, 'value': null},
		regne : null,
		phylum : null,
		classe : null,
		ordre: null,
		famille: null,
		group2_inpn: null,
	}

	// à l'envoie du formulaire, on le passe au module pere: APP qui fait la requete ajax sur les geojson et les passe a toute l'appli
	this.submitForm = function(form){
		this.onFormSubmit({$event: {form: form}})
	}


	//RADIO REGNE
	ctrl.regneRadio = 'current';
	$('.radiotout').attr("checked");

	$('radio').click(function(){
		$(this).siblings.removeAttr('checked')
	})
	// changement de protocole, change les données de recherche des taxons (faune, flore)
	this.changeProtocole = function(protocole){
		this.onProtocoleChange({$event:{protocole:protocole}})
	}


	// Liste des rang taxonomique de la recherche avancée
	ctrl.regne = ['Animalia', 'Plantae', 'Fungi']
	$scope.phylum = [];
	$scope.ordre = [];
	$scope.classe = [];
	$scope.famille = [];

	// chargement des données des rang taxonomique en ajax
	ctrl.loadTaxonomyHierachy = function(rang_fils,rang_pere, rang_grand_pere,value_rang_grand_pere, value){
		proxy.loadTaxonomyHierachy(rang_fils,rang_pere,rang_grand_pere,value_rang_grand_pere, value).then(function(response){
			$scope[rang_fils] = response.data;

		})
	}
	

	// UI event for taxonomie
	$scope.showTaxonomie = false;
	// si on fait la recherche taxonomique: on affiche les truc selectionné, et on met à null la recherche par nom de taxon
	ctrl.onTaxonomieChange = function(){
		if ($scope.showTaxonomie == false){
			$scope.showTaxonomie = !$scope.showTaxonomie;
		}
		// on met à null les cd_nom
		this.form.lb_nom.cd_nom = null;
		this.form.lb_nom.lb_nom = null;
		this.form.nom_vern.cd_nom = null;
		// on vide les input de la recherche des taxons
		$("#input_lbnom").val('');
		$("#input_nomvern").val('');
	}
	// si on rempli  un nom de taxon apres avoir faire une recherche par taxonomie, on reinitialise la hierarchie taxo à null;
	ctrl.fillTaxonEvent = function(){
		if($scope.showTaxonomie){
			$scope.showTaxonomie = !$scope.showTaxonomie;
			this.form.regne = null;
			this.form.phylum = null;
			this.form.classe = null;
			this.form.ordre = null;
			this.form.famille = null;
		}
	}

  	// UI event for date picker
  		ctrl.popup = {
    	first:{ opened : false},
    	last:{opened:false} 
  	};
	ctrl.open = function(prop) {
		if (prop == "first"){
    		this.popup.first.opened = true;
    	}
    	else {
    		this.popup.last.opened = true;
    	}
  	};


}

app.component('formObs', {

  controller : formCtrl,
  templateUrl : templateForm,
  bindings: {
  	taxons : '<',
  	communes : '<',
  	forets: '<',
  	onFormSubmit : '&',
  	onProtocoleChange : '&',
  }
});





//####################################################################
// ######################## LEAFLET MAIN MAP #######################
//####################################################################




templateLeafletCtrl = 'synthese/templates/leafletCtrl.html';

function leafletCtrl($http, $scope, leafletData){
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



}// END controller


app.component('leafletCtrl', {

  controller : leafletCtrl,
  templateUrl : templateLeafletCtrl,
  bindings : {
  	'geojson' : '<',
  	'currentListObs' : '<',
  	'currentLeafletObs': '<'
  }

});





//####################################################################
// ######################## LISTE OBSERVATIONS #######################
//####################################################################



function lastObsCtrl ($uibModal, $http){
	ctrl = this;
	ctrl.currentPoint = null;

	ctrl.$onChanges = function(changes){
		if (changes.geojson){
			if (changes.geojson.currentValue != undefined){
				ctrl.currentList = changes.geojson.currentValue.point;
			}
		}


	}

	ctrl.zoom = function(id_synthese){
		ctrl.mainController.updateCurrentLeafletObs(id_synthese);
		ctrl.mainController.updateCurrentListObs(id_synthese);
	}

	ctrl.isCurrentObs = function(listIdSynthese, row_id_synthese){
		i = 0;
		while(i<listIdSynthese.length){
			return listIdSynthese[i] == row_id_synthese;
			i++;
		}
	}

	ctrl.selected = 'point';

	ctrl.isSelected = function(list){
		return this.selected === list;
	}

	ctrl.changeList = function(list){
		this.currentList = this.geojson[list];
		this.selected = list;
	}


}


templateLastObs = 'synthese/templates/lastObs.html';

app.component('lastObs', {

  controller : lastObsCtrl,
  templateUrl : templateLastObs,
  require: {
  	mainController : '^app',
  },
  bindings : {
  	'geojson' : '<',
  	'currentListObs' : '<',
  	'currentLeafletObs': '<'
  }

});



