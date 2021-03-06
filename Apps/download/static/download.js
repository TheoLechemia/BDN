var angularInstance = angular.module("app", ['ui.bootstrap', 'toaster']);

angularInstance.controller("headerCtrl", function($scope){

 })

//PROXY//
proxy = angularInstance.factory('proxy', function proxy($http) {
		return{
			lastObs: function(){
	            return $http.get(CONFIGURATION.URL_APPLICATION+"synthese/lastObs");
				},
			sendData : function(data){
				return $http.post(CONFIGURATION.URL_APPLICATION+"download/getObs", data)
			},

			loadTaxons: function(id_projet, expr){
				return $http.get(CONFIGURATION.URL_APPLICATION+"download/search_taxon_name/"+id_projet+"/"+expr)
			},
			loadCommunes: function(){
				return $http.get(CONFIGURATION.URL_APPLICATION+"synthese/loadCommunes")
			},
			loadForets: function(){
				return $http.get(CONFIGURATION.URL_APPLICATION+"synthese/loadForets")
			},
			loadTypologgie : function(){
				return $http.get(CONFIGURATION.URL_APPLICATION+"synthese/loadTypologgie")
			},
			exportShapeFile : function(data){
				return $http.post(CONFIGURATION.URL_APPLICATION+"synthese/export", data)
			},
			loadTaxonomyHierachy : function(rang_fils, rang_pere, rang_grand_pere, value_rang_grand_pere, value){
				return $http.get(CONFIGURATION.URL_APPLICATION +"synthese/loadTaxonomyHierachy/"+rang_fils+"/"+rang_pere+"/"+rang_grand_pere+"/"+value_rang_grand_pere+"/"+value)
			},
			loadProtocole: function(){
				return $http.get(CONFIGURATION.URL_APPLICATION+"download/loadProtocoles")
			},
			bindNewValues : function(table_field){
 				return $http.get(CONFIGURATION.URL_APPLICATION+"addObs/loadValues/"+table_field)
			}
	  }
	});


// APPP //


template = 'download/templates/app.html';

function appCtrl (proxy, toaster){
  var ctrl = this;
  
  ctrl.nbObs = "Les 50 dernieres observations";
  proxy.lastObs().then(function(response){
      ctrl.geojson = response.data;
    });
  

  proxy.loadCommunes().then(function(response){
      ctrl.communesList = response.data;
  })
  proxy.loadForets().then(function(response){
      ctrl.foretsList = response.data;
  })
  proxy.loadTypologgie().then(function(response){
    ctrl.typologie = response.data;
  }) 
  proxy.loadProtocole().then(function(response){
    ctrl.protocoles = response.data;
  })


  ctrl.formSubmit = function(form){
    ctrl.form = form;
    toaster.pop({type: 'wait', title: "", body:"Téléchargement en cours..."});
    proxy.sendData(form).then(function(response){
    	toaster.clear();
    	toaster.pop('success', "Observations exportées avec succès... Les données vont être téléchargées...", null, 'trustedHtml');
    	window.location =CONFIGURATION.URL_APPLICATION+'download/uploads/'+response.data.filename+".zip";       
    }, function errorCallBack(){
    	toaster.pop('error', " Erreur ! Avez vous séléctionné un projet ? Si oui,  merci de faire remonter le bug au gestionnaire de BDD", null, 'trustedHtml');
    })
  }

  ctrl.changeProtocole = function(protocole){
  	table_field = protocole.bib_champs;

  	if (protocole.table_independante){
  		proxy.bindNewValues(table_field).then(function(response){
  		ctrl.fields = response.data;
  	})
  	}

  }

}

angularInstance.component('app', {

  controller : appCtrl,
  templateUrl : template

});



// FORM


function formControler(proxy, $http, $scope){
	formCtrl = this;
	formCtrl.templateProtocole = null;
	// Modele du formulaire
	formCtrl.form = {
		'selectedProtocole': null,
		'taxon' : {'lb_nom': null },
		'listTaxons' : [],
		'where' : {'code_insee': null, 'nom': null},
		'when' : {'first': null, 'last': null},
		'foret' : {'ccod_frt': null, 'lib_frt': null},
		'taxonomie' : {'rang': null, 'value': null},
		'regne' : null,
		'phylum' : null,
		'classe' : null,
		'ordre': null,
		'famille': null,
		'group2_inpn': null,
		'habitat': {'id':null, 'type':null},
		'protection':null,
		'lr':{'id_statut':null, 'type_statut':null},
		'observateur': {'observateur':null},
		'structure': {'id_organisme': null, 'nom_structure': null},
	}

	formCtrl.child = {'protocoleForm':{}};

	formCtrl.search_taxons = function(id_projet, expr){
	    return proxy.loadTaxons(id_projet,expr).then(function(response){ 
	      return response.data;
	    });
    }



	// à l'envoie du formulaire, on le passe au module pere: APP qui fait la requete ajax sur les geojson et les passe a toute l'appli
	formCtrl.submitForm = function(){
		form = {'globalForm': this.form, 'protocoleForm': this.child.protocoleForm} 
		this.onFormSubmit({$event: {'form': form}})
	}



	//RADIO REGNE
	formCtrl.regneRadio = 'current';
	$('.radiotout').attr("checked");

	$('radio').click(function(){
		$(this).siblings.removeAttr('checked')
	})
	// changement de protocole, change les données de recherche des taxons (faune, flore) depuis le module pere APP
	formCtrl.changeProtocole = function(protocole){
		this.form.taxon = {};
		this.form.listTaxons = [];
		this.newTaxons = [];
		this.showNewTaxons = false;

		this.child={'protocoleForm': {}};
		this.selectedProtocole = protocole;
		if(protocole){
			this.templateProtocole = CONFIGURATION.URL_APPLICATION+"addObs/"+protocole.template;
			console.log(this.templateProtocole);
			currentProtocole = protocole
		}
		else{
			currentProtocole = "Tout"
		}
		this.onProtocoleChange({$event:{protocole:currentProtocole}})
	}




	// Liste des rang taxonomique de la recherche avancée
	formCtrl.regne = ['Animalia', 'Plantae', 'Fungi']
	$scope.phylum = [];
	$scope.ordre = [];
	$scope.classe = [];
	$scope.famille = [];

	// chargement des données des rang taxonomique en ajax
	formCtrl.loadTaxonomyHierachy = function(rang_fils,rang_pere, rang_grand_pere,value_rang_grand_pere, value){
		proxy.loadTaxonomyHierachy(rang_fils,rang_pere,rang_grand_pere,value_rang_grand_pere, value).then(function(response){
			$scope[rang_fils] = response.data;
		})
	}
	

	// UI event for taxonomie
	formCtrl.showTaxonomie = false;




	// ajout à la liste des taxons selectionnés
		formCtrl.showNewTaxons = false;
		formCtrl.newTaxons = []

	 formCtrl.onSelectlbNom = function ($item, $model, $label) {
	 	console.log($item);
	 	this.form.taxon.lb_nom = $item.lb_nom;
 		this.form.listTaxons.push($item.cd_nom);
 	   	if (this.showNewTaxons == false){
			this.showNewTaxons = !this.showNewTaxons;
		}
		this.newTaxons.push({'name':$item.lb_nom, 'cd_nom': $item.cd_nom});

		// on vide les inputs

		setTimeout(function(){
		$("#input_lbnom").val('');
		 $("#input_nomvern").val('');
		}, 1000)

	}
	

		// retirer un taxon de la liste des taxons selectionnés
	formCtrl.removeTaxonEvent = function(cd_nom){
		console.log("remove");	
		this.newTaxons.splice(this.newTaxons.indexOf(cd_nom), 1 );
		this.form.listTaxons.splice(this.newTaxons.indexOf(cd_nom), 1 );
		if (this.newTaxons.length == 0){
			this.showNewTaxons = false;
		}
	}

	// rafrachir l'ensemble des sélections
	formCtrl.onRefreshEvent = function(){
		console.log('refresh');
		this.child = {'protocoleForm': {}};
		this.form = {
		'selectedProtocole': null,
		'taxon' : {'lb_nom': null, 'nom_vern': null, 'cd_nom' : null },
		'listTaxons' : [],
		'where' : {'code_insee': null, 'nom': null},
		'when' : {'first': null, 'last': null},
		'foret' : {'ccod_frt': null, 'lib_frt': null},
		'taxonomie' : {'rang': null, 'value': null},
		'regne' : null,
		'phylum' : null,
		'classe' : null,
		'ordre': null,
		'famille': null,
		'group2_inpn': null,
		'habitat': {'id':null, 'type':null},
		'protection':null,
		'lr':{'id_statut':null, 'type_statut':null},
		'observateur': {'observateur':null},
		'structure': {'id_organisme': null, 'nom_structure': null},
		}

		this.newTaxons = [];
		this.showNewTaxons = false;
	} 

	  formCtrl.checkProtocole  = function(){
	    if(formCtrl.selectedProtocole == undefined){
	      alert("Selectionner un projet")
	    };
	  }

  	// UI event for date picker
  	formCtrl.popup = {
    	first:{ opened : false},
    	last:{opened:false} 
  		};

  	formCtrl.maxDate = new Date();

	formCtrl.open = function(prop) {
		if (prop == "first"){
    		this.popup.first.opened = true;
    	}
    	else {
    		this.popup.last.opened = true;
    	}
  	};


}

var templateForm = CONFIGURATION.URL_APPLICATION+'download/download/templates/formObs.html';


angularInstance.component('formObs', {

  controller : formControler,
  templateUrl : templateForm,
  bindings: {
  	onFormSubmit : '&',
  	taxons : '<',
	communes : '<',
	forets: '<',
	typologie : '<',
	protocoles : '<',
	onProtocoleChange : '&',
	fields : '<',
  }
});