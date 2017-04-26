module.exports = function(angularInstance){

	function taxonomieController($http){
		taxCtrl = this;

		taxCtrl.loadTaxonomieDetails = function(cdNom){
			$http.get(configuration.URL_APPLICATION+"synthese/detailsTaxonomie/"+cdNom).then(function(response){
				taxCtrl.currentTaxonomieDetails = response.data;
			});
		}

		taxCtrl.$onChanges = function(changes){
			if(changes){
				console.log("changes");
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