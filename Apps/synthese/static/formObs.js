module.exports = function(angularInstance){

function formControler(proxy, $http, $scope){
	formCtrl = this;

	// Modele du formulaire
	formCtrl.form = {
		'selectedProtocole': null,
		'searchRegne': undefined,
		'taxon' : {'lb_nom': null},
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

	// à l'envoie du formulaire, on le passe au module pere: APP qui fait la requete ajax sur les geojson et les passe a toute l'appli
	formCtrl.submitForm = function(form){
		this.onFormSubmit({$event: {form: form}})
	}

	formCtrl.search_taxons = function($viewValue, id_projet) {
		if(id_projet === undefined) id_projet = 99999;
		return proxy.loadTaxons($viewValue, id_projet)
			.then(function(response){
				return response.data;
		})
	}

	//RADIO REGNE
	formCtrl.regneRadio = 'current';
	$('.radiotout').attr("checked");

	$('radio').click(function(){
		$(this).siblings.removeAttr('checked')
	})
	// changement de protocole, change les données de recherche des taxons (faune, flore) depuis le module pere APP
	this.changeProtocole = function(protocole){
		if(protocole){
			currentProtocole = protocole
		}
		this.onProtocoleChange({$event:{'protocole':currentProtocole}})
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


	// si on fait la recherche taxonomique: on affiche les trucs selectionnés, et on met à null la recherche par nom de taxon
	formCtrl.onTaxonomieChange = function(){
		if (this.showTaxonomie == false){
			this.showTaxonomie = !$scope.showTaxonomie;
		}
		// on met à null les cd_nom et vide le tableau de cd_nom du formulaire
		this.form.taxon.cd_nom = null;
		this.form.taxon.lb_nom = null;
		this.form.taxon.nom_vern = null;
		this.form.listTaxons = [];
		this.newTaxons = [];

		// on vide les input de la recherche des taxons
		$("#input_lbnom").val('');
		$("#input_nomvern").val('');
		// on chache eventuellement la liste des taxons selectionnées
		this.showNewTaxons = false;
	}
	// si on rempli  un nom de taxon apres avoir faire une recherche par taxonomie, on reinitialise la hierarchie taxo à null;
	formCtrl.fillTaxonEvent = function(){
		if(this.showTaxonomie){
			this.showTaxonomie = !$scope.showTaxonomie;
			this.form.regne = null;
			this.form.phylum = null;
			this.form.classe = null;
			this.form.ordre = null;
			this.form.famille = null;
		}
	} 

	//synchronisation des deux inputs et ajout du cd_nom selectionné dans la liste de cd_nom du formulaire
	// et ajout à la liste des taxons selectionnés
		formCtrl.showNewTaxons = false;
		formCtrl.newTaxons = []

	 formCtrl.onSelectlbNom = function ($item, $model, $label) {
	 	   this.form.listTaxons.push($item.cd_nom);
	 	   this.form.taxon.lb_nom = $item.lb_nom;

	 	   	if (this.showNewTaxons == false){
				this.showNewTaxons = !this.showNewTaxons;
			}
			this.newTaxons.push({'name':this.form.taxon.lb_nom, 'cd_nom': this.form.taxon.cd_nom});

			// on vide les inputs

			setTimeout(function(){
			$("#input_lbnom").val('');
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
		this.form = {
		'selectedProtocole': null,
		'searchRegne': undefined,
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

		this.newTaxons = [];
		this.showNewTaxons = false;
	} 

  	// UI event for date picker
  	formCtrl.maxDate = new Date()

  	formCtrl.popup = {
    	first:{ opened : false},
    	last:{opened:false} 
  		};


	formCtrl.open = function(prop) {
		if (prop == "first"){
    		this.popup.first.opened = true;
    	}
    	else {
    		this.popup.last.opened = true;
    	}
  	};

}// END CONTROLLER

var templateForm = 'synthese/templates/formObs.html';


angularInstance.component('formObs', {

  controller : formControler,
  templateUrl : templateForm,
  bindings: {
  	onFormSubmit : '&',
	communes : '<',
	forets: '<',
	typologie : '<',
	protocoles : '<',
	onProtocoleChange : '&'
  }
});

}// END WEBPACK