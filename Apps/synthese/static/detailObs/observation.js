module.exports = function(angularInstance){

	function observationController($http){
		var obsCtrl = this;
		obsCtrl.currentObsDetails = undefined;

		obsCtrl.loadObsDetails = function(id_synthese){
			$http.get(configuration.URL_APPLICATION+"synthese/detailsObs/"+id_synthese).then(function(response){
				obsCtrl.currentObsDetails = response.data;
			})
		}

		obsCtrl.$onChanges = function(changes){
			if(changes){
				console.log("changes");
				if(changes.idSynthese.currentValue != undefined){
					console.log(changes);
					this.loadObsDetails(changes.idSynthese.currentValue);
				}
			}
		}
	}// END CONTROLLER



var observationTemplate = 'synthese/templates/observation.html';

	angularInstance.component('observation', {
	  controller : observationController,
	  templateUrl : observationTemplate,
	  bindings : {
	  	'idSynthese' : '<',
	  }
	});
}//END WEBPACK