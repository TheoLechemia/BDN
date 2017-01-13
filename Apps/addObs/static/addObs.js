var app = angular.module("app", ['leaflet-directive', 'ui.bootstrap']);


app.controller("headerCtrl", function($scope, $http){

  $scope.test = 'tessssssssst';

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

   $scope.$on('leafletDirectiveMarker.drag', function(e, args) {
      $scope.markers.main.lat = args.leafletObject._latlng.lat;
      $scope.markers.main.lng = args.leafletObject._latlng.lng;
      $scope.form.coord.lat = args.leafletObject._latlng.lat;
      $scope.form.coord.lng = args.leafletObject._latlng.lng;
   });


   $scope.taxons = [{'lb_nom': 'capra ibex', 'nom_vern': 'bouquetin des alpes', 'cd_nom': 12000}, {'lb_nom': 'Iguana Delicatissima', 'nom_vern': 'Iguane des petites Antilles', 'cd_nom': 350755},
                    {'lb_nom': 'Gaiacum Gaiacum', 'nom_vern': 'Gaiac', 'cd_nom': 629786}]

   $scope.form = {
    observateur : null,
    taxon : {'lb_nom': null, 'nom_vern': null, 'cd_nom': null},
    coord : {'lat': null, 'lng':null },
    date : null,
   }

   $scope.view = 'flore'

   $scope.changeViewFlore = function(){
    console.log("heho")
    $scope.view.flore = !$scope.view.flore;
    $scope.view.faune = !$scope.view.faune;
   }
  $scope.changeViewFaune = function(){
    $scope.view.flore = !$scope.view.flore;
    $scope.view.faune = !$scope.view.faune;
   }

   $scope.formFlore = {
    'abondance' : null,
    'nb_pied_exact': null,
    'nb_pied_approx': null,
    'stade_dev': null,
   }

   $scope.formFaune = {}

   $scope.isOpen = false;

   $scope.openDate = function(){
      console.log($scope.form.date);
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

 var completeForm = {'general': $scope.form, 'faune': $scope.formFaune, 'flore': $scope.formFlore};

  $scope.onSubmit = function(protocole){
    $http.post(URL_APPLICATION+'addObs/submit/'+protocole, completeForm).then(function(response){
      console.log(response.data);
    })
  }

 });



 


