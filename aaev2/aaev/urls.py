# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from aaev import views


urlpatterns= patterns('',
    
    url(r'^$', views.index, name='index'),
    url(r'^recuperarClave/(?P<mail>[\w|\W]+)/$', views.recuperarClave, name='recuperarClave'),
    url(r'^admin/$', views.indexAdmin, name='admin'),
    url(r'^examenEjemplo/$', views.examenEjemplo, name='examenEjemplo'),
    url(r'^admin/ingresar/$', views.loginAdmin, name='ingresarAdmin'),
    url(r'^admin/inicio/$', views.inicioAdmin, name='inicioAdmin'),
    url(r'^admin/salir/$', views.logoutAdmin, name='logoutAdmin'),
    url(r'^admin/solicitudes/$', views.solicitudesAdmin, name='solicitudesAdmin'),
    #repito los metodos para traer las carreras y materias por AJAX que se usan en el registro
    url(r'^admin/universidades/$', views.adminUniversidades, name='adminUniversidades'),
    url(r'^admin/universidades/agregarUniversidad/$', views.agregarUniversidad, name='agregarUniversidad'),
    url(r'^admin/universidades/editarUniversidad/(?P<idUniversidad>\d+)/$', views.editarUniversidad, name='editarUniversidad'),
    url(r'^admin/universidades/eliminarUniversidad/(?P<idUniversidad>\d+)/$', views.eliminarUniversidad, name='eliminarUniversidad'),
    url(r'^admin/universidades/detalles/(?P<idUniversidad>\d+)/$', views.detallesUniversidad, name='detallesUniversidad'),
    url(r'^admin/carreras/$', views.adminCarreras, name='adminCarreras'),
    url(r'^admin/carreras/agregarCarrera/$', views.agregarCarrera, name='agregarCarrera'),
    url(r'^admin/carreras/eliminarCarrera/(?P<idCarrera>\d+)/$', views.eliminarCarrera, name='eliminarCarrera'),
    url(r'^admin/carreras/editarCarrera/(?P<idCarrera>\d+)/$', views.editarCarrera, name='editarCarrera'),
    url(r'^admin/carreras/detalles/(?P<idCarrera>\d+)/$', views.detallesCarrera, name='detallesCarrera'),
    url(r'^admin/materias/$', views.adminMaterias, name='adminMaterias'),
    url(r'^admin/materias/(?P<idUniversidad>\d+)/$', views.traerCarrerasAdmin, name='traerCarrerasAdmin'),
    url(r'^admin/materias/agregarMateria/$', views.agregarMateria, name='agregarMateria'),
    url(r'^admin/materias/eliminarMateria/(?P<idMateria>\d+)/$', views.eliminarMateria, name='eliminarMateria'),
    url(r'^admin/materias/detallesEditar/(?P<idMateria>\d+)/$', views.detallesEditarMateria, name='detallesEditarMateria'),
    url(r'^admin/materias/editarMateria/(?P<idMateria>\d+)/$', views.editarMateria, name='editarMateria'),
    url(r'^admin/solicitudes/detallesSolicitud/(?P<idSolicitud>\d+)/$', views.detallesSolicitudRegistro, name='detallesSolicitudRegistro'),
    url(r'^admin/solicitudes/detallesSolicitudMateria/(?P<idSolicitud>\d+)/$', views.detallesSolicitudMateria, name='detallesSolicitudMateria'),
    url(r'^admin/solicitudes/(?P<iduniversidad>\d+)/$', views.traerCarrerasRegistro ,name='traerCarrerasRegistro'),
    url(r'^admin/solicitudes/(?P<iduniversidad>\d+)/(?P<idcarrera>\d+)/$', views.traerMateriasRegistro, name='traerMateriasRegistro'),
    url(r'^admin/solicitudes/rechazarSolicitud/(?P<idSolicitud>\d+)/$', views.rechazarSolicitudRegistro, name='rechazarSolicitudRegistro'),
    url(r'^admin/solicitudes/rechazarSolicitudMateria/(?P<idSolicitud>\d+)/$', views.rechazarSolicitudMateria, name='rechazarSolicitudMateria'),
    url(r'^admin/solicitudes/rechazarTodasSolicitudes/$', views.rechazarTodasSolicitudes, name='rechazarTodasSolicitudes'),
    url(r'^admin/solicitudes/rechazarTodasSolicitudesMateria/$', views.rechazarTodasSolicitudesMateria, name='rechazarTodasSolicitudesMateria'),
    url(r'^admin/solicitudes/aceptarSolicitud/(?P<idSolicitud>\d+)/(?P<idMateria>\d+)/$', views.aceptarSolicitudRegistro, name='aceptarSolicitudRegistro'),
    url(r'^admin/solicitudes/aceptarSolicitudMateria/(?P<idSolicitud>\d+)/(?P<idMateria>\d+)/$', views.aceptarSolicitudMateria, name='aceptarSolicitudMateria'),
    url(r'^admin/docentes/$', views.gestionDocentes, name='gestionDocentes'),
    url(r'^admin/docentes/detallesDocente/(?P<idDocente>\d+)/$', views.detallesDocente, name='detallesDocente'),
    url(r'^admin/docentes/eliminarDocente/(?P<idDocente>\d+)/$', views.eliminarDocente, name='eliminarDocente'),
    url(r'^admin/docentes/eliminarTodosDocentes/$', views.eliminarTodosDocentes, name='eliminarTodosDocentes'),
    
    url(r'^registro/$', views.registro, name='registro'),
    url(r'^prueba/$', views.prueba, name='prueba'),
    url(r'^ingresar/$',views.login,name='ingresar'),
    url(r'^registro/(?P<iduniversidad>\d+)/$', views.traerCarrerasRegistro ,name='traerCarrerasRegistro'),
    url(r'^registro/(?P<iduniversidad>\d+)/(?P<idcarrera>\d+)/$', views.traerMateriasRegistro, name='traerMateriasRegistro'),
    url(r'^registro/registrarAlumno/$', views.registrarAlumno, name='registrarAlumno'),
    url(r'^alumno/$', views.inicioAlumno, name='inicioAlumno'),
    url(r'^alumno/detallesMateria/(?P<idMateria>\d+)/$', views.detallesMateria, name='detallesMateria'),
    url(r'^alumno/enviarSolicitud/(?P<idMateria>\d+)/$', views.inscripcionMateria, name='inscripcionMateria'),   
    url(r'^alumno/(?P<idMateria>\d+)/examenes/$', views.verExamenesAlumno, name='verExamenesAlumno'),   
    url(r'^alumno/buscarExamen/(?P<nombreExamen>[\w|\W]+)/$', views.buscarExamen, name='buscarExamen'),   
    url(r'^alumno/(?P<idMateria>\d+)/examenes/realizarExamen/$', views.realizarExamen, name='realizarExamen'),   
    url(r'^alumno/(?P<idMateria>\d+)/examenes/realizarExamen/corregirExamen/(?P<idExamen>\d+)/$', views.corregirExamen, name='corregirExamen'),   
    url(r'^registro/enviarDatos/$', views.envioSolicitudRegistroDocente, name='registrarDocente'),
    
#DOCENTE
    url(r'^docente/$', views.inicioDocente, name='inicioDocente'),
    url(r'^docente/(?P<iduniversidad>\d+)/$', views.traerCarrerasId ,name='traerCarrerasId'),
    url(r'^docente/(?P<iduniversidad>\d+)/(?P<idcarrera>\d+)/$', views.traerMateriasId, name='traerMateriasId'),
    url(r'^docente/enviarSolicitud/$', views.enviarSolicitudMateria, name='enviarSolicitudMateria'),
    url(r'^salir/$', views.logout, name='cerrarSesion'),
    url(r'^docente/(?P<idMateria>\d+)/unidades/$', views.verUnidadesMateria, name='verUnidadesMateria'),
    url(r'^docente/(?P<idMateria>\d+)/alumnos/$', views.gestionAlumnos, name='gestionAlumnos'),
    url(r'^docente/(?P<idMateria>\d+)/alumnos/detallesAlumno/(?P<idAlumno>\d+)/$', views.detallesAlumno, name='detallesAlumno'),
    url(r'^docente/(?P<idMateria>\d+)/alumnos/eliminarAlumno/(?P<idAlumno>\d+)/$', views.eliminarAlumno, name='eliminarAlumno'),
    url(r'^docente/(?P<idMateria>\d+)/alumnos/eliminarTodosAlumnos/$', views.eliminarTodosAlumnos, name='eliminarTodosAlumnos'), 
    url(r'^docente/(?P<idMateria>\d+)/solicitudes/$', views.solicitudesDeAlumnos, name='solicitudesAlumnos'), 
    url(r'^docente/(?P<idMateria>\d+)/solicitudes/detallesSolicitud/(?P<idSolicitud>\d+)/$', views.detallesSolicitud, name='detallesSolicitud'), 
    url(r'^docente/(?P<idMateria>\d+)/solicitudes/aceptarSolicitud/(?P<idSolicitud>\d+)/$', views.aceptarSolicitud, name='aceptarSolicitud'), 
    url(r'^docente/(?P<idMateria>\d+)/solicitudes/rechazarSolicitud/(?P<idSolicitud>\d+)/$', views.rechazarSolicitud, name='rechazarSolicitud'), 
    url(r'^docente/(?P<idMateria>\d+)/solicitudes/rechazarTodas/$', views.rechazarTodasSolicitudesAlu, name='rechazarTodasSolicitudesAlu'), 
    url(r'^docente/(?P<idMateria>\d+)/solicitudes/aceptarTodas/$', views.aceptarTodasSolicitudesAlu, name='aceptarTodasSolicitudesAlu'), 
    url(r'^docente/(?P<idMateria>\d+)/unidades/agregarUnidad/(?P<nombre>[\w|\W]+)/$', views.agregarUnidad, name='agregarUnidad'),
    url(r'^docente/(?P<idMateria>\d+)/unidades/eliminarUnidad/(?P<idUnidad>\d+)/$', views.eliminarUnidad, name='eliminarUnidad'),
    url(r'^docente/(?P<idMateria>\d+)/unidades/editarUnidad/(?P<idUnidad>\d+)/(?P<nombre>[\w|\W]+)/$', views.editarUnidad, name='editarUnidad'),
    url(r'^docente/(?P<idMateria>\d+)/preguntas/$', views.verPreguntasMateria, name='verPreguntasMateria'),
    url(r'^docente/(?P<idMateria>\d+)/preguntas/(?P<idTipo>\d+)/$', views.formularioTipo, name='formularioTipo'),
    url(r'^docente/(?P<idMateria>\d+)/preguntas/agregarPregunta/$', views.agregarPregunta, name='agregarPregunta'),
    url(r'^docente/(?P<idMateria>\d+)/preguntas/(?P<idPregunta>\d+)/eliminarPregunta/$', views.eliminarPregunta, name='eliminarPregunta'),
    url(r'^docente/(?P<idMateria>\d+)/preguntas/detalles/(?P<idPregunta>\d+)/$', views.detallesPregunta, name='detallesPregunta'),
    url(r'^docente/(?P<idMateria>\d+)/preguntas/editarPregunta/(?P<idPregunta>\d+)/$', views.editarPregunta, name='editarPregunta'),
    url(r'^docente/(?P<idMateria>\d+)/examenes/$', views.verExamenesMateria, name='verExamenesMateria'),
    url(r'^docente/(?P<idMateria>\d+)/examenes/(?P<idExamen>\d+)/visible/$', views.cambiarVisibilidad, name='cambiarVisibilidad'),
    url(r'^docente/(?P<idMateria>\d+)/examenes/exportarExamen/(?P<idExamen>\d+)/$', views.exportarExamen, name='exportarExamen'),
    
    url(r'^docente/(?P<idMateria>\d+)/examenes/(?P<idExamen>\d+)/eliminarExamen/$', views.eliminarExamen, name="eliminarExamen"),
    url(r'^docente/(?P<idMateria>\d+)/examenes/agregarExamen/$', views.agregarExamen, name="agregarExamen"),
    url(r'^docente/(?P<idMateria>\d+)/examenes/detalles/(?P<idExamen>\d+)/$', views.detallesExamen, name='detallesExamen'),
    url(r'^docente/(?P<idMateria>\d+)/examenes/editarExamen/(?P<idExamen>\d+)/$', views.editarExamen, name='editarExamen'),
    url(r'^docente/(?P<idMateria>\d+)/examenes/quitarUnidadTipo/(?P<idUnidadHasExamen>\d+)/$', views.quitarUnidadTipoExamen, name='quitarUnidadTipo')
    )