var angularApp = angular.module("app", ['ui.router', 'ngSanitize', 'toaster']);
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



function metaController ($http, toaster){
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
		'table_independante': 'False',
		'saisie_possible': 'False'
	};
	metaCtrl.form = angular.copy(initialForm);

	metaCtrl.bind_table_indep = function(){
		console.log(this.form.saisie_possible)
			if(this.form.saisie_possible == 'True'){
				this.form.table_independante = 'True';
		}
	}

	metaCtrl.fieldForm = [];

	

	metaCtrl.sendData = function(e){
		console.log(e.target)
		btn = e.target;
		btn.classList.add('disabled');
		data = {'projectForm': this.form, 'fieldForm': this.fieldForm}

		toaster.pop({type: 'wait', title: "Création du projet", body:"Cela peut prendre un peu de temps"});
		$http.post(configuration.URL_APPLICATION+'meta/addProject', data).then(function(response){
			// reset le form
			metaCtrl.form = angular.copy(initialForm);
			toaster.clear();
			btn.classList.remove('disabled');
			toaster.success({title: "OK", body:"Projet ajouté avec succès"});
			}, function errorCallBack(response){
				toaster.clear();
				toaster.error({title: "Attention", body:"Un erreur s'est produite, contactez le gestionnaire de base de données"})

		});
		
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


function listProtController($http){
	listCtrl = this;
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
template = configuration.URL_APPLICATION+'meta/meta/project.html'
angularApp.component('project', {

  controller :projectController ,
  templateUrl : template,
  bindings:{
  	'data': '<'	
  }

});

function projectController($stateParams, $http, toaster){
	prjCtrl = this;
	prjCtrl.currentValues = null;
	
	prjCtrl.$onInit = function(){
		$http.get(configuration.URL_APPLICATION+"meta/getProject/"+$stateParams.id).then(function(response){
			prjCtrl.projet = response.data.projet;
			prjCtrl.formulaire = response.data.formulaire;
			// s'il ny a pas de formulaire on initialise le formulaire commme un tableau vide;
			if(prjCtrl.formulaire != null){
				prjCtrl.initialNbField = prjCtrl.formulaire.length;	
			}else{
				prjCtrl.formulaire = [];
				prjCtrl.initialNbField = 0;
			}
		})
	}

	prjCtrl.editProject = function(){
		var nbNewField = this.formulaire.length - this.initialNbField;
		console.log(nbNewField)
		data = {'projectForm': this.projet, 'fieldForm': this.formulaire, 'nbNewField': nbNewField }
		console.log(data);
		$http.post(configuration.URL_APPLICATION+'meta/editProject', data).then(function(response){
			// update le nb de field
			prjCtrl.initialNbField = prjCtrl.formulaire.length;	
			toaster.success({title: "OK", body:"Projet edité avec succès"});


		})

	}


}// END CONTROLLER


template = configuration.URL_APPLICATION+'meta/meta/formulaire.html'
angularApp.component('formulaire', {

  controller :formController ,
  templateUrl : template,
  bindings:{
  	'form': '<',
  }

});


function formController(){
	formCtrl = this;
	formCtrl.type_widget = ['Checkbox', 'Texte', 'Nombre', 'Liste déroulante']
	formCtrl.db_type = ['character varying', 'integer', 'float', 'boolean'];
	formCtrl.newFields = [];



	formCtrl.addNewField = function(){
		console.log('click')
			lastIndex = this.form.length;
			if(lastIndex == 0){
				nextId = 0;
			}else{
				nextId = this.form[lastIndex-1].id_champ + 1;
			}
			
		this.form.push({'id_champ': nextId, 'lib_champ':'', 'no_spec':'spec_'+nextId, 'nom_champ':'', 'type_widget': '', 'db_type':'', 'valeur': "{\"values\":[]}"});
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
  	formCtrl.showValues = function(id){
		var inter = [];
		this.form.forEach(function(o){
				if(o.id_champ === id){
					formCtrl.currentField = o;
					inter = JSON.parse(o.valeur).values
				}
			})
		formCtrl.currentValues=inter.map(function(i){
				return {'value': i}
		})
	}

	 formCtrl.validateNewForm = function(){
  		$http.post(configuration.URL_APPLICATION+'/updateFormulaire', this.form).then(function(response){
  	})
  }


}
