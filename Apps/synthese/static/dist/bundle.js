/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};

/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {

/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;

/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};

/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);

/******/ 		// Flag the module as loaded
/******/ 		module.l = true;

/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}


/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;

/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;

/******/ 	// identity function for calling harmony imports with the correct context
/******/ 	__webpack_require__.i = function(value) { return value; };

/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, {
/******/ 				configurable: false,
/******/ 				enumerable: true,
/******/ 				get: getter
/******/ 			});
/******/ 		}
/******/ 	};

/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};

/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };

/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";

/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 4);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, exports) {

module.exports = function(angularInstance){

function formCtrl(proxy, $http, $scope){
	ctrl = this;

	// Modele du formulaire
	ctrl.form = {
		'selectedProtocole': null,
		'who' : null,
		'taxon' : {'lb_nom': null, 'nom_vern': null, 'cd_nom' : null },
		'listTaxons' : [],
		'where' : {'code_insee': null, 'nom': null},
		'when' : {'first': null, 'last': null},
		'foret' : {'ccod_frt': null, 'lib_frt': null},
		'taxonomie' : {'rang': null, 'value': null},
		'regne' : null,
		'phylum' : null,
		'classe' : null,
		'ordre': null,
		'famille': null,
		'group2_inpn': null,
		'habitat': {'id':null, 'type':null},
		'protection':null,
		'lr':{'id_statut':null, 'type_statut':null},
		'observateur': {'observateur':null},
		'structure': {'id_structure': null, 'nom_structure': null},
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
	// changement de protocole, change les données de recherche des taxons (faune, flore) depuis le module pere APP
	this.changeProtocole = function(protocole){
		if(protocole){
			currentProtocole = protocole.nom_schema
		}
		else{
			currentProtocole = "Tout"
		}
		this.onProtocoleChange({$event:{protocole:currentProtocole}})
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
	ctrl.showTaxonomie = false;


	// si on fait la recherche taxonomique: on affiche les trucs selectionnés, et on met à null la recherche par nom de taxon
	ctrl.onTaxonomieChange = function(){
		if (this.showTaxonomie == false){
			this.showTaxonomie = !$scope.showTaxonomie;
		}
		// on met à null les cd_nom et vide le tableau de cd_nom du formulaire
		this.form.taxon.cd_nom = null;
		this.form.taxon.lb_nom = null;
		this.form.taxon.nom_vern = null;
		this.form.listTaxons = [];
		this.newTaxons = [];

		// on vide les input de la recherche des taxons
		$("#input_lbnom").val('');
		$("#input_nomvern").val('');
		// on chache eventuellement la liste des taxons selectionnées
		this.showNewTaxons = false;
	}
	// si on rempli  un nom de taxon apres avoir faire une recherche par taxonomie, on reinitialise la hierarchie taxo à null;
	ctrl.fillTaxonEvent = function(){
		if(this.showTaxonomie){
			this.showTaxonomie = !$scope.showTaxonomie;
			this.form.regne = null;
			this.form.phylum = null;
			this.form.classe = null;
			this.form.ordre = null;
			this.form.famille = null;
		}
	} 

	//synchronisation des deux inputs et ajout du cd_nom selectionné dans la liste de cd_nom du formulaire
	// et ajout à la liste des taxons selectionnés
		ctrl.showNewTaxons = false;
		ctrl.newTaxons = []
	 ctrl.onSelectNomVern = function ($item, $model, $label) {
	 	   //$("#input_lbnom").val($item.lb_nom);
	 	   this.form.listTaxons.push($item.cd_nom);

	 	   	 if (this.showNewTaxons == false){
				this.showNewTaxons = !this.showNewTaxons;
			}
			this.newTaxons.push({'name':this.form.taxon.lb_nom, 'cd_nom': this.form.taxon.cd_nom});

			setTimeout(function(){
			$("#input_lbnom").val('');
			 $("#input_nomvern").val('');
			}, 1000)
		}


	 ctrl.onSelectlbNom = function ($item, $model, $label) {
	 	   $("#input_nomvern").val($item.nom_vern);
	 	   this.form.listTaxons.push($item.cd_nom);

	 	   	if (this.showNewTaxons == false){
				this.showNewTaxons = !this.showNewTaxons;
			}
			this.newTaxons.push({'name':this.form.taxon.lb_nom, 'cd_nom': this.form.taxon.cd_nom});

			// on vide les inputs

			setTimeout(function(){
			$("#input_lbnom").val('');
			 $("#input_nomvern").val('');
			}, 1000)

		}
	

		// retirer un taxon de la liste des taxons selectionnés
		ctrl.removeTaxonEvent = function(cd_nom){
			console.log("remove");	
			this.newTaxons.splice(this.newTaxons.indexOf(cd_nom), 1 );
			this.form.listTaxons.splice(this.newTaxons.indexOf(cd_nom), 1 );
			if (this.newTaxons.length == 0){
				this.showNewTaxons = false;
			}
		}

	// rafrachir l'ensemble des sélections
	ctrl.onRefreshEvent = function(){
		console.log('refresh');
		this.form = {
		'selectedProtocole': null,
		'who' : null,
		'taxon' : {'lb_nom': null, 'nom_vern': null, 'cd_nom' : null },
		'listTaxons' : [],
		'where' : {'code_insee': null, 'nom': null},
		'when' : {'first': null, 'last': null},
		'foret' : {'ccod_frt': null, 'lib_frt': null},
		'taxonomie' : {'rang': null, 'value': null},
		'regne' : null,
		'phylum' : null,
		'classe' : null,
		'ordre': null,
		'famille': null,
		'group2_inpn': null,
		'habitat': {'id':null, 'type':null},
		'protection':null,
		'lr':{'id_statut':null, 'type_statut':null},
		'observateur': {'observateur':null},
		'structure': {'id_structure': null, 'nom_structure': null},
		}

		this.newTaxons = [];
		this.showNewTaxons = false;
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

var templateForm = 'synthese/templates/formObs.html';


angularInstance.component('formObs', {

  controller : formCtrl,
  templateUrl : templateForm,
  bindings: {
  	onFormSubmit : '&',
  	taxons : '<',
	communes : '<',
	forets: '<',
	typologie : '<',
	protocoles : '<',
	onProtocoleChange : '&'
  }
});
}

/***/ }),
/* 1 */
/***/ (function(module, exports) {

module.exports = function(angularInstance){


function lastObsCtrl ($uibModal, $http){
	ctrl = this;
	ctrl.currentPoint = null;

	var overFlowedList = $('.last-obs');

	ctrl.$onChanges = function(changes){
		if (changes.geojson){
			if (changes.geojson.currentValue != undefined){
				this.currentList = changes.geojson.currentValue.point;
			}
		}
		if(changes.currentListObs){
			//scroll dans la liste
			if(changes.currentListObs.currentValue != undefined){
				    var vpHeight = overFlowedList.height();
				    var scrollTop = overFlowedList.scrollTop();
				    var link = $('#'+changes.currentListObs.currentValue);
				    if (link.length>0){
				   		var position = link.position();

				        $('.last-obs').animate({
					        scrollTop: (position.top + scrollTop -100)
					    }, 500);
					}
			}
		}
	}

	ctrl.zoom = function(id_synthese){
		this.mainController.updateCurrentLeafletObs(id_synthese);
		this.mainController.updateCurrentListObs(id_synthese);
	}

	ctrl.isCurrentObs = function(id, row_id_synthese){
			return id == row_id_synthese;	
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

templateLastObs = 'synthese/templates/listObs.html';

angularInstance.component('listObs', {

  controller : lastObsCtrl,
  templateUrl : templateLastObs,
  require: {
  	mainController : '^app',
  },
  bindings : {
  	'geojson' : '<',
  	'currentListObs' : '<',
  	'currentLeafletObs': '<',
  }

});

}

/***/ }),
/* 2 */
/***/ (function(module, exports) {

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

/***/ }),
/* 3 */
/***/ (function(module, exports) {

module.exports = function(angularInstance){

proxy = angularInstance.factory('proxy', function proxy($http) {
		return{
			lastObs: function(){
	            return $http.get(URL_APPLICATION+"synthese/lastObs");
				},
			sendData : function(data){
				return $http.post(URL_APPLICATION+"synthese/getObs", data)
			},

			loadTaxons: function(protocole){
				return $http.get(URL_APPLICATION+"synthese/loadTaxons/"+protocole)
			},
			loadCommunes: function(){
				return $http.get(URL_APPLICATION+"synthese/loadCommunes")
			},
			loadForets: function(){
				return $http.get(URL_APPLICATION+"synthese/loadForets")
			},
			loadTypologgie : function(){
				return $http.get(URL_APPLICATION+"synthese/loadTypologgie")
			},
			exportShapeFile : function(data){
				return $http.post(URL_APPLICATION+"synthese/export", data)
			},
			loadTaxonomyHierachy : function(rang_fils, rang_pere, rang_grand_pere, value_rang_grand_pere, value){
				return $http.get(URL_APPLICATION +"synthese/loadTaxonomyHierachy/"+rang_fils+"/"+rang_pere+"/"+rang_grand_pere+"/"+value_rang_grand_pere+"/"+value)
			},
			loadProtocole: function(){
				return $http.get(URL_APPLICATION+"synthese/loadProtocoles")
			}			
		}
	  });
}

/***/ }),
/* 4 */
/***/ (function(module, exports, __webpack_require__) {

var angularInstance = angular.module("app", ['ui.bootstrap', 'leaflet-directive', 'ngRoute']);


__webpack_require__(3)(angularInstance);

angularInstance.controller("headerCtrl", function($scope){

 })


template = 'synthese/templates/app.html';

function appCtrl (proxy){
  var ctrl = this;
  
  ctrl.nbObs = "Les 50 dernieres observations";
  proxy.lastObs().then(function(response){
      ctrl.geojson = response.data;

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
  proxy.loadTypologgie().then(function(response){
    ctrl.typologie = response.data;
  }) 
  proxy.loadProtocole().then(function(response){
    ctrl.protocoles = response.data;
  })

  ctrl.formSubmit = function(form){
    ctrl.form = form;
    console.log(form);
    proxy.sendData(form).then(function(response){
      ctrl.geojson = response.data;
      nbObs = ctrl.geojson.point.features.length+ctrl.geojson.maille.features.length
      ctrl.nbObs = nbObs+' observation(s)'
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

  ctrl.exportShape = function(form){
    proxy.exportShapeFile(form).then(function(response){
      window.location =URL_APPLICATION+'synthese/uploads/'+response.data;       
    })
  }


}

angularInstance.component('app', {

  controller : appCtrl,
  templateUrl : template

});


__webpack_require__(0)(angularInstance);
__webpack_require__(2)(angularInstance);
__webpack_require__(1)(angularInstance);

/***/ })
/******/ ]);