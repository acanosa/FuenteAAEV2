$(function(){
	
	$("form[name='iniciarSesion']").validate({
	
		rules:{
			mail: "required",
			clave: "required"
		},
		messages: {
			mail: "Ingresa un usuario para iniciar sesion",
			clave: "Ingresa tu clave para iniciar sesion"
			
		},
		submitHandler: function(iniciarSesion){
			iniciarSesion.submit();
		}
		
	
	});

});