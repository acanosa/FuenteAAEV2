$(function(){
	var fechaHoy = new Date();
	
jQuery.validator.addMethod("greaterThan", 
function(value, element, params) {
	//console.log(params);

	array = value.split('-'); //el elemento tiene un valor de tipo String, asi que convierto a fecha
	fecha = new Date(parseInt(array[0]), parseInt(array[1]) - 1, parseInt(array[2]));
	if (fecha > params)
		return this.optional(element) || true;
	else
		return this.optional(element) || false;
});


	$("form[name='formEditar']").validate({
		
		rules:{
			fechaCierreEditar: {date: true, greaterThan: fechaHoy},
			
		},
		messages: {
			fechaCierreEditar:{greaterThan: "La fecha no es válida" },
		},
		submitHandler: function(editarExamen){
			editarExamen.submit();
		}
		
	
	});

});
