module.exports = function(angularInstance){

proxy = angularInstance.factory('proxy', function proxy($http) {
		return{
			lastObs: function(){
	            return $http.get(configuration.URL_APPLICATION+"synthese/lastObs");
				},
			sendData : function(data){
				return $http.post(configuration.URL_APPLICATION+"synthese/getObs", data)
			},

			loadTaxons: function(expre, protocole){
				return $http.get(configuration.URL_APPLICATION+"synthese/loadTaxons/"+expre+"/"+protocole)
			},
			loadCommunes: function(){
				return $http.get(configuration.URL_APPLICATION+"synthese/loadCommunes")
			},
			loadForets: function(){
				return $http.get(configuration.URL_APPLICATION+"synthese/loadForets")
			},
			loadTypologgie : function(){
				return $http.get(configuration.URL_APPLICATION+"synthese/loadTypologgie")
			},
			exportShapeFile : function(data){
				return $http.post(configuration.URL_APPLICATION+"synthese/export", data)
			},
			loadTaxonomyHierachy : function(rang_fils, rang_pere, rang_grand_pere, value_rang_grand_pere, value){
				return $http.get(configuration.URL_APPLICATION +"synthese/loadTaxonomyHierachy/"+rang_fils+"/"+rang_pere+"/"+rang_grand_pere+"/"+value_rang_grand_pere+"/"+value)
			},
			loadProtocole: function(){
				return $http.get(configuration.URL_APPLICATION+"synthese/loadProtocoles")
			},
			downloadCSV: function(form){
				return $http.post(configuration.URL_APPLICATION+'synthese/downloadCSV', form)
			}			
		}
	  });
}