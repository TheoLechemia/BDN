var app = angular.module("app", ['ui.bootstrap']);

console.log(URL_APPLICATION)


proxy = app.factory('proxy', function proxy($http) {
		return{
			lastObs: function(){
	            return $http.get(URL_APPLICATION+"lastObs");
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
	  });




app.controller("headerCtrl", function($scope){

 })


template = URL_APPLICATION+'static/templates/app.html';

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


	ctrl.updateCurrentObs = function(obs){
		ctrl.currentObs = obs;
	}



	ctrl.exportShape = function(form){
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

templateLastObs = URL_APPLICATION+'static/templates/lastObs.html';

app.component('lastObs', {

  controller : lastObsCtrl,
  templateUrl : templateLastObs,
  bindings : {
  	geojson : '<',
  	currentObs : '<',
  	onUpdate :'&',
  }

});


templateLeafletMap = URL_APPLICATION+'static/templates/leafletMap.html';

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
	ctrl.test = "hop";

/*	$scope.$watch(function(){
		return ctrl.test;
	}, function(newVal){
		alert('value change: '+newVal)
	});*/


	ctrl.testclick = function(){
		console.log(ctrl.test);
	}


	

	L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v9/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoidGhlb2xlY2hlbWlhIiwiYSI6ImNpa29lODhvejAwYTl3MGxzZGY0aHc0NXIifQ.fEujW2fUlRuUk9PHfPdKIg').addTo(map);

	function onEachFeature(features, layer){

		// bind pop up
		nom_vern = " - "
		if (features.properties.nom_vern != null){
			nom_vern = features.properties.nom_vern
		}
		layer.bindPopup ("<b>Nom Latin:</b> <a href= 'https://inpn.mnhn.fr/espece/cd_nom/"+features.properties.cd_nom+"'>"+features.properties.lb_nom+ "<br> </a>\
						  <b> Nom commun: </b>"+ nom_vern +"<br> \
						  <b> Date: </b> " + features.properties.date+" <br>\
						  <b> Observateur: </b>"+ features.properties.observateur)
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



templateForm = URL_APPLICATION+'static/templates/formObs.html';


function formCtrl(proxy, $http, $scope){
	ctrl = this;

	$scope.test = "yahhhhhhhh";

	$('.radiotout').attr("checked");

	$('radio').click(function(){
		$(this).siblings.removeAttr('checked')
	})



	ctrl.regne = ['Animalia', 'Plantae', 'Fungi']
	$scope.phylum = [];
	$scope.ordre = [];
	$scope.classe = [];
	$scope.famille = [];


	function fillList(response){
		listHierarchyTaxonomy.phylum = response;
		console.log(listHierarchyTaxonomy)
	}
	
	ctrl.loadTaxonomyHierachy = function(rang_fils,rang_pere, rang_grand_pere,value_rang_grand_pere, value){
		proxy.loadTaxonomyHierachy(rang_fils,rang_pere,rang_grand_pere,value_rang_grand_pere, value).then(function(response){
			$scope[rang_fils] = response.data;

		})
	
	}

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

	ctrl.regneRadio = 'current';


	this.submitForm = function(form){
		this.onFormSubmit({$event: {form: form}})
	}

	this.changeProtocole = function(protocole){
		this.onProtocoleChange({$event:{protocole:protocole}})
	}

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



