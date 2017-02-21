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
  proxy.loadGroup2_inpn().then(function(response){
    ctrl.group2_inpn = response.data;
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


require('./formObs.js')(angularInstance);
require('./map.js')(angularInstance);
require('./listObs.js')(angularInstance);