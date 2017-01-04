var app = angular.module("app", ['ui.bootstrap']);

console.log(URL_APPLICATION)


proxy = app.factory('proxy', function proxy($http) {
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
			loadGroup2_inpn : function(){
				return $http.get(URL_APPLICATION+"synthese/loadGroup2_inpn")
			},

			exportShapeFile : function(data){
				return $http.post(URL_APPLICATION+"synthese/export", data)
			},
			loadTaxonomyHierachy : function(rang_fils, rang_pere, rang_grand_pere, value_rang_grand_pere, value){
				return $http.get(URL_APPLICATION +"synthese/loadTaxonomyHierachy/"+rang_fils+"/"+rang_pere+"/"+rang_grand_pere+"/"+value_rang_grand_pere+"/"+value)
			}
			
		}
	  });




app.controller("headerCtrl", function($scope){

 })


//template = URL_APPLICATION+'static/templates/app.html';
/*template = URL_APPLICATION+'static/templates/app.html';*/
/*template = URL_APPLICATION+'/synthese/synthese/templates/app.html'*/
template = "synthese/templates/app.html";
console.log(template);

function appCtrl (proxy){
	var ctrl = this;

	ctrl.nbObs = "Les 50 dernieres observations";
	
	proxy.lastObs().then(function(response){
		ctrl.geojson = response.data;
	});
	proxy.loadTaxons('Tout').then(function(response){
	  	ctrl.taxonslist = response.data;
  	})

	proxy.loadCommunes().then(function(response){
  		ctrl.communesList = response.data;
	})
	proxy.loadForets().then(function(response){
  		ctrl.foretsList = response.data;

	})
	proxy.loadGroup2_inpn().then(function(response){
		ctrl.group2_inpn = response.data;
		console.log(ctrl.group2_inpn);
	}) 

	ctrl.changeProtocole = function(protocole){
		proxy.loadTaxons(protocole).then(function(response){
			ctrl.taxonslist = response.data;
		})
	}

	ctrl.formSubmit = function(form){
		ctrl.form = form;
		proxy.sendData(form).then(function(response){
			ctrl.geojson = response.data;
			ctrl.nbObs = ctrl.geojson.features.length+' observation(s)'
		});
	}




	ctrl.updateCurrentObs = function(obs){
		ctrl.currentObs = obs;
	}


	ctrl.exportAlert = false;
	ctrl.exportShape = function(form){
		this.exportAlert = true;  
		proxy.exportShapeFile(form).then(function(response){
			window.location =URL_APPLICATION+'uploads/'+response.data;
			
		})
	}


	
}

app.component('app', {

  controller : appCtrl,
  templateUrl : template

});



function lastObsCtrl (){
	ctrl = this;

	this.update = function(currentObs){
		this.onUpdate({$event: {currentObs: currentObs}});
	}


}

templateLastObs = 'synthese/templates/lastObs.html';

app.component('lastObs', {

  controller : lastObsCtrl,
  templateUrl : templateLastObs,
  bindings : {
  	geojson : '<',
  	currentObs : '<',
  	onUpdate :'&',
  }

});


templateLeafletMap = 'synthese/templates/leafletMap.html';

function leafletCtrl($http,$scope){
	ctrl = this;
  

	ctrl.center = {
		lat: 16.2412500, 
		lng: -61.5361400,
		zoom: 10
	}

	selectLayer = undefined;
	var geojsonFeature = undefined;

	ctrl.childCurrentObs = null;

    var map = L.map('map').setView([16.2412500, -61.5361400],11);

	ctrl.setCurrentObs = function(obs){
			ctrl.childCurrentObs = obs;
	}


	

	L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v9/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoidGhlb2xlY2hlbWlhIiwiYSI6ImNpa29lODhvejAwYTl3MGxzZGY0aHc0NXIifQ.fEujW2fUlRuUk9PHfPdKIg').addTo(map);

	function onEachFeature(features, layer){

		// bind pop up
		nom_vern = " - "
		if (features.properties.nom_vern != null){
			nom_vern = features.properties.nom_vern
		}
		layer.bindPopup ("<b>Nom Latin:</b> <a target='_blank' href= 'https://inpn.mnhn.fr/espece/cd_nom/"+features.properties.cd_nom+"'>"+features.properties.lb_nom+ "<br> </a>\
						  <b> Nom commun: </b>"+ nom_vern +"<br> \
						  <b> Date: </b> " + features.properties.date+" <br>\
						  <b> Observateur: </b>"+ features.properties.observateur+ "<br>\
						  <b> Validé : </b>"+ features.properties.valide )
	}



    function loadGeojson(geojsonData){
    	if (geojsonFeature != undefined){
    	map.removeLayer(geojsonFeature)
    	}
		geojsonFeature = L.geoJSON(geojsonData,{
			pointToLayer: function (feature, latlng) {
           		return L.circleMarker(latlng);
           	},
           	onEachFeature: onEachFeature,
			}).addTo(map);
	}

	function onCurrentObsChange(id_synthese){
		if (selectLayer != undefined){
			selectLayer.setStyle({
						color: '#3388ff',
		            	fillColor: '#3388ff'
					})
			}

		p = (geojsonFeature._layers);
        
        for (var key in p) {
          if (p[key].feature.properties.id_synthese == id_synthese){
            selectLayer = p[key];
			}
          }
        if (selectLayer != undefined){
        selectLayer.setStyle({
					color: '#ff0000',
		            fillColor: '#ff0000'
				})
        map.setView(selectLayer._latlng, 12);
    	}
	}



         this.$onChanges = function(changesObj){
         	console.log(changesObj);
      		if(changesObj.geojson){
      			geojsondData=changesObj.geojson.currentValue;
      			loadGeojson(geojsondData);
      		}

      		if(changesObj.currentObs){
      			if(changesObj.currentObs.currentValue){
	      			onCurrentObsChange(changesObj.currentObs.currentValue);
	      		}
      		}
      	}

}


app.component('leafletCtrl', {

  controller : leafletCtrl,
  templateUrl : templateLeafletMap,
  bindings : {
  	geojson : '<',
  	currentObs : '<',
  	onCurrentObsChange :'&',
  	childCurrentObs : '=',
  }

});



templateForm = 'synthese/templates/formObs.html';


function formCtrl(proxy, $http, $scope){
	ctrl = this;



	// Modele du formulaire
	ctrl.form = {
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
		this.onProtocoleChange({$event:{protocole:protocole}})}


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
	 	   $("#input_lbnom").val($item.lb_nom);
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
		this.newTaxons = [];
		this.showNewTaxons = false;
		this.form.regne = null;
		this.form.listTaxons = [];
		if (this.taxon){
			this.form.taxon.cd_nom = null;
			this.form.taxon.lb_nom = null;
		}

		this.form.taxon.nom_vern = null;
		this.form.group2_inpn = null;

		$("#input_lbnom").val('');
		$("#input_nomvern").val('');
		$('#firstDate').val('');
		$('#lastDate').val('');
		$('#inputCommune').val('');
		$('#inputForet').val('');
		// supprime tout les values des select de la modal

		$('#formContent select').toArray().forEach(function(select){
			$(select).val('')
		})

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
  	onFormSubmit : '&',
  	taxons : '<',
	communes : '<',
	forets: '<',
	group2inpn : '<',
	onProtocoleChange : '&'
  }
});



