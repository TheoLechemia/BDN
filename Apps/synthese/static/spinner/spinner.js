module.exports = function(angularInstance){

	var template = 'synthese/spinner/spinner.html';

	angularInstance.component('spinner', {

	  'templateUrl' :template ,
	  'bindings':{
	  	'showSpinner': '<'
	  }


	});
}