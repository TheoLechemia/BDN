//var app = angular.module("app", ['leaflet-directive', 'ui.bootstrap']);

var app = angular.module("app", ['leaflet-directive', 'ui.bootstrap']).config(function($interpolateProvider){
    $interpolateProvider.startSymbol('%%').endSymbol('%%');
});


app.controller("headerCtrl", function($scope, $http, leafletData){


$scope.search_scientist_name = function(expre, view){
  return $http.get(URL_APPLICATION+"addObs/search_scientist_name/"+view+"/"+expre).then(function(response){ 
    return response.data;
  })
  }

$scope.search_vern_name = function(expre, view){
  return $http.get(URL_APPLICATION+"addObs/search_vern_name/"+view+"/"+expre).then(function(response){ 
    return response.data;
  })
  }



$scope.isLoading = true;



//#######FORMULAIRE ##############


/*   $scope.form = {
    coord : {'lat': null, 'lng':null },
    loc_exact : true,
    code_maille: ""
   }
*/



   $scope.formFlore = {
    'abondance' : null,
    'nb_pied_exact': null,
    'nb_pied_approx': null,
    'stade_dev': null,
   }

   $scope.formFaune = {'type_obs': null,
    'effectif': null,
    'comportement': null,
    'trace': null, 
    'nb_individu':null, 
    'nb_male': null,
    'nb_femelle': null,
    'nb_jeune':null,
    'nb_non_identifie': null,
    }

   $scope.view = 'flore'

   $scope.changeViewFlore = function(){
    $scope.view.flore = !$scope.view.flore;
    $scope.view.faune = !$scope.view.faune;
   }

  $scope.changeViewFaune = function(){
    $scope.view.flore = !$scope.view.flore;
    $scope.view.faune = !$scope.view.faune;
   }



   $scope.isOpen = false;

   $scope.openDate = function(){
      $scope.isOpen = !$scope.isOpen;
   }

   $scope.changeLng = function(){
    $scope.form.coord.lng = $scope.markers.main.lng;
   }
  $scope.changeLat = function(){
    $scope.form.coord.lat = $scope.markers.main.lat;
   }


   $scope.abondance = [
        '1',
        '2-3',
        '4-5',
        '6-50',
        '>50 (<5%)',
        '5-25%',
        '16-25%',
        '26-50%',
        '51-75%',
        '76-100%',
      ]
  $scope.nb_pied_approx = ['<1', '10 - 50', '50 - 100', '100 - 500', '>1000']
  $scope.stade_dev = ['Plantule', 'Juvenile', 'Adulte', 'Bouton', 'Début floraison', 'Plein floraison', 'Fin floraison', 'Début fructification', 'Plein fructification', 'Fin fructification', 'Dissémination', 'Squelette, autre',
                      'Prothale (Ptéridophytes)', 'Sporophyte juvénile (Ptéridophytes)','Sporophyte Adulte (Ptéridophytes)', 'Sporange immature (Ptéridophytes)', 'Sporange matures (Sporophyte)']

  $scope.type_obs= ['Animal mort ou collision','Capture manuelle', 'Chant','Cris','Contact sonore', 'Contact visuel', 'Détection','Empreintes, Traces','Filet','Gîte', 'Nichoir', 'Nid', 'Indices (crottes,...)'];

  $scope.effectif = ['1-5','6-10','11-20','21-50','51-100','101-500','501-1000','> 1000'];

  $scope.comportement = ['Alerte','Alimentation','Colonie avec certaines femelles gestantes','Colonie avec jeunes non volants','Colonie avec jeunes volants','Colonie avec males','Colonie avec mise bas','Repos','Colonie de reproduction','Colonie sans jeunes','Comportement parental','Comportement territorial','Eclosion','Emergence','En chasse','En vol','Estivage','Fuite','Harem','Hibernation','Individus isolés','Léthargie diurne','Léthargie hivernale','Migration','Nidification','Parade nuptiale','Ponte','Reproduction','Transit','Autres']
  $scope.trace = ['Crottes ou crottier','Ecorçage ou frottis','Empreintes','Epiderme','Guano','Nid','Oeufs','Pelage','Pelotes de réjection','Restes alimentaires',"Restes de l'animal",'Terrier','Autres','Larves','Exuvie']




 var completeForm = {'general': $scope.form, 'faune': $scope.formFaune, 'flore': $scope.formFlore};

  $scope.onSubmit = function(protocole, form){
    console.log(form);
    console.log(form.observateur)
/*    $http.post(URL_APPLICATION+'addObs/submit/'+protocole, completeForm).then(function(response){
      console.log(response.data);
    })*/
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

$http.get(URL_APPLICATION+'addObs/loadMailles').success(function(data){
  console.log(data)
  saveGeojsonMaille['data'] = data;
  saveGeojsonMaille['style'] = originStyle;
})

/*$http.get(URL_APPLICATION+"static/data/mailles_1km.geojson").success(function(data){

  saveGeojsonMaille['data'] = data;
  saveGeojsonMaille['style'] = originStyle;
})*/


  $scope.center = { 'lat':16.2412500 , 'lng':-61.5361400 , 'zoom':11 }
  $scope.markers = {
    main: {
        lat: 16.2412500,
        lng: -61.5361400,
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
      $scope.form.coord.lat = args.leafletObject._latlng.lat;
      $scope.form.coord.lng = args.leafletObject._latlng.lng;
   });

   selectedMaille = null;
   $scope.$on('leafletDirectiveGeoJson.click', function(e, args) {
    $scope.form.code_maille = args.model.properties.CODE_1KM;
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
    $scope.form.loc_exact = false;
    $scope.markers = {};
    console.log(saveGeojsonMaille);
    $scope.geojsonMaille = saveGeojsonMaille;
  }

  $scope.switchPoint = function(){
    $scope.form.loc_exact = true;
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
       // container.style.backgroundImage = "url("+configuration.URL_APPLICATION+"/static/images/logo_earth_map.PNG)";
        container.style.width = '50px';
        container.style.height = '50px';
        container.style.border = 'solid white 1px';
        container.style.cursor = 'pointer';
        $(container).attr("data-placement", "right");
        $(container).attr("data-toggle", "tooltip");
        $(container).attr("data-original-title", "Photos aérienne");


        container.onclick = function(){
          if(currentTileMap == "topo"){
         // container.style.backgroundImage = "url("+configuration.URL_APPLICATION+"/static/images/logo_topo_map.PNG)";
          $(container).attr("data-original-title", "Plan");
          map.removeLayer(firstMapTile);
          orthoMap.addTo(map);
          currentTileMap = "earth";
          }
          else{
          container.style.backgroundImage = "url("+configuration.URL_APPLICATION+"/static/images/logo_earth_map.PNG)";
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



