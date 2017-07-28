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


	$("form[name='agregarExamen']").validate({
		
		rules:{
			nombre: "required",
			fechaCierre: {required: true, date: true, greaterThan: fechaHoy},
			'opcionVisible[]':{ required:true },
			'unidades[]': {required: true}
		},
		messages: {
			nombre: "Este campo es obligatorio",
			fechaCierre:{ required: "Este campo es obligatorio", greaterThan: "La fecha no es válida" },
			'opcionVisible[]': "Elegi al menos una de las 2 opciones",
			'unidades[]': "Tenés que elegir al menos una unidad"
		},
		errorPlacement: function (error, element) {
            if (element.attr("name") == "opcionVisible[]") {
                error.appendTo("#errorRadio");
            } else if (element.attr("name") == "unidades[]"){ //si no elijo ninguna unidad para agregar al examen
            	error.appendTo("#errorUnidades");
            }
            else{
                error.insertAfter(element);
            }
        },
		submitHandler: function(agregarExamen){
			console.log($("#fechaCierre").val());
			if (!esFechaMayor($("#fechaCierre").val()))
				$("#fechaNoValida").html("Introduci una fecha válida");
			else
				agregarExamen.submit();
		}
		
	
	});

});
