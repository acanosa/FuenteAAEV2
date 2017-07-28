$(function(){
	
	$("form[name='enviarSolicitudMateria']").validate({
		errorLabelContainer: "#errorPlacement",
		rules: {
			materia_idmateria:{
	        	require_from_group: [1, '.formEnvio']
		    },
		    mensaje:{
		        require_from_group: [1, '.formEnvio']
		    }
		},
		messages: {
		},
		groups: {
			formularioGrupo: "materia_idmateria mensaje"
		},
		submitHandler: function(iniciarSesion){
			iniciarSesion.submit();
		}
		
	
	});

});