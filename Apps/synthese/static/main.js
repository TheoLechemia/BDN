var angularInstance = angular.module("app", ['ui.bootstrap', 'leaflet-directive', 'ngRoute']);


require('./services/proxy.js')(angularInstance);

angularInstance.controller("headerCtrl", function($scope){

 })


template = 'synthese/templates/app.html';

function appCtrl (proxy){
  var ctrl = this;
  
  ctrl.nbObs = "Les 50 dernieres observations";
  proxy.lastObs().then(function(response){
      ctrl.geojson = response.data;

    });
  
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


require('./formObs.js')(angularInstance);
require('./map.js')(angularInstance);
require('./listObs.js')(angularInstance);
require('./detailObs/detailObs.js')(angularInstance);