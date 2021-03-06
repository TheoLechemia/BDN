var angularApp = angular.module("app", ['ui.router', 'ngSanitize', 'toaster', 'ngAnimate', 'ngCookies']);
angularApp.config([ '$stateProvider', '$urlServiceProvider', function($stateProvider, $urlServiceProvider) {

	$urlServiceProvider.rules.otherwise({ state: 'listProj' });

	$stateProvider.state('listProj', {
	    url: '/liste',
	    component: 'listProj',
  });

	$stateProvider.state('addProject', {
	    url: '/addProject',
	    component: 'metaApp',
  });

  $stateProvider.state('editProject', {
	    url: '/project/:id',
	    component: 'project',
  });

}]);

function metaController ($http, toaster, $cookies){
	metaCtrl = this;
	var initialForm = {
		'nom_projet': null,
		'nom_bdd': null,
		'theme_principal': null,
		'service': null,
		'partenaires': null,
		'subvention_commande': null,
		'duree': null,
		'initiateur': null,
		'producteur': null,
		'commentaire': null,
		'table_independante': false,
		'saisie_possible': false,
	};

	metaCtrl.token = $cookies.get('token')

	metaCtrl.projectForm = angular.copy(initialForm);

	metaCtrl.showDataModel = true;
	metaCtrl.dataModelFormIsValid = true;

	metaCtrl.regex = new RegExp('^([a-z]+(_*[0-9]*)*)+$')

	metaCtrl.bind_table_indep = function(){
			if(this.projectForm.saisie_possible == true){
				this.projectForm.table_independante = true;
		}
	}

	metaCtrl.fieldForm = [];

	metaCtrl.isValidChildForm = function(isValid){
		console.log("is valid ?", isValid)
		if(isValid){
			this.showDataModel = !this.showDataModel
		}
		this.dataModelFormIsValid = isValid;
	}


	

	metaCtrl.sendData = function(e, form){
		btn = e.target;
		btn.classList.add('disabled');
		data = {'projectForm': this.projectForm, 'fieldForm': this.fieldForm}
		console.log(form);
		console.log(this.dataModelFormIsValid)
		if(form.$valid && this.dataModelFormIsValid){
			toaster.pop({type: 'wait', title: "Création du projet", body:"Cela peut prendre un peu de temps"});
			$http.post(configuration.URL_APPLICATION+'meta/addProject', data).then(function(response){
			// reset le form
			metaCtrl.projectForm = angular.copy(initialForm);
			toaster.clear();
			btn.classList.remove('disabled');
			toaster.success({title: "OK", body:"Projet ajouté avec succès"});
			}, function errorCallBack(response){
				console.log(response)
				toaster.clear();
				toaster.error({title: "Attention", body:"Un erreur s'est produite, contactez le gestionnaire de base de données"})

		});
		}else{
			toaster.pop({type: 'error', title: "Attention", body:"Le formulaire contient des erreurs"});
			btn.classList.remove('disabled');
		}	
	}

}// END CONTROLLER

templateMeta = configuration.URL_APPLICATION+'meta/meta/meta.html';
angularApp.component('metaApp', {

  controller : metaController,
  templateUrl : templateMeta,
  bindings:{
  }

});

// LISTE DES PROTOCOLES


function listProtController($http, $cookies){
	listCtrl = this;

	listCtrl.$onInit = function(){
		this.authLevel = parseInt($cookies.get('auth_level'));
		console.log(this.authLevel);
	}

	$http.get(configuration.URL_APPLICATION+'meta/listProject').then(function(response){
		listCtrl.projets = response.data;
	})
}

template = configuration.URL_APPLICATION+'meta/meta/liste_proj.html';
angularApp.component('listProj', {

  controller :listProtController ,
  templateUrl : template,
  bindings:{
  }

});


// Une fiche projet
angularApp.component('project', {

  controller :projectController ,
  templateUrl : templateMeta,
  bindings:{
  	'data': '<',

  }

});

function projectController($stateParams, $http, toaster){
	prjCtrl = this;
	prjCtrl.currentValues = null;
	this.showDataModel = true;


	prjCtrl.$onInit = function(){
		// ON INIT DISABLE les inputs qu'il ne faut pas modifier

		var toDisable = document.getElementsByClassName('toDisable');
		Array.from(toDisable).forEach(function(el){
			el.setAttribute('disabled', 'true');
		})

		finalButton = document.getElementById('finalButton');
		finalButton.textContent = "Editer le projet";

		//get les donnes du projet
		$http.get(configuration.URL_APPLICATION+"meta/getProject/"+$stateParams.id).then(function(response){
			prjCtrl.projectForm = response.data.projet;
			prjCtrl.fieldForm = response.data.formulaire;
			// s'il ny a pas de formulaire on initialise le formulaire commme un tableau vide;
			if(prjCtrl.fieldForm != null){
				prjCtrl.showDataModel = true;
				prjCtrl.initialNbField = prjCtrl.fieldForm.length;	
			}else{
				prjCtrl.fieldForm = [];
				prjCtrl.initialNbField = 0;
			}
			console.log(prjCtrl.initialNbField);
		})
	}

	prjCtrl.isValidChildForm = function(isValid){
		console.log("is valid ?", isValid)
		if(isValid){
			this.showDataModel = !this.showDataModel
		}
		this.dataModelFormIsValid = isValid;
	}

	prjCtrl.sendData = function(event, form){
		var nbNewField = this.fieldForm.length - this.initialNbField;
		console.log(nbNewField);
		data = {'projectForm': this.projectForm, 'fieldForm': this.fieldForm, 'nbNewField': nbNewField }	
		console.log(data);
		console.log(form.$valid)
		if(form.$valid && this.dataModelFormIsValid){
			$http.post(configuration.URL_APPLICATION+'meta/editProject', data).then(function(response){
				// update le nb de field
				prjCtrl.initialNbField = prjCtrl.fieldForm.length;
				toaster.success({title: "OK", body:"Projet edité avec succès"});
			}, function errorCallBack(){
				toaster.pop({type: 'error', title: "Attention", body:"Une erreur s'est produite, contactez le gestionnaire de BDD"});
			})
	
		}else{
			toaster.pop({type: 'error', title: "Attention", body:"Le formulaire contient des erreurs"});
		}

	}


}// END CONTROLLER


// ####### FORMULAIRE DES CHAMPS ##############

template = configuration.URL_APPLICATION+'meta/meta/formulaire.html'
angularApp.component('formulaire', {

  controller :formController ,
  templateUrl : template,
  bindings:{
  	'form': '<',
  	'onFormValidation' : '&'
  }

});


function formController(toaster){
	formCtrl = this;
	formCtrl.type_widget = ['Booléen', 'Texte', 'Entier', 'Réel','Liste déroulante']
	formCtrl.newFields = [];

	formCtrl.regex = new RegExp('^([a-z]+(_*[0-9]*)*)+$')

	formCtrl.addNewField = function(validForm){
		lastIndex = this.form.length;
		if(lastIndex == 0){
			nextId = 1;
		}else{
			nextId = this.form[lastIndex-1].id_champ + 1;
		}
		this.form.push({'id_champ': nextId, 'lib_champ':'', 'no_spec':'spec_'+nextId, 'nom_champ':'', 'type_widget': '', 'db_type':'', 'valeur': "{\"values\":[]}", 'obligatoire': false, 'new':true});
	}

	formCtrl.addValue = function(){
  		this.currentValues.push({'value': ''});
  	}

  formCtrl.validateNewValues = function(id){
  	var formatedNewValues = this.currentValues.map(function(e){
  		return e.value;
  	})
  	i = 0;
  	while(i<this.form.length && id != this.form[i].id_champ){
  		i++;
  	}
  	var inter = {"values": formatedNewValues};
  	this.form[i].valeur = JSON.stringify(inter);
  	this.currentValues = null;
  }

  	formCtrl.showValues_and_fillDbType = function(champ){
  		if(champ.type_widget == 'Liste déroulante'){
	  		var inter = [];
			this.form.forEach(function(o){
					if(o.id_champ === champ.id_champ){
						formCtrl.currentField = o;
						inter = JSON.parse(o.valeur).values
					}
				})
			formCtrl.currentValues=inter.map(function(i){
					return {'value': i}
			})
  		}

  		console.log(this.form)
  		this.form[champ.id_champ -1].db_type = cor_widget_type[champ.type_widget]

	}

	formCtrl.formValidation = function(isValid){
		if(!isValid){
			toaster.pop({type: 'error', title: "Attention", body:"Le formulaire contient des erreurs"});
		}else{
			toaster.pop({type: 'succes', title: "Ok", body:"Le modèle de données a été enregistré. N'oubliez pas de créer/editer le projet..."});
			this.onFormValidation({'isValidForm':isValid})
		}
	}

	formCtrl.deleteLastInput = function(tab){
		tab.splice(tab.length -1, 1);
	}

	var cor_widget_type = {
		'Booléen': 'boolean',
		'Liste déroulante': 'character varying',
		'Texte': 'character varying',
		'Entier': 'integer',
		'Réel': 'float'
	}


}