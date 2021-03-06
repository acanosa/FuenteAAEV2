var contador=1;


$.ajaxSetup({ 
        beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                         break;
                     }
                 }
             }
             return cookieValue;
         }
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
     } 
});

$(document).ready(function(){
	$("#agregar").click(function(event){ //esta es bastante larga, porque genera dinamicamente bastantes componentes MDL para que el usuario pueda ver el cambio inmediato en la pagina en vez de re-renderizar todo...
		event.preventDefault(); //evito el evento predeterminado del boton
		var nombre = $("#nombre").val();
		var dominio = $("#dominiomail").val();
		console.log(nombre);
		console.log(dominio);
		var lista = [nombre, dominio];
		var url= "agregarUniversidad/"; //creo la URL que voy a direccionar
		if((nombre != '' && nombre != null) && (dominio != '' && dominio != null)){
			$.post(url, {nombre: nombre, dominiomail: dominio}, function(data){ //peticion al servidor para agregar universidad
				//aca muestro mi universidad recien creada en la tabla de universidades de esta vista
				console.log(data);
				var tabla = document.getElementById("tablaUniversidades"); //tabla de universidades
				if (tabla == null){ //genero automaticamente una tabla de universidades si la universidad agregada es la primer universidad de la materia.
					var tablaUniversidades =document.createElement('table');
					tablaUniversidades.id="tablaUniversidades";
					tablaUniversidades.className = "mdl-data-table mdl-js-data-table" // agrego este <tr> a la tabla abajo del todo
					
					document.getElementById("cuerpoTarjetaUniversidades").appendChild(tablaUniversidades);
					
					var tr = document.createElement('tr'); //creo un <tr> </tr>
					tablaUniversidades.appendChild(tr);
					var th1 = document.createElement('th');
					th1.innerHTML="Nombre";
					th1.className = "row"; // agrego este <tr> a 
					tr.appendChild(th1);
					var th2 = document.createElement('th');
					th2.className = "row";
					tr.appendChild(th2);
					var th3 = document.createElement('th');
					th3.className = "row";
					tr.appendChild(th3);
					var tr2 = document.createElement('tr'); //creo un <tr> </tr>
					tablaUniversidades.appendChild(tr2); // agrego este <tr> a la tabla abajo del todo
					tr2.id= data.iduniversidad;
					var td = document.createElement('td'); // creo un <td> </td>
					td.className = "mdl-data-table-cel--non-numeric row"; // le doy mis clases de CSS
					td.innerHTML = data.nombre; //le pongo el nombre de la universidad recien creada
					td.id = "n" + data.iduniversidad;
					console.log(td.id);
					td.style="text-align: -webkit-center;";
					tr2.appendChild(td); // agrego el td al fondo del tr (que creamos unas lineas mas arriba)
					//genero un icono de edicion con sus clases y el nombre del icono
					var botonEditar = document.createElement("button");
						
						botonEditar.className = "mdl-button mdl-js-button";
						
						var iconoEditar = document.createElement('i');
						iconoEditar.className = "material-icons md-36 md-green";
						iconoEditar.innerHTML = "mode_edit";
						
						botonEditar.appendChild(iconoEditar);

						var tdEditar = document.createElement('td'); // otro td con el boton para editar
						tdEditar.className = "mdl-data-table-cel--non-numeric row "; //agrego clases
						tdEditar.appendChild(botonEditar); //le pongo texto adentro (el boton en si)
						//genero un icono de edicion con las clases y el icono correspondiente
						tdEditar.style="text-align: -webkit-center;";
						tr2.appendChild(tdEditar); //lo pongo al fondo del tr que creamos aca
						
						var botonEliminar = document.createElement("button");
						botonEliminar.type="button";
						
						botonEliminar.className = "mdl-button mdl-js-button";
						
						var iconoEliminar = document.createElement('i');
						iconoEliminar.className = "material-icons md-36 md-red";
						iconoEliminar.innerHTML = "highlight_off";

						botonEliminar.appendChild(iconoEliminar);
						
						var tdEliminar = document.createElement('td'); //mismo procedimiento pero con boton Eliminar
						tdEliminar.className = "mdl-data-table-cel--non-numeric row";
						tdEliminar.appendChild(botonEliminar); // lo meto al boton 
						tdEliminar.style="text-align: -webkit-center;";



						tr2.appendChild(tdEliminar);

						$("#mensaje").html(data.mensaje);
						$("#vacio").remove();
						botonEditar.onclick = function(event){
				            editarUniversidad(event, data.iduniversidad, data.nombre);
				            
				        };
						botonEliminar.onclick = function(event){
				            eliminarUniversidad(event, data.iduniversidad);

				            componentHandler.upgradeAllRegistered();
				        };

						$("#nombre").val('');
						$("#dominiomail").val('');
						var mensaje = data.mensaje;
						mensaje.className = "success";
						$("#mensaje").html(data.mensaje);
						$(window).scrollTo("#tablaUniversidades");
						componentHandler.upgradeAllRegistered(); /*"Reinicia" el cargado de Material Design para lograr obtener el comportamiento deseado del DOM con los elementos cargados dinamicamente, si esto no esta, por ejemplo aparece un textfield pero no se aplica nada del JavaScript de Material Design */
					} else { //si ya tengo una tabla de universidades solo agrego una fila que es mi universidad recientemente creada.
						var tr = document.createElement('tr'); //creo un <tr> </tr>
						tabla.appendChild(tr); // agrego este <tr> a la tabla abajo del todo
						tr.id= data.iduniversidad;
						var td = document.createElement('td'); // creo un <td> </td>
						td.className = "mdl-data-table-cel--non-numeric row"; // le doy mis clases de CSS
						td.innerHTML = data.nombre; //le pongo el nombre de la universidad recien creada
						td.id = "n" + data.iduniversidad;
						console.log(td.id);
						td.style="text-align: -webkit-center;";
						tr.appendChild(td); // agrego el td al fondo del tr (que creamos unas lineas mas arriba)
						//genero un icono de edicion con sus clases y el nombre del icono
						var botonEditar = document.createElement("button");
						
						botonEditar.className = "mdl-button mdl-js-button";
						
						var iconoEditar = document.createElement('i');
						iconoEditar.className = "material-icons md-36 md-green";
						iconoEditar.innerHTML = "mode_edit";
						
						botonEditar.appendChild(iconoEditar);

						var tdEditar = document.createElement('td'); // otro td con el boton para editar
						tdEditar.className = "mdl-data-table-cel--non-numeric row "; //agrego clases
						tdEditar.appendChild(botonEditar); //le pongo texto adentro (el boton en si)
						//genero un icono de edicion con las clases y el icono correspondiente
						tr.appendChild(tdEditar); //lo pongo al fondo del tr que creamos aca
						
						var botonEliminar = document.createElement("button");
						botonEliminar.type="button";
						
						botonEliminar.className = "mdl-button mdl-js-button";
						
						var iconoEliminar = document.createElement('i');
						iconoEliminar.className = "material-icons md-36 md-red";
						iconoEliminar.innerHTML = "highlight_off";

						botonEliminar.appendChild(iconoEliminar);
						
						var tdEliminar = document.createElement('td'); //mismo procedimiento pero con boton Eliminar
						tdEliminar.className = "mdl-data-table-cel--non-numeric row";
						tdEliminar.appendChild(botonEliminar); // lo meto al boton 



						tr.appendChild(tdEliminar);
						$("#nombre").val('');
						$("#dominiomail").val('');
						$("#mensaje").html(data.mensaje);

						botonEditar.onclick = function(event){
				            editarUniversidad(event, data.iduniversidad, data.nombre);
				            
				        };
						botonEliminar.onclick = function(event){
				            eliminarUniversidad(event, data.iduniversidad);

				            componentHandler.upgradeAllRegistered();
				        };

						componentHandler.upgradeAllRegistered(); /*"Reinicia" el cargado de Material Design para lograr obtener el comportamiento deseado del DOM con los elementos cargados dinamicamente, si esto no esta, por ejemplo aparece un textfield pero no se aplica nada del JavaScript de Material Design
				*/		
						$('html, body').scrollTop(0); //deberia hacer autoscroll hacia arriba, pero no funciona aun
					}
					$("#mensaje").html("Universidad agregada con éxito");
					$("#errorAgregar").empty();
				})
				.fail(function(xhr, status, error) {
				       alert("ERROR: " + error + "\n" + "STATUS: " + status + "\n" + "XHR: " + xhr);

				});
			}else{
				$("#errorAgregar").html("Faltan datos para agregar universidad");
			}
		})

		
		$('body').on('click','#aceptarEdicion' , function(){
			componentHandler.upgradeAllRegistered();
			var nombre = $("#nombreEditar").val();
			var dominiomail = $("#dominiomailEditar").val();
			var idUniversidad = $("#idUniversidadEditar").val();
			data = {nombre: nombre, dominiomail: dominiomail}
			var url= "editarUniversidad/" + idUniversidad + "/";
			$.post(url, data, function(data){ 
			})
			.done(function(data){ //para aplicar tambien en componentes dinamicamente generados:
				$("#espacioEdicion").slideUp();
				$("#espacioEdicion").remove(); //elimino el formulario generado
				$("#success").html(data.mensaje);
				$("#n" + data.iduniversidad).empty(); //vacio el nombre de la universidad en la tabla
				$("#n" + data.iduniversidad).html(data.nombre);		 //le pongo el nombre nuevo
				location.reload();
			});

		});
		$('body').on('click','#cancelarEdicion' , function(){
			$("#espacioEdicion").slideUp();
			$("#espacioEdicion").remove(); //elimino el formulario generado
		
		});
			
	});
	
		

	$.fn.eliminar = function(event, idUniversidad){ //funcion de Jquery en una especie de variable
			event.preventDefault();
			url = "eliminarUniversidad/" + idUniversidad + "/";
			$.post(url, function(data){
				
			})
			.done(function(data){
				$("#" + idUniversidad).hide();
				$("#mensajeEliminar").show();
				$("#mensajeEliminar").html(data);
				window.scrollTo(0, 0);
				$("#" + idUniversidad).remove();
				
			});
	}

	function eliminarUniversidad(event){
		var idUniversidad = document.getElementById('idUniversidadBaja').value;
		$.fn.eliminar(event,idUniversidad); //aca lllamo a la funcion de arriba
	}

	//dialogo de confirmacion para eliminar un examen...
	function dialogoEliminar(event, idUniversidad){
		event.preventDefault();
		//uso de dialogo para confirmar la baja de un examen
		var dialog = document.querySelector('dialog');
		var titulo = dialog.querySelector('.mdl-dialog__title');
		if (! dialog.showModal) {
		   dialogPolyfill.registerDialog(dialog);
		}
		var nombre = document.getElementById("n" + idUniversidad).innerText //agarro td
		titulo.innerHTML = titulo.innerHTML + nombre;
		document.getElementById("idUniversidadBaja").value = idUniversidad;
		dialog.showModal(); //mostrar
		dialog.querySelector('.close').addEventListener('click', function() {
		      dialog.close(); //habilitar cierre del dialogo
		      titulo.innerHTML = "Eliminar "; //vuelve a vaciarse el espacio reservado para el nombre
		});
		dialog.querySelector('.confirmar').addEventListener('click', function() {
		      dialog.close(); //habilitar cierre del dialogo
		      titulo.innerHTML = "Eliminar "; //vuelve a vaciarse el espacio reservado para el nombre
		});
	}

	function editarUniversidad(event, idUniversidad){
		//genero un "formulario" de edicion por medio de javascript
		event.preventDefault();
		//if(document.getElementById("espacioEdicion") == null){ //evito que se genere mas de 1
			//formulario y se haga un lio
			var url="detalles/" + idUniversidad + "/";
			$.post(url, function(data){
				$("#espacioEdicion").slideUp(function(){
					$("#espacioEdicion").empty();
					$("#espacioEdicion").html(data);
					componentHandler.upgradeAllRegistered();
					$("#espacioEdicion").slideDown();
				});
			});
			/*
			var br = document.createElement("br");
			var div = document.createElement("div"); //div que contiene formulario
			div.id = "divFormEdicion";
			div.className = "mdl-textfield mdl-js-textfield mdl-textfield--floating-label";
			div.style.width = "auto";
	 		// agrego clase CSS con classname

	 		divNombre = document.createElement("div");
	 		//-----------------------------------
			// nombre de la universidad
			var input = document.createElement("input");
			input.type="text";
			input.className = "mdl-textfield__input";
			input.id = "nombreEditar";
			divNombre.appendChild(input);
			
			var label = document.createElement("label");
			label.innerHTML = "Editar universidad: " + nombre;
			label.htmlFor= input.id;
			label.className="mdl-textfield__label is-dirty";
			divNombre.appendChild(label);
			//agrego un enter
			div.appendChild(divNombre);
			div.appendChild(br);
			//-----------------------------------
			// dominio de la universidad
			var divDominio = document.createElement("div");
			var inputDominio = document.createElement("input");
			inputDominio.type="text";
			inputDominio.className = "mdl-textfield__input";
			inputDominio.id = "dominioMailEditar";
			divDominio.appendChild(inputDominio);
			
			var labelDominio = document.createElement("label");
			labelDominio.innerHTML = "Editar universidad: " + dominio;
			labelDominio.htmlFor= inputDominio.id;
			labelDominio.className="mdl-textfield__label is-dirty";
			divDominio.appendChild(labelDominio);

			div.appendChild(divDominio);
			div.appendChild(br);

			document.getElementById("cuerpoTarjetaUniversidades").appendChild(div);
			//boton para confirmar edicion
			var botonAceptar = document.createElement("input");
			botonAceptar.type="button";
			botonAceptar.value = "Aceptar";
			botonAceptar.id = "aceptarEdicion";
			botonAceptar.className = "mdl-button mdl-js-button";
			console.log(botonAceptar.id);
			div.appendChild(br);
			document.getElementById("cuerpoTarjetaUniversidades").appendChild(botonAceptar);

			document.getElementById("idUniversidadEditarId").value = idUniversidad;
			document.getElementById("idUniversidadEditarNombre").value = nombre;
			componentHandler.upgradeAllRegistered();
			*/
		//}
	}
