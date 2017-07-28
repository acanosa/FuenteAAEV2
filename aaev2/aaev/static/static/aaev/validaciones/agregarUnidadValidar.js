$(function(){
	
	$("form[name='agregarUnidad']").validate({
	
		rules:{
			nombre: "required",
		},
		messages: {
			nombre: "Ingresa un nombre para tu unidad",
		},
		submitHandler: function(iniciarSesion){
			agregarUnidad.submit();
		}
		
	
	});

});