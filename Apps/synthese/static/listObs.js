module.exports = function(angularInstance){

function lastObsCtrl ($uibModal, $http){
	ctrl = this;
	ctrl.currentPoint = null;

	ctrl.$onChanges = function(changes){
		if (changes.geojson){
			if (changes.geojson.currentValue != undefined){
				ctrl.currentList = changes.geojson.currentValue.point;
			}
		}


	}

	ctrl.zoom = function(id_synthese){
		ctrl.mainController.updateCurrentLeafletObs(id_synthese);
		ctrl.mainController.updateCurrentListObs(id_synthese);
	}

	ctrl.isCurrentObs = function(listIdSynthese, row_id_synthese){
		i = 0;
		while(i<listIdSynthese.length){
			return listIdSynthese[i] == row_id_synthese;
			i++;
		}
	}

	ctrl.selected = 'point';

	ctrl.isSelected = function(list){
		return this.selected === list;
	}

	ctrl.changeList = function(list){
		this.currentList = this.geojson[list];
		this.selected = list;
	}


}


templateLastObs = 'synthese/templates/listObs.html';

angularInstance.component('listObs', {

  controller : lastObsCtrl,
  templateUrl : templateLastObs,
  require: {
  	mainController : '^app',
  },
  bindings : {
  	'geojson' : '<',
  	'currentListObs' : '<',
  	'currentLeafletObs': '<'
  }

});

}