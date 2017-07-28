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
		var idmateria= $("#idmateria").val();
		console.log(idmateria);
		var nombre = $("#nombre").val();
		console.log(nombre);
		if (nombre != '' && nombre != null){
			$("#errorUnidad").hide();
			var url= "agregarUnidad/" + nombre + "/"; //creo la URL que voy a direccionar
			console.log(url);
			$.post(url, nombre, function(data){ //peticion al servidor para agregar unidad
				//aca muestro mi unidad recien creada en la tabla de unidades de esta vista
				var tabla = document.getElementById("tablaUnidades"); //tabla de unidades
				if (tabla == null){ //genero automaticamente una tabla de unidades si la unidad agregada es la primer unidad de la materia.
					var tablaUnidades =document.createElement('table');
					tablaUnidades.id="tablaunidades";
					tablaUnidades.className = "mdl-data-table mdl-js-data-table" // agrego este <tr> a la tabla abajo del todo
					
					document.getElementById("cuerpoTarjetaUnidades").appendChild(tablaUnidades);
					
					var tr = document.createElement('tr'); //creo un <tr> </tr>
					tablaUnidades.appendChild(tr);
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
					tablaUnidades.appendChild(tr2); // agrego este <tr> a la tabla abajo del todo
					tr2.id= data.idunidad;
					var td = document.createElement('td'); // creo un <td> </td>
					td.className = "mdl-data-table-cel--non-numeric row"; // le doy mis clases de CSS
					td.innerHTML = data.nombre; //le pongo el nombre de la unidad recien creada
					td.id = "n" + data.idunidad;
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
						$("#nombre").val('');
						$("#mensaje").html(data.mensaje);
						$("#vacio").remove();
						//botonEditar.onclick = editarUnidad(event, data.idunidad, data.nombre);
						botonEditar.onclick = function(event){
				            editarUnidad(event, data.idunidad, data.nombre);
				            
				        };
						//botonEliminar.onclick = eliminarUnidad(event,data.idunidad);
						botonEliminar.onclick = function(event){
				            dialogo(event, data.idunidad);

				            componentHandler.upgradeAllRegistered();
				        };

						$("#nombre").val('');
						var mensaje = data.mensaje;
						mensaje.className = "success";
						$("#mensaje").html(data.mensaje);
						$(window).scrollTo("#tablaUnidades");
						componentHandler.upgradeAllRegistered(); /*"Reinicia" el cargado de Material Design para lograr obtener el comportamiento deseado del DOM con los elementos cargados dinamicamente, si esto no esta, por ejemplo aparece un textfield pero no se aplica nada del JavaScript de Material Design */
					} else { //si ya tengo una tabla de unidades solo agrego una fila que es mi unidad recientemente creada.
						var tr = document.createElement('tr'); //creo un <tr> </tr>
						tabla.appendChild(tr); // agrego este <tr> a la tabla abajo del todo
						tr.id= data.idunidad;
						var td = document.createElement('td'); // creo un <td> </td>
						td.className = "mdl-data-table-cel--non-numeric row"; // le doy mis clases de CSS
						td.innerHTML = data.nombre; //le pongo el nombre de la unidad recien creada
						td.id = "n" + data.idunidad;
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
						$("#mensaje").html(data.mensaje);
						//botonEditar.onclick = editarUnidad(event, data.idunidad, data.nombre);
						botonEditar.onclick = function(event){
				            editarUnidad(event, data.idunidad, data.nombre);
				            
				        };
						//botonEliminar.onclick = eliminarUnidad(event,data.idunidad);
						botonEliminar.onclick = function(event){
				            dialogo(event, data.idunidad);

				            componentHandler.upgradeAllRegistered();
				        };

						componentHandler.upgradeAllRegistered(); /*"Reinicia" el cargado de Material Design para lograr obtener el comportamiento deseado del DOM con los elementos cargados dinamicamente, si esto no esta, por ejemplo aparece un textfield pero no se aplica nada del JavaScript de Material Design
				*/		
						$('html, body').scrollTop(0); //deberia hacer autoscroll hacia arriba, pero no funciona aun
					}
					
				})
				.fail(function(xhr, status, error) {
				       alert("ERROR: " + error + "\n" + "STATUS: " + status + "\n" + "XHR: " + xhr);

				});
			}else{
				$("#errorUnidad").show();
			}
		})

		
		$('body').on('click','#aceptarEdicion' , function(){
			componentHandler.upgradeAllRegistered();
			var nombre =$("#nombreEditar").val();
			if (nombre != '' && nombre != null){
				var idUnidad = $("#idUnidadEditarId").val();
				var url= "editarUnidad/" + idUnidad + "/" +  nombre + "/";
				$.post(url, function(data){ 
				})
				 .done(function(data){ //para aplicar tambien en componentes dinamicamente generados:
					$("#divFormEdicion").slideUp();
					$("#divFormEdicion").remove(); //elimino el formulario generado
					$("#aceptarEdicion").remove(); //elimino el boton generado
					$("#success").html(data.mensaje);
					$("#n" + data.idUnidad).empty(); //vacio el nombre de la unidad en la tabla
					$("#n" + data.idUnidad).html(data.nombre);		 //le pongo el nombre nuevo
				});
			}

		});
			
	});
	
		

	$.fn.eliminar = function(event, idUnidad){ //funcion de Jquery en una especie de variable
			event.preventDefault();
			url = "eliminarUnidad/" + idUnidad + "/";
			$.post(url, function(data){
				
			})
			.done(function(data){
				$("#" + idUnidad).hide();
				$("#mensajeEliminar").show();
				$("#success").html(data);
				window.scrollTo(0, 0);
				$("#" + idUnidad).remove();
				
			})
			.fail(function(ts) {
				alert(ts.responseText);
			    //alert("ERROR: " + error + "\n" + "STATUS: " + status + "\n" + "XHR: " + xhr);

			});
	}

	function eliminarUnidad(event){
		var idUnidad = $("#idUnidadBaja").val();
		$.fn.eliminar(event,idUnidad); //aca lllamo a la funcion de arriba
	}

	function editarUnidad(event, idUnidad, nombre){
		//genero un "formulario" de edicion por medio de javascript
		event.preventDefault();
		console.log(idUnidad);
		if(document.getElementById("divFormEdicion") == null){ //evito que se genere mas de 1
			//formulario y se haga un lio
			var div = document.createElement("div"); //div que contiene formulario
			div.id = "divFormEdicion";
			div.className = "mdl-textfield mdl-js-textfield mdl-textfield--floating-label";
	 		// agrego clase CSS con classname
			var input = document.createElement("input");
			input.type="text";
			input.value = nombre;
			input.className = "mdl-textfield__input";
			input.id = "nombreEditar";
			div.appendChild(input);
			
			var label = document.createElement("label");
			label.innerHTML = "Editar unidad: " + nombre;
			label.htmlFor= input.id;
			label.className="mdl-textfield__label";
			div.appendChild(label);

			document.getElementById("cuerpoTarjetaUnidades").appendChild(div);
			
			var botonAceptar = document.createElement("input");
			botonAceptar.type="button";
			botonAceptar.value = "Aceptar";
			botonAceptar.id = "aceptarEdicion";
			botonAceptar.className = "mdl-button mdl-js-button";
			console.log(botonAceptar.id);
			//botonAceptar.onclick=$.fn.editar(event, idUnidad, nombre);
			document.getElementById("cuerpoTarjetaUnidades").appendChild(botonAceptar);

			document.getElementById("idUnidadEditarId").value = idUnidad;
			document.getElementById("idUnidadEditarNombre").value = nombre;
			componentHandler.upgradeAllRegistered();
		}
	}

	
