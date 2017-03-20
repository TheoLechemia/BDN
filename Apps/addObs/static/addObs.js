//var app = angular.module("app", ['leaflet-directive', 'ui.bootstrap']);

var app = angular.module("app", ['leaflet-directive', 'ui.bootstrap']).config(function($interpolateProvider){
    $interpolateProvider.startSymbol('%%').endSymbol('%%');
});


app.controller("headerCtrl", function($scope, $http, leafletData){

$http.get(configuration.URL_APPLICATION+"addObs/loadProtocoles").then(function(response){ 
    $scope.protocole = response.data;
  })


$scope.search_scientist_name = function(expre, selectedProtocole){
  console.log(selectedProtocole);
  return $http.get(configuration.URL_APPLICATION+"addObs/search_scientist_name/"+selectedProtocole.nom_schema+"/"+expre).then(function(response){ 
    return response.data;
  })
  }

$scope.search_vern_name = function(expre, selectedProtocole){
  return $http.get(configuration.URL_APPLICATION+"addObs/search_vern_name/"+selectedProtocole.nom_schema+"/"+expre).then(function(response){ 
    return response.data;
  })
  }

$scope.bindNewValues = function(protocole){
  table = protocole.bib_champs
  $http.get(configuration.URL_APPLICATION+"addObs/loadValues/"+table).then(function(response){ 
    $scope.fields = response.data;
  });
};


$scope.isLoading = true;
$scope.showCoord = true;



//#######FORMULAIRE ##############


   $scope.globalForm = {
    'coord' : {'lat': null, 'lng':null },
    'loc_exact' : true,
    'code_maille': null,
    'commentaire': null,
    'comm_loc': null,
   }


   $scope.child = {'protocoleForm':{}};


   $scope.isOpen = false;

   $scope.openDate = function(){
      $scope.isOpen = !$scope.isOpen;
   }

   $scope.changeLng = function(){
    $scope.globalForm.coord.lng = $scope.markers.main.lng;
   }
  $scope.changeLat = function(){
    $scope.globalForm.coord.lat = $scope.markers.main.lat;
   }



 $scope.validationAttempt = false;

  $scope.onSubmit = function(form){
    var completeForm = {'protocole': $scope.selectedProtocole, 'general': $scope.globalForm, 'protocoleForm': $scope.child.protocoleForm};
    $scope.validationAttempt = true;
    console.log(completeForm);

    console.log(form);

     console.log(form.$valid);

    if (form.$valid){
          $http.post(configuration.URL_APPLICATION+'addObs/submit/', completeForm).then(function(response){
          if(response.status == 200){
            $scope.formSuccessfullySent = true;
            //angular.copy({},form);
            // on reset tous les champs
            var saveCoord = $scope.globalForm.coord;
            var saveMaille = $scope.globalForm.code_maille;
            $scope.globalForm = {
                    'coord' : saveCoord,
                    'loc_exact' : loc_exact,
                    'code_maille': saveMaille,
                    'observateur' : null,
                    'date': null,
                    'taxon': null,
                    'commentaire': null,
                    'comm_loc': null,
                   }
/*            $scope.formFlore = resetFormFlore;
            $scope.formFaune = resetFormFaune;*/
          $scope.child.protocoleForm = {};
          }

          setTimeout(function(){
            $scope.formSuccessfullySent = false;
             }, 200);
          // on reset les actions sur les champs du formulaire pour l'affichage des erreurs
          form.observateur.$pristine= true;
          form.lb_nom.$pristine = true;
          form.date.$pristine = true;
          $scope.validationAttempt = false;

    })
    }
  }



//##########################################################
//####################### MAP ##############################
//##########################################################



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
$scope.geojsonMaille = {};

// load Mailles

$http.get(configuration.URL_APPLICATION+'addObs/loadMailles').success(function(data){
  console.log(data)
  saveGeojsonMaille['data'] = data;
  saveGeojsonMaille['style'] = originStyle;
})

/*$http.get(configuration.URL_APPLICATION+"static/data/mailles_1km.geojson").success(function(data){

  saveGeojsonMaille['data'] = data;
  saveGeojsonMaille['style'] = originStyle;
})*/


  $scope.center = { 'lat':configuration.MAP.COORD_CENTER.Y , 'lng':configuration.MAP.COORD_CENTER.X , 'zoom':configuration.MAP.ZOOM_LEVEL }
  $scope.markers = {
    main: {
        lat: configuration.MAP.COORD_CENTER.Y,
        lng: configuration.MAP.COORD_CENTER.X,
        draggable: true,
        icon : { 
          iconUrl: '/static/lib/leaflet/images/marker-icon.png',
          shadowUrl: '/static/lib/leaflet/images/marker-shadow.png',
          iconSize:    [25, 41],
          iconAnchor:  [12, 41],
          popupAnchor: [1, -34],
          tooltipAnchor: [16, -28],
          shadowSize:  [41, 41]
        }
    }
  }
  var saveMarkers = $scope.markers;

  // EVENT

   $scope.$on('leafletDirectiveMarker.drag', function(e, args) {
      $scope.markers.main.lat = args.leafletObject._latlng.lat;
      $scope.markers.main.lng = args.leafletObject._latlng.lng;
      $scope.globalForm.coord.lat = args.leafletObject._latlng.lat;
      $scope.globalForm.coord.lng = args.leafletObject._latlng.lng;
   });

   selectedMaille = null;
   $scope.$on('leafletDirectiveGeoJson.click', function(e, args) {

    $scope.globalForm.code_maille = args.model.properties.code_1km;

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
  $scope.switchMaille = function(){
    loc_exact = false;
    $scope.globalForm.loc_exact = loc_exact;
    $scope.markers = {};
    $scope.showCoord = false;
    console.log(saveGeojsonMaille);
    $scope.geojsonMaille = saveGeojsonMaille;
  }

  $scope.switchPoint = function(){
    loc_exact = true;
    $scope.showCoord = true;
    $scope.globalForm.loc_exact = loc_exact;
    $scope.geojsonMaille = {};
    $scope.markers = saveMarkers;
  }

// google map layer switcher
leafletData.getMap()
            .then(function(map) {
      console.log(map)
      var LayerControl = L.Control.extend({

      options: {
        position: 'bottomleft' 
      },

    onAdd: function (map) {
        currentTileMap = "topo";
        var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
     
        container.style.backgroundColor = 'white';
       // container.style.backgroundImage = "url("+configurationuration.configuration.URL_APPLICATION+"/static/images/logo_earth_map.PNG)";
        container.style.width = '50px';
        container.style.height = '50px';
        container.style.border = 'solid white 1px';
        container.style.cursor = 'pointer';
        $(container).attr("data-placement", "right");
        $(container).attr("data-toggle", "tooltip");
        $(container).attr("data-original-title", "Photos aérienne");


        container.onclick = function(){
          if(currentTileMap == "topo"){
         // container.style.backgroundImage = "url("+configurationuration.configuration.URL_APPLICATION+"/static/images/logo_topo_map.PNG)";
          $(container).attr("data-original-title", "Plan");
          map.removeLayer(firstMapTile);
          orthoMap.addTo(map);
          currentTileMap = "earth";
          }
          else{
          container.style.backgroundImage = "url("+configuration.configuration.URL_APPLICATION+"/static/images/logo_earth_map.PNG)";
          $(container).attr("data-original-title", "Photos aérienne");
          map.removeLayer(orthoMap);
          firstMapTile.addTo(map);
          currentTileMap = "topo";
          }
        }
        return container;
      }
});
    });





 });


