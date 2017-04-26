module.exports = function(angularInstance){

	require('./observation.js')(angularInstance);
	require('./taxonomie.js')(angularInstance);
	require('./reglementation.js')(angularInstance);


	function detailObsController(){
	}



var detailObsTemplate = 'synthese/templates/detailObs.html';

	angularInstance.component('detailObs', {
	  controller : detailObsController,
	  templateUrl : detailObsTemplate,
	  bindings : {
	  	'cdNom' : '<',
	  	'idSynthese' : '<',
	  }
	});
}//END WEBPACK