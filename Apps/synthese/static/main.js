var angularInstance = angular.module("app", ['ui.bootstrap', 'leaflet-directive', 'toaster']);


require('./services/proxy.js')(angularInstance);



template = 'synthese/templates/app.html';

function appCtrl (proxy, toaster){
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
    toaster.pop({type: 'wait', title: "", body:"Recherche des observations en cours"});
    proxy.sendData(form).then(function(response){
      toaster.clear();


      if(response.data.point.features.length + response.data.maille.features.length  < 8000){
          ctrl.geojson = response.data;
          nbObs = ctrl.geojson.point.features.length+ctrl.geojson.maille.features.length
          ctrl.nbObs = nbObs+' observation(s)';
      }else{
        toaster.pop({ 'type': 'error', title: "", body:"Nombre d'observations trop important: affinez la recherche"});
      }

    }, function errorCallBack(){
      toaster.clear();
      toaster.pop({ 'type': 'error', title: "", body:"Une erreur est survenue, merci de faire remonter le bug au gestionnaire de BDD"});
    });
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

  ctrl.onCsvDowload = function(){
    console.log(this.form);
    proxy.downloadCSV(this.form).then(function(response){
      window.location =configuration.URL_APPLICATION+'synthese/uploadscsv/'+response.data;   
    }, function errorCallBack(){
        toaster.pop({ 'type': 'error', title: "", body:"Veuillez effectuer une recherche avant d'exporter en CSV"});
    })

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