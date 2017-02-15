module.exports = function(angularInstance){

	templateForm = 'synthese/templates/formObs.html';


	function formCtrl(proxy, $http, $scope){
		ctrl = this;

		// Modele du formulaire
		ctrl.form = {
			who : null,
			lb_nom : {'lb_nom': null, 'cd_nom' : null },
			nom_vern : {'nom_vern': null, 'cd_nom' : null }, 
			where : {'code_insee': null, 'nom': null},
			when : {'first': null, 'last': null},
			foret : {'ccod_frt': null, 'lib_frt': null},
			taxonomie : {'rang': null, 'value': null},
			regne : null,
			phylum : null,
			classe : null,
			ordre: null,
			famille: null,
			group2_inpn: null,
		}

		// à l'envoie du formulaire, on le passe au module pere: APP qui fait la requete ajax sur les geojson et les passe a toute l'appli
		ctrl.submitForm = function(form){
			this.onFormSubmit({$event: {form: form}})
		}


		//RADIO REGNE
		ctrl.regneRadio = 'current';
		$('.radiotout').attr("checked");

		$('radio').click(function(){
			$(this).siblings.removeAttr('checked')
		})
		// changement de protocole, change les données de recherche des taxons (faune, flore)
		ctrl.changeProtocole = function(protocole){
			this.onProtocoleChange({$event:{protocole:protocole}})
		}


		// Liste des rang taxonomique de la recherche avancée
		ctrl.regne = ['Animalia', 'Plantae', 'Fungi']
		$scope.phylum = [];
		$scope.ordre = [];
		$scope.classe = [];
		$scope.famille = [];

		// chargement des données des rang taxonomique en ajax
		ctrl.loadTaxonomyHierachy = function(rang_fils,rang_pere, rang_grand_pere,value_rang_grand_pere, value){
			proxy.loadTaxonomyHierachy(rang_fils,rang_pere,rang_grand_pere,value_rang_grand_pere, value).then(function(response){
				$scope[rang_fils] = response.data;

			})
		}
		

		// UI event for taxonomie
		$scope.showTaxonomie = false;
		// si on fait la recherche taxonomique: on affiche les truc selectionné, et on met à null la recherche par nom de taxon
		ctrl.onTaxonomieChange = function(){
			if ($scope.showTaxonomie == false){
				$scope.showTaxonomie = !$scope.showTaxonomie;
			}
			// on met à null les cd_nom
			this.form.lb_nom.cd_nom = null;
			this.form.lb_nom.lb_nom = null;
			this.form.nom_vern.cd_nom = null;
			// on vide les input de la recherche des taxons
			$("#input_lbnom").val('');
			$("#input_nomvern").val('');
		}
		// si on rempli  un nom de taxon apres avoir faire une recherche par taxonomie, on reinitialise la hierarchie taxo à null;
		ctrl.fillTaxonEvent = function(){
			if($scope.showTaxonomie){
				$scope.showTaxonomie = !$scope.showTaxonomie;
				this.form.regne = null;
				this.form.phylum = null;
				this.form.classe = null;
				this.form.ordre = null;
				this.form.famille = null;
			}
		}

	  	// UI event for date picker
	  		ctrl.popup = {
	    	first:{ opened : false},
	    	last:{opened:false} 
	  	};
		ctrl.open = function(prop) {
			if (prop == "first"){
	    		this.popup.first.opened = true;
	    	}
	    	else {
	    		this.popup.last.opened = true;
	    	}
	  	};


	}

	angularInstance.component('formObs', {

	  controller : formCtrl,
	  templateUrl : templateForm,
	  bindings: {
	  	taxons : '<',
	  	communes : '<',
	  	forets: '<',
	  	onFormSubmit : '&',
	  	onProtocoleChange : '&',
	  }
	});
}