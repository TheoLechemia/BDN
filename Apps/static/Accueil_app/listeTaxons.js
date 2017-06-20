console.log('yooooo')

var angularApp = angular.module("app", ['ui.router', 'ngTable']);


angularApp.config([ '$stateProvider', '$urlServiceProvider', function($stateProvider, $urlServiceProvider) {

	$urlServiceProvider.rules.otherwise({ state: 'app' });
	$stateProvider.state('app', {
	    url: '/',
	    component: 'app',
  });

	$stateProvider.state('listeTaxons', {
	    url: '/listeTaxons',
	    component: 'listeTaxons',
  });

}]);



templateApp = configuration.URL_APPLICATION+'static/Accueil_app/app.html';
angularApp.component('app', {

  controller : appController,
  templateUrl : templateApp,
  bindings: {}

  });

function appController($http){
	var ctrl = this;
	this.$onInit = function(){
		$http.get(configuration.URL_APPLICATION+'getStats')
			.then(function(response){
				ctrl.stat = response.data;
			})
	}

}



templateListe = configuration.URL_APPLICATION+'static/Accueil_app/listeTaxons.html';
angularApp.component('listeTaxons', {

  controller : listController,
  templateUrl : templateListe,
  bindings: {}

  });

function listController($http, NgTableParams){
	var listCtrl = this;
	listCtrl.tableParams = {};

	this.$onInit = function(){


		$http.get(configuration.URL_APPLICATION+'getAllTaxons')
			.then(function(response){
				listCtrl.taxons = response.data;

				listCtrl.tableParams = new NgTableParams({
					count:50,
					sorting: {nb:'desc'}
				}, { dataset: listCtrl.taxons});
			})



	}

}