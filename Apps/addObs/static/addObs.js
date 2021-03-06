//var app = angular.module("app", ['leaflet-directive', 'ui.bootstrap']);

var angularInstance = angular.module("app", ['leaflet-directive', 'ui.bootstrap', 'toaster'])

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

function formController($http, toaster){
  formCtrl = this;


  formCtrl.bindNewValues = function(protocole){
    table = protocole.bib_champs
    $http.get(configuration.URL_APPLICATION+"addObs/loadValues/"+table).then(function(response){ 
      appCtrl.fields = response.data;
    });
  };

  // regex pour ne pas mettre de point dans les input des coordonnées
/*$('.coord').keypress(function(e){
  console.log(e)
  console.log(e.which)
  if (e.which==46 || e.which < 48 || e.which > 57 || e.wich != 8 ){
    return false
  }
})*/

$('.coord').on('keypress', function(e){
  console.log(e.which)
  console.log(e.target.value)
  return e.metaKey || // cmd/ctrl
    e.which <= 0 || // arrow keys
    e.which == 8 || // delete key
    (e.which == 44 &&  e.target.value.indexOf('.') == -1 ) ||
    /[0-9]/.test(String.fromCharCode(e.which)); // numbers
})

/*$('.coord').on('keypress', function(e){
  console.log(e.which)
  return //e.metaKey || // cmd/ctrl
    e.which <= 0 || // arrow keys
    e.which == 8 || // delete key
    (e.which == 44 &&  e.target.value.indexOf('.') == -1 ) || // virgule si il y a deja un point dans le chiffre
    /[0-9]/.test(String.fromCharCode(e.which));
})*/


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
            formCtrl.formSuccessfullySent = true;
            toaster.success({title: "OK", body:"Observation enregistrée avec succès"});

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
          setTimeout(function(){
            formCtrl.formSuccessfullySent = false;
             }, 200);
          // on reset les actions sur les champs du formulaire pour l'affichage des erreurs
          form.observateur.$pristine= true;
          form.lb_nom.$pristine = true;
          form.date.$pristine = true;
          formCtrl.validationAttempt = false;
    }, function erroCallBack(){
    	toaster.error({title: "Attention", body:"Une erreur s'est produite, merci de faire remonter le bug au gestionnaire de BDD"})
    })
    }
    else{
       toaster.error({title: "Attention", body:"Le formulaie est incomplet ou comporte des erreurs"})
    }
  }// END onSubmit


  // EVENT between components
    formCtrl.onCoordChange = function(coord){
    this.globalForm.coord = coord;
  }

  formCtrl.onSwitchLayer = function(){
    this.globalForm.loc_exact = !this.globalForm.loc_exact;
    this.showCoord = !this.showCoord;
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
      alert("Selectionner un projet")
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

// #########################END FORMULAIRE #############################


// ######################### MAP ####################################


function mapController($http, $scope, leafletData, toaster){
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

    this.layers = configuration.MAP.LAYERS;




  var saveGeojsonMaille = {};
  this.geojsonMaille = {};
  this.saveMarkers = {}


  mapCtrl.center = { 'lat':configuration.MAP.COORD_CENTER.Y , 'lng':configuration.MAP.COORD_CENTER.X , 'zoom':configuration.MAP.ZOOM_LEVEL }
  mapCtrl.$onInit= function(){
    this.markers = {
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
    this.saveMarkers = this.markers;
  }

  // EVENT

var currentMaille = null;
var loc_exact = true;

//load the maille of the current boudingBox with Ajax
  function loadMailles(){
        leafletData.getMap("map").then(
        function (map) {
            if (map.getZoom() >= 13 && !loc_exact) {
              bounds = map.getBounds()
              boundingBox = bounds.toBBoxString();
              if(currentMaille){
                map.removeLayer(currentMaille);
              }
              $http.get(configuration.URL_APPLICATION+'addObs/load_bounding_box_mailles/'+boundingBox).then(function(response){
                  currentMaille = {};
                  currentMaille['data'] = response.data;
                  currentMaille['style'] = originStyle;
                  mapCtrl.geojsonMaille = currentMaille;
              })
            };
        }
    );
  }

// on move end, reload mailles
  $scope.$on('leafletDirectiveMap.moveend', function(e, args){
    loadMailles();
  })


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
    var id_maille = args.model.properties.id_maille;
    mapCtrl.updateCodeMaille({
      $event : {'code' :id_maille}
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


  mapCtrl.switchMaille = function(){
    toaster.pop({ 'type': 'info', title: "", body:"Zoomer pour afficher les mailles"});
    loc_exact = false;
    this.markers={};
    loadMailles();
    this.switchLayer();
  }

  mapCtrl.switchPoint = function(){
    loc_exact = true;
    this.switchLayer();
    mapCtrl.geojsonMaille = {};
    mapCtrl.markers = this.saveMarkers;
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













 


