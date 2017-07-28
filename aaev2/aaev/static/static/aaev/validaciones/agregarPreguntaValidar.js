$(function(){
	jQuery.validator.addMethod("distinto", function(value, element, param) {
		return this.optional(element) || value != param;
	}, "Elegi un valor que no sea el por defecto");
	
	$("#agregarPregunta").validate({
		rules:{
			texto: "required",
			selectTipo: { distinto: "0" },
			selectUnidad: { distinto: "0"},
		},
		messages: {
			texto: "Este campo es obligatorio",
			selectTipo: {distinto: "Elegi una opción"},
			selectUnidad:{distinto: "Elegi una opción"}
		},
		submitHandler: function(agregarPregunta){
			//console.log("Termine de validar");
			agregarPregunta.submit();
		}		
	
	});

});