module.exports = function(angularInstance){


function listObsCtrl ($uibModal, $http){
	listCtrl = this;
	listCtrl.currentPoint = null;

	var overFlowedList = $('.last-obs');

	listCtrl.$onChanges = function(changes){
		if (changes.geojson){
			if (changes.geojson.currentValue != undefined){
				this.currentList = changes.geojson.currentValue.point;
			}
		}
		if(changes.currentListObs){
			//scroll dans la liste
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

	listCtrl.zoom = function(geojsonProperties){
		this.mainController.updateCurrentLeafletObs(geojsonProperties);
		this.mainController.updateCurrentListObs(geojsonProperties);
	}

	listCtrl.isCurrentObs = function(id, row_id_synthese){
			return id == row_id_synthese;	
	}

	listCtrl.selected = 'point';

	listCtrl.isSelected = function(list){
		return this.selected === list;
	}

	listCtrl.changeList = function(list){
		this.currentList = this.geojson[list];
		this.selected = list;
	}
}

templateLastObs = 'synthese/templates/listObs.html';

angularInstance.component('listObs', {

  controller : listObsCtrl,
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