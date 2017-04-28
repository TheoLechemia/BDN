//var app = angular.module("app", ['leaflet-directive', 'ui.bootstrap']);

var angularInstance = angular.module("app", ['leaflet-directive', 'ui.bootstrap'])

angularInstance.config(function($logProvider){
  $logProvider.debugEnabled(false);
});



function appController($http, leafletData){
  appCtrl = this;

    $http.get(configuration.URL_APPLICATION+"addObs/loadProtocoles").then(function(response){ 
      appCtrl.protocole = response.data;
    })

}// END CRTL

template = 'addObs/templates/app.html';
angularInstance.component('app', {

  controller : appController,
  templateUrl : template

});



//#######FORMULAIRE ##############

function formController($http){
  formCtrl = this;


  formCtrl.bindNewValues = function(protocole){
    table = protocole.bib_champs
    $http.get(configuration.URL_APPLICATION+"addObs/loadValues/"+table).then(function(response){ 
      appCtrl.fields = response.data;
    });
  };




  formCtrl.search_taxon_name = function(expre, selectedProtocole){
    return $http.get(configuration.URL_APPLICATION+"addObs/search_taxon_name/"+selectedProtocole.nom_schema+"/"+expre).then(function(response){ 
      return response.data;
    })
    }

    formCtrl.onNameSubmit = function($item, $model, $label, $event){
      this.globalForm.taxon.nom_valide = $item.nom_valide;
      this.globalForm.taxon.cd_ref = $item.cd_ref;
    }

  formCtrl.isLoading = true;
  formCtrl.showCoord = true;


   formCtrl.globalForm = {
    'coord' : {'lat': configuration.MAP.COORD_CENTER.Y, 'lng':configuration.MAP.COORD_CENTER.X },
    'loc_exact' : true,
    'code_maille': null,
    'commentaire': null,
    'comm_loc': null,
   }


   formCtrl.child = {'protocoleForm':{}};

   //DATE UI EVENT

   formCtrl.maxDate = new Date();

   formCtrl.isOpen = false;

   formCtrl.openDate = function(){
      formCtrl.isOpen = !formCtrl.isOpen;
   }

  //  formCtrl.changeLng = function(){
  //   formCtrl.globalForm.coord.lng = formCtrl.markers.main.lng;
  //  }
  // formCtrl.changeLat = function(){
  //   formCtrl.globalForm.coord.lat = formCtrl.markers.main.lat;
  //  }



 formCtrl.validationAttempt = false;

  formCtrl.onSubmit = function(form){
    var completeForm = {'protocole': formCtrl.selectedProtocole, 'general': formCtrl.globalForm, 'protocoleForm': formCtrl.child.protocoleForm};
    formCtrl.validationAttempt = true;
    console.log(completeForm);

    console.log(form);

     console.log(form.$valid);
     var loc_exact = this.globalForm.loc_exact;

    if (form.$valid){
          $http.post(configuration.URL_APPLICATION+'addObs/submit/', completeForm).then(function(response){
          if(response.status == 200){
            formCtrl.formSuccessfullySent = true;
            //angular.copy({},form);
            // on reset tous les champs
            var saveCoord = formCtrl.globalForm.coord;
            var saveMaille = formCtrl.globalForm.code_maille;
            var saveObservateur = formCtrl.globalForm.observateur;
            formCtrl.globalForm = {
                    'coord' : saveCoord,
                    'loc_exact' : loc_exact,
                    'code_maille': saveMaille,
                    'observateur' : saveObservateur,
                    'date': null,
                    'taxon': null,
                    'commentaire': null,
                    'comm_loc': null,
                   }

          formCtrl.child.protocoleForm = {};
          }
          setTimeout(function(){
            formCtrl.formSuccessfullySent = false;
             }, 200);
          // on reset les actions sur les champs du formulaire pour l'affichage des erreurs
          form.observateur.$pristine= true;
          form.lb_nom.$pristine = true;
          form.date.$pristine = true;
          formCtrl.validationAttempt = false;

    })
    }
  }// END onSubmit


  // EVENT between components
    formCtrl.onCoordChange = function(coord){
    this.globalForm.coord = coord;
  }

  formCtrl.onSwitchLayer = function(){
    this.globalForm.loc_exact = !this.globalForm.loc_exact;
    console.log(this.showCoord);
    this.showCoord = !this.showCoord;
    console.log(this.showCoord);  
  }

  formCtrl.onCodeMailleChange = function(code){
    this.globalForm.code_maille = code;
  }

  formCtrl.$onChanges = function(changes){
      if(changes.coord){
        this.globalForm.coord = changes.coord.currentValue;
      }
  }

   formCtrl.checkProtocole  = function(){
    if(formCtrl.selectedProtocole == undefined){
      alert("Selectionner un protocole")
    };
  }

}// END CTRL


templateForm = 'addObs/templates/form.html';
angularInstance.component('formAdd', {

  controller : formController,
  templateUrl : templateForm,
  bindings :{
    protocole: '<',
    fields : '<',
  }

});






function mapController($http, $scope){
  mapCtrl = this;
  var originStyle = {
    "color": "#000000",
    "weight": 1,
    "fillOpacity": 0
  };

var selectedStyle = {
  'color':'#ff0000',
   'weight':3
  }



var saveGeojsonMaille = {};
mapCtrl.geojsonMaille = {};

// load Mailles

$http.get(configuration.URL_APPLICATION+'addObs/loadMailles').success(function(data){
  console.log(data)
  saveGeojsonMaille['data'] = data;
  saveGeojsonMaille['style'] = originStyle;
})



  mapCtrl.center = { 'lat':configuration.MAP.COORD_CENTER.Y , 'lng':configuration.MAP.COORD_CENTER.X , 'zoom':configuration.MAP.ZOOM_LEVEL }
  mapCtrl.$onInit= function(){
    mapCtrl.markers = {
      main: {
          lat: mapCtrl.y,
          lng: mapCtrl.x,
          draggable: true,
          icon : { 
            iconUrl: configuration.URL_APPLICATION+'/static/lib/leaflet/images/marker-icon.png',
            shadowUrl: configuration.URL_APPLICATION+'/static/lib/leaflet/images/marker-shadow.png',
            iconSize:    [25, 41],
            iconAnchor:  [12, 41],
            popupAnchor: [1, -34],
            tooltipAnchor: [16, -28],
            shadowSize:  [41, 41]
          }
      }
    }
    var saveMarkers = mapCtrl.markers;
  }

  // EVENT

  // init marker


   $scope.$on('leafletDirectiveMarker.drag', function(e, args) {
      var coord = {'lat':args.leafletObject._latlng.lat, 'lng':args.leafletObject._latlng.lng }
      mapCtrl.updateCoordinates({
        $event : {'coord' :coord}
      });
      mapCtrl.markers.main.lat = args.leafletObject._latlng.lat;
      mapCtrl.markers.main.lng = args.leafletObject._latlng.lng;

      saveMarkers = mapCtrl.markers;
   });

   selectedMaille = null;
   $scope.$on('leafletDirectiveGeoJson.click', function(e, args) {

    var code_maille = args.model.properties.code_1km;
    mapCtrl.updateCodeMaille({
      $event : {'code' :code_maille}
    })

    //set style
      if (!selectedMaille){
          args.leafletObject.setStyle(selectedStyle)
          selectedMaille = args.leafletObject;
      }else{
        selectedMaille.setStyle(originStyle);
        args.leafletObject.setStyle(selectedStyle);
        selectedMaille = args.leafletObject;
      }
      
    });

  var loc_exact = true;
  mapCtrl.switchMaille = function(){
    this.markers={};
    this.switchLayer();
    mapCtrl.geojsonMaille = saveGeojsonMaille;
  }

  mapCtrl.switchPoint = function(){
    loc_exact = true;
    this.switchLayer();
    mapCtrl.geojsonMaille = {};
    mapCtrl.markers = saveMarkers;
  }

  mapCtrl.$onChanges = function(changes){
    if (changes.y){
      mapCtrl.markers.main.lat = changes.y.currentValue;
    }
    if (changes.x){
      mapCtrl.markers.main.lng = changes.x.currentValue;
    }
  }

}// END CTRL


templateMap = 'addObs/templates/map.html';
angularInstance.component('leafletMap', {

  controller : mapController,
  templateUrl : templateMap,
  bindings:{
    updateCoordinates: '&',
    switchLayer : '&',
    updateCodeMaille:'&',
    x: '<',
    y: '<',
  }

});













 


