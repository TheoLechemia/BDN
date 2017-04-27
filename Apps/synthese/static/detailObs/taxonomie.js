module.exports = function(angularInstance){

	require('../spinner/spinner.js')(angularInstance);

	function taxonomieController($http){
		taxCtrl = this;
		taxCtrl.showSpinner = false;

		taxCtrl.loadTaxonomieDetails = function(cdNom){
			taxCtrl.showSpinner = true;
			$http.get(configuration.URL_APPLICATION+"synthese/detailsTaxonomie/"+cdNom).then(function(response){
				taxCtrl.showSpinner = false;
				taxCtrl.currentTaxonomieDetails = response.data;
			});
		}

		taxCtrl.$onChanges = function(changes){
			if(changes){
				if(changes.cdNom.currentValue != undefined){
					this.loadTaxonomieDetails(changes.cdNom.currentValue);
				}
			}
		}
	}//END CONTROLLER



var taxonomieTemplate = 'synthese/templates/taxonomie.html';

	angularInstance.component('taxonomie', {
	  controller : taxonomieController,
	  templateUrl : taxonomieTemplate,
	  bindings : {
	  	'cdNom' : '<',
	  }
	});
}//END WEBPACK