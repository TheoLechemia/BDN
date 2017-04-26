module.exports = function(angularInstance){

	function reglementationController($http){
		reglCtrl = this;

		reglCtrl.loadReglementationDetails = function(cdNom){
			$http.get(configuration.URL_APPLICATION+"synthese/detailsReglementation/"+cdNom).then(function(response){
				reglCtrl.currentRegDetails = response.data;
			});
		}

		reglCtrl.$onChanges = function(changes){
			if(changes){
				console.log("changes");
				if(changes.cdNom.currentValue != undefined){
					this.loadReglementationDetails(changes.cdNom.currentValue);
				}
			}
		}
	}



var reglementationTemplate = 'synthese/templates/reglementation.html';

	angularInstance.component('reglementation', {
	  controller : reglementationController,
	  templateUrl : reglementationTemplate,
	  bindings : {
	  	'cdNom' : '<',
	  }
	});
}//END WEBPACK