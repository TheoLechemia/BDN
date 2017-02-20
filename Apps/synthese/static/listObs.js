module.exports = function(angularInstance){


function lastObsCtrl ($uibModal, $http){
	ctrl = this;
	ctrl.currentPoint = null;

	var overFlowedList = $('.last-obs');

	ctrl.$onChanges = function(changes){
		if (changes.geojson){
			if (changes.geojson.currentValue != undefined){
				ctrl.currentList = changes.geojson.currentValue.point;
			}
		}
		if(changes.currentListObs){
			if(changes.currentListObs.currentValue != undefined){
				    var vpHeight = overFlowedList.height();
				    var scrollTop = overFlowedList.scrollTop();
				    var link = $('#'+changes.currentListObs.currentValue);
				    if (link.length>0){
				   		var position = link.position();

				        $('.last-obs').animate({
					        scrollTop: (position.top + scrollTop -100)
					    }, 500);
					}
			}

		}
	}

	ctrl.zoom = function(id_synthese){
		ctrl.mainController.updateCurrentLeafletObs(id_synthese);
		ctrl.mainController.updateCurrentListObs(id_synthese);
	}

	ctrl.isCurrentObs = function(id, row_id_synthese){
			return id == row_id_synthese;	
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
  	'currentLeafletObs': '<',
  }

});

}