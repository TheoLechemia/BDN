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
/******/ 	return __webpack_require__(__webpack_require__.s = 8);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, exports) {

module.exports = function(angularInstance){

proxy = angularInstance.factory('proxy', function proxy($http) {
		return{
			lastObs: function(){
	            return $http.get(configuration.URL_APPLICATION+"synthese/lastObs");
				},
			sendData : function(data){
				return $http.post(configuration.URL_APPLICATION+"synthese/getObs", data)
			},

			loadTaxons: function(protocole){
				return $http.get(configuration.URL_APPLICATION+"synthese/loadTaxons/"+protocole)
			},
			loadCommunes: function(){
				return $http.get(configuration.URL_APPLICATION+"synthese/loadCommunes")
			},
			loadForets: function(){
				return $http.get(configuration.URL_APPLICATION+"synthese/loadForets")
			},
			loadTypologgie : function(){
				return $http.get(configuration.URL_APPLICATION+"synthese/loadTypologgie")
			},
			exportShapeFile : function(data){
				return $http.post(configuration.URL_APPLICATION+"synthese/export", data)
			},
			loadTaxonomyHierachy : function(rang_fils, rang_pere, rang_grand_pere, value_rang_grand_pere, value){
				return $http.get(configuration.URL_APPLICATION +"synthese/loadTaxonomyHierachy/"+rang_fils+"/"+rang_pere+"/"+rang_grand_pere+"/"+value_rang_grand_pere+"/"+value)
			},
			loadProtocole: function(){
				return $http.get(configuration.URL_APPLICATION+"synthese/loadProtocoles")
			}			
		}
	  });
}

/***/ }),
/* 1 */
/***/ (function(module, exports, __webpack_require__) {

module.exports = function(angularInstance){

	__webpack_require__(5)(angularInstance);
	__webpack_require__(7)(angularInstance);
	__webpack_require__(6)(angularInstance);


	function detailObsController(){
	}



var detailObsTemplate = 'synthese/templates/detailObs.html';

	angularInstance.component('detailObs', {
	  controller : detailObsController,
	  templateUrl : detailObsTemplate,
	  bindings : {
	  	'cdNom' : '<',
	  	'idSynthese' : '<',
	  }
	});
}//END WEBPACK

/***/ }),
/* 2 */
/***/ (function(module, exports) {

module.exports = function(angularInstance){

function formControler(proxy, $http, $scope){
	formCtrl = this;

	// Modele du formulaire
	formCtrl.form = {
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
	formCtrl.regneRadio = 'current';
	$('.radiotout').attr("checked");

	$('radio').click(function(){
		$(this).siblings.removeAttr('checked')
	})
	// changement de protocole, change les données de recherche des taxons (faune, flore) depuis le module pere APP
	this.changeProtocole = function(protocole){
		if(protocole){
			currentProtocole = protocole
		}
		else{
			currentProtocole = "Tout"
		}
		this.onProtocoleChange({$event:{protocole:currentProtocole}})
	}


	// Liste des rang taxonomique de la recherche avancée
	formCtrl.regne = ['Animalia', 'Plantae', 'Fungi']
	$scope.phylum = [];
	$scope.ordre = [];
	$scope.classe = [];
	$scope.famille = [];

	// chargement des données des rang taxonomique en ajax
	formCtrl.loadTaxonomyHierachy = function(rang_fils,rang_pere, rang_grand_pere,value_rang_grand_pere, value){
		proxy.loadTaxonomyHierachy(rang_fils,rang_pere,rang_grand_pere,value_rang_grand_pere, value).then(function(response){
			$scope[rang_fils] = response.data;
		})
	}
	

	// UI event for taxonomie
	formCtrl.showTaxonomie = false;


	// si on fait la recherche taxonomique: on affiche les trucs selectionnés, et on met à null la recherche par nom de taxon
	formCtrl.onTaxonomieChange = function(){
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
	formCtrl.fillTaxonEvent = function(){
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
		formCtrl.showNewTaxons = false;
		formCtrl.newTaxons = []
	 formCtrl.onSelectNomVern = function ($item, $model, $label) {
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


	 formCtrl.onSelectlbNom = function ($item, $model, $label) {
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
	formCtrl.removeTaxonEvent = function(cd_nom){
		console.log("remove");	
		this.newTaxons.splice(this.newTaxons.indexOf(cd_nom), 1 );
		this.form.listTaxons.splice(this.newTaxons.indexOf(cd_nom), 1 );
		if (this.newTaxons.length == 0){
			this.showNewTaxons = false;
		}
	}

	// rafrachir l'ensemble des sélections
	formCtrl.onRefreshEvent = function(){
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
  	formCtrl.maxDate = new Date()

  	formCtrl.popup = {
    	first:{ opened : false},
    	last:{opened:false} 
  		};


	formCtrl.open = function(prop) {
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

  controller : formControler,
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

}// END WEBPACK

/***/ }),
/* 3 */
/***/ (function(module, exports, __webpack_require__) {

module.exports = function(angularInstance){

__webpack_require__(0)(angularInstance);


function listObsCtrl ($uibModal, $http, proxy){
	listCtrl = this;
	listCtrl.currentPoint = null;

	var overFlowedList = $('.last-obs');

	listCtrl.$onChanges = function(changes){
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
	};

	listCtrl.zoom = function(geojsonProperties){
		this.mainController.updateCurrentLeafletObs(geojsonProperties);
		this.mainController.updateCurrentListObs(geojsonProperties);
	};

	listCtrl.isCurrentObs = function(id, row_id_synthese){
			return id == row_id_synthese;	
	};

	listCtrl.selected = 'point';

	listCtrl.isSelected = function(list){
		return this.selected === list;
	};

	listCtrl.changeList = function(list){
		this.currentList = this.geojson[list];
		this.selected = list;
	};

	listCtrl.exportShape = function(geojson){
	    proxy.exportShapeFile(geojson).then(function(response){
	      window.location =configuration.URL_APPLICATION+'synthese/uploads/'+response.data;       
	    })
  	};

}// END CONTROLLER

templateLastObs = 'synthese/templates/listObs.html';

angularInstance.component('listObs', {

  controller : listObsCtrl,
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
/* 4 */
/***/ (function(module, exports) {

module.exports = function(angularInstance){

	templateLeafletCtrl = 'synthese/templates/map.html';

	function mapCtrl($http, $scope, leafletData){
		mapCtrl = this;
		var selectLayer;
		layersDict = {};


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

/***/ }),
/* 5 */
/***/ (function(module, exports) {

module.exports = function(angularInstance){

	function observationController($http){
		var obsCtrl = this;
		obsCtrl.currentObsDetails = undefined;

		obsCtrl.loadObsDetails = function(id_synthese){
			$http.get(configuration.URL_APPLICATION+"synthese/detailsObs/"+id_synthese).then(function(response){
				obsCtrl.currentObsDetails = response.data;
			})
		}

		obsCtrl.$onChanges = function(changes){
			if(changes){
				console.log("changes");
				if(changes.idSynthese.currentValue != undefined){
					console.log(changes);
					this.loadObsDetails(changes.idSynthese.currentValue);
				}
			}
		}
	}// END CONTROLLER



var observationTemplate = 'synthese/templates/observation.html';

	angularInstance.component('observation', {
	  controller : observationController,
	  templateUrl : observationTemplate,
	  bindings : {
	  	'idSynthese' : '<',
	  }
	});
}//END WEBPACK

/***/ }),
/* 6 */
/***/ (function(module, exports) {

module.exports = function(angularInstance){

	function reglementationController($http){
		reglCtrl = this;

		reglCtrl.loadReglementationDetails = function(cdNom){
			$http.get(configuration.URL_APPLICATION+"synthese/detailsReglementation/"+cdNom).then(function(response){
				reglCtrl.currentRegDetails = response.data;
			});
		}

		reglCtrl.$onChanges = function(changes){
			if(changes){
				console.log("changes");
				if(changes.cdNom.currentValue != undefined){
					this.loadReglementationDetails(changes.cdNom.currentValue);
				}
			}
		}
	}



var reglementationTemplate = 'synthese/templates/reglementation.html';

	angularInstance.component('reglementation', {
	  controller : reglementationController,
	  templateUrl : reglementationTemplate,
	  bindings : {
	  	'cdNom' : '<',
	  }
	});
}//END WEBPACK

/***/ }),
/* 7 */
/***/ (function(module, exports) {

module.exports = function(angularInstance){

	function taxonomieController($http){
		taxCtrl = this;

		taxCtrl.loadTaxonomieDetails = function(cdNom){
			$http.get(configuration.URL_APPLICATION+"synthese/detailsTaxonomie/"+cdNom).then(function(response){
				taxCtrl.currentTaxonomieDetails = response.data;
			});
		}

		taxCtrl.$onChanges = function(changes){
			if(changes){
				console.log("changes");
				if(changes.cdNom.currentValue != undefined){
					this.loadTaxonomieDetails(changes.cdNom.currentValue);
				}
			}
		}
	}//END CONTROLLER



var taxonomieTemplate = 'synthese/templates/taxonomie.html';

	angularInstance.component('taxonomie', {
	  controller : taxonomieController,
	  templateUrl : taxonomieTemplate,
	  bindings : {
	  	'cdNom' : '<',
	  }
	});
}//END WEBPACK

/***/ }),
/* 8 */
/***/ (function(module, exports, __webpack_require__) {

var angularInstance = angular.module("app", ['ui.bootstrap', 'leaflet-directive', 'ngRoute']);


__webpack_require__(0)(angularInstance);

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


  ctrl.updateCurrentListObs = function(geojsonProperties){
    console.log("geojsonProperties: ")
    console.log(geojsonProperties)
    ctrl.currentListObs = geojsonProperties.id;
    
    // pour la recherche sur le detail taxon on prend le premier ID et le premier cd_nom si c'est une maille
    ctrl.currentCd_nom = geojsonProperties.cd_nom instanceof Array ? geojsonProperties.cd_nom[0] : geojsonProperties.cd_nom;
    ctrl.currentIdSynthese = geojsonProperties.id_synthese instanceof Array ? geojsonProperties.id_synthese[0]:geojsonProperties.id_synthese
  }

  ctrl.updateCurrentLeafletObs = function(geojsonProperties){
    ctrl.currentLeafletObs = geojsonProperties.id;
    ctrl.currentCd_nom = geojsonProperties.cd_nom instanceof Array ? geojsonProperties.cd_nom[0] : geojsonProperties.cd_nom;
    ctrl.currentIdSynthese = geojsonProperties.id_synthese instanceof Array ? geojsonProperties.id_synthese[0]:geojsonProperties.id_synthese
  }


}

angularInstance.component('app', {

  controller : appCtrl,
  templateUrl : template

});


__webpack_require__(2)(angularInstance);
__webpack_require__(4)(angularInstance);
__webpack_require__(3)(angularInstance);
__webpack_require__(1)(angularInstance);

/***/ })
/******/ ]);