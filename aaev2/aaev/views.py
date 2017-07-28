# -*- coding: utf-8 -*-
#--------------------IMPORTS DJANGO --------------------
import json #para formatear a un diccionario json para enviarlo al done del AJAX
import base64 #para decodear y encodear imagenes a string
import datetime #fechas
import random #para la seleccion aleatoria de preguntas
import time
import StringIO
from PIL import Image #para usar MC de imagenes en PDF
import PIL #para usar MC de imagenes en PDF
from django.core.mail import send_mail, EmailMessage #envio de mail para recuperar clave
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.graphics.shapes import Drawing
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import *
from reportlab.lib.styles import *
from reportlab.lib.units import inch
from datetime import date #para el cierre del , ver metodo verExamenesMateria
from random import shuffle #ver agregarPregunta
from django.shortcuts import render #cargar html con contexto
from django.shortcuts import redirect #redireccionar a una url 
from django.views.decorators.csrf import ensure_csrf_cookie #asegurar cookie
from django.http import *
from django.core.context_processors import csrf #uso de tokens
from django.views.decorators.csrf import csrf_protect #proteger el csrf
from django.template.defaulttags import register #para uso de metodos en templates
from django.template.loader import render_to_string #plantillas a string
from django.template import Template, Context #generacion de plantillas
from django.contrib import messages #mensajes al redirigir la pagina, usado como session, solo que se eliminan al recargar
#--------------------MODELOS ------------------------------
from aaev.models import *
#--------------------FUNCIONES PROPIAS--------------------
from funciones import *
#--------------------FORMULARIOS BASADOS EN MODELOS-------------
from aaev.forms import *

# -----------------------------------CONTROLADORES DE VISTAS -------------------------

@csrf_protect
def index(request):
    return render(request, 'index.html', None) #pagina de inicio, sin variables

def examenEjemplo(request):
    return render(request, "examenEjemplo.html",None)

def prueba(request):
    return render(request, 'prueba.html', None)

#carga la solicitud de registro del docente en la base de datos,
#devuelve la vista de registro y un mensaje de exito
def envioSolicitudRegistroDocente(request): #el docente completa el formulario de la pagina de registro
    if request.method == 'POST':
        form = solicitudRegistroForm(request.POST)
        if form.is_valid(): #si el campo es valido agarro los datos
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            dni = str(form.cleaned_data['dni']) #aca lo hago texto para la base de datos, que usa VARCHAR
            email = form.cleaned_data['mail']
            idmateria = form.cleaned_data['idmateria']
            solicitudMensaje = form.cleaned_data['solicitud']
            idsolicitud = 0
            try:
                solicitud = SolicitudRegistro.objects.latest('idsolicitud_registro')
                idsolicitud = solicitud.idsolicitud_registro + 1
            except(SolicitudRegistro.DoesNotExist):
                idsolicitud = 1

            try:
                solicitudDniExistente = SolicitudRegistro.objects.get(dni = dni)
                if solicitudDniExistente:
                    messages.add_message(request, messages.INFO, "Ya hay una solicitud o docente registrado con ese DNI")
                    return redirect('aaev:registro')
            except (SolicitudRegistro.DoesNotExist):
                try:
                    solicitudMailExistente = SolicitudRegistro.objects.get(mail = email)
                    if solicitudMailExistente:
                        messages.add_message(request,messages.INFO, "Ya hay una solicitud o docente registrado con ese mail")
                        return redirect('aaev:registro')
                except (SolicitudRegistro.DoesNotExist):
                    try: 
                        docenteMail = Login.objects.get(mail = email)
                        if docenteMail:
                            messages.add_message(request,messages.INFO, "Ya hay una solicitud o docente registrado con ese mail")
                            return redirect('aaev:registro')
                    except (Login.DoesNotExist):                    
                        if solicitudMensaje and idmateria: #si se envio mensaje
                            solicitudGuardar = SolicitudRegistro(idsolicitud, nombre, apellido, email, dni, idmateria, solicitudMensaje)
                        elif idmateria and not solicitudMensaje: #si no se envio
                            solicitudGuardar = SolicitudRegistro(idsolicitud, nombre, apellido, email, dni, idmateria, 'El docente no ha enviado mensaje')
                        elif solicitudMensaje and not idmateria:
                            solicitudGuardar = SolicitudRegistro(idsolicitud, nombre, apellido, email, dni, None ,solicitudMensaje)
                        else:
                            solicitudGuardar = SolicitudRegistro(idsolicitud, nombre, apellido, email, dni, None, 'El docente no ha enviado mensaje')
                        solicitudGuardar.save()
                        messages.add_message(request, messages.SUCCESS, u"¡Solicitud de registro enviada! Tu solicitud se ha enviado al administrador para ser evaluada")
                        return redirect('aaev:registro')
        else:
            messages.add_message(request, messages.INFO, "Asegurate de completar todos los campos")
            return redirect('aaev:registro')

    else:
        return redirect('aaev:registro')

#registra un alumno en el sistema y habilita el login
def registrarAlumno(request):
    form = registroAlumnoForm(request.POST)
    if form.is_valid():
        nombre = form.cleaned_data['nombre']
        apellido = form.cleaned_data['apellido']
        dni = str(form.cleaned_data['dni']) #aca lo hago texto para la base de datos, que usa VARCHAR
        email = form.cleaned_data['email']
        clave = form.cleaned_data['clave']
        idLogin = 0
        idAlumno = 0
        try:
            login = Login.objects.latest('idlogin')
            idLogin = login.idlogin + 1
        except(SolicitudRegistro.DoesNotExist):
            idLogin = 1
        try:
            ultimoAlumno = Alumno.objects.latest('idalumno')
            idAlumno = ultimoAlumno.idalumno + 1
        except(Alumno.DoesNotExist):
            idAlumno = 1
        login = Login(idLogin,email,clave,3,True)
        login.save()
        alumno = Alumno(idAlumno,nombre,apellido,email,dni,idLogin)
        alumno.save()
        messages.add_message(request, messages.SUCCESS, u"¡Registro éxitoso!")
        return redirect('aaev:registro')
    else:
        messages.add_message(request,messages.ERROR, u"Registro fallido, asegurate de completar todos los campos")
        return redirect('aaev:registro')

#inicio de sesion de los usuarios, depende el usuario la vista que devuelva
#Nota: para Admin ver "loginAdmin"
def login(request): 
        if request:
            if request.method == 'POST':
                form = LoginForm(request.POST) #agarro el formulario de ingreso
                if form.is_valid():
                    nombre = form.cleaned_data['mail']
                    clave = form.cleaned_data['clave']
                    if validarLogin(nombre,clave):
                        usuario = Login.objects.get(mail=nombre)
                        request.session['usuario'] = str(usuario.mail)
                        if usuario.privilegio == 2:
                            docente = Docente.objects.get(idlogin = usuario.idlogin)
                            request.session['docente'] = str(docente.iddocente)
                            context = {'docente': docente}
                            return redirect('aaev:inicioDocente')
                        elif usuario.privilegio == 3:
                            alumno = Alumno.objects.get(idlogin = usuario.idlogin)
                            request.session['alumno'] = str(alumno.idalumno)
                            #materias solicitadas y aceptadas 
                            materias = AlumnoHasMateria.objects.filter(idalumno = alumno.idalumno).exclude(habilitado = False)
                            materias = Materia.objects.filter(alumnohasmateria = materias)
                            #materias solicitadas pero no aceptadas
                            materiasSolicitadas = AlumnoHasMateria.objects.filter(idalumno = alumno.idalumno).exclude(habilitado = True)
                            materiasSolicitadas = Materia.objects.filter(alumnohasmateria = materiasSolicitadas)
                            context = {'alumno': alumno, 'materias': materias,'materiasSolicitadas': materiasSolicitadas}
                            return redirect('aaev:inicioAlumno')
                    else:
                        messages.add_message(request,messages.ERROR, "Usuario y/o clave incorrectos")
                        return redirect('aaev:index')
                else:
                    messages.add_message(request,messages.ERROR, "Usuario y/o clave incorrectos")
                    return redirect('aaev:index')
                    """mensaje="Completa todos los campos"
                                                                                context = {'mensaje': mensaje}"""
                    #return redirect('aaev:index')
            else:
                return redirect('aaev:index')
        else:
            redirect('aaev:index')

#ingreso del administrador del sistema, solo para usuarios de este tipo
def loginAdmin(request):
    if request.method == 'POST':
        form = adminLoginForm(request.POST) #agarro el formulario de ingreso
        if form.is_valid():
            nombre = form.cleaned_data['usuario']
            clave = form.cleaned_data['clave']
            if validarLoginAdmin(nombre,clave):
                usuario = Admin.objects.get(usuario = nombre)
                request.session['usuario'] = str(usuario.usuario)
                registrosPendientes = len(SolicitudRegistro.objects.all())
                solicitudesMateria = len(SolicitudMateria.objects.all())
                docentesSolicitudes = registrosPendientes + solicitudesMateria
                context = {'admin': usuario, 'docentesSolicitantes': docentesSolicitudes}
                return redirect('aaev:inicioAdmin')
            else:
                messages.add_message(request,messages.ERROR, "Usuario y/o clave incorrectos")
                return redirect('aaev:admin')
                    
        else:
            messages.add_message(request,messages.ERROR, "Usuario y/o clave incorrectos")
           
            return redirect('aaev:admin')
            #return render(request, 'indexAdmin.html', context)
    else:
        return redirect('aaev:admin')
        #return redirect('aaev:indexAdmin')

def recuperarClave(request,mail):
    if request.method == 'POST':
        try:
            login = Login.objects.get(mail = mail)
            datosUsuario = None
            if login.privilegio == 2:
                datosUsuario = Docente.objects.get(idlogin=login.idlogin)  
            elif login.privilegio == 3:
                datosUsuario = Alumno.objects.get(idlogin=login.idlogin)
            mensaje = 'Hola ' + datosUsuario.nombre + ' ' + datosUsuario.apellido \
            + u', recientemente solicitaste la clave de tu usuario debio a que te la olvidaste,' \
            + u' la clave es la siguiente: ' + login.clave + '.'
            msg = EmailMessage(u'Recuperación de clave',
                       mensaje, to=[datosUsuario.mail])
            """
            send_mail(
                u'Recuperación de clave',
                mensaje,
                to=[datosUsuario.mail],
                fail_silently=False,
            )
            """
            msg.send()
            messages.add_message(request,messages.SUCCESS,u"Se ha enviado un mail conteniendo la clave solicitada")
            return redirect('aaev:index')
        except(Login.DoesNotExist):
            messages.add_message(request,messages.ERROR,u"No existe el usuario solicitado")
            return redirect('aaev:index')
    else:
        return redirect('aaev:index')

#carga el inicio del administrador una vez esta logeado, devuelve
#una vista con las solicitudes docentes tanto de registro como de materia 
def inicioAdmin(request):
    registrosPendientes = len(SolicitudRegistro.objects.all())
    solicitudesMateria = len(SolicitudMateria.objects.all())
    docentesSolicitudes = registrosPendientes + solicitudesMateria
    usuario = request.session['usuario']
    admin = Admin.objects.get(usuario = usuario)
    context = {'admin': admin, 'docentesSolicitantes': docentesSolicitudes}
    return render(request, 'inicioAdministrador.html', context)

#Carga el ABM de universidades
def adminUniversidades(request):
    try:
        universidades = Universidad.objects.all()
        usuario = request.session['usuario']
        admin = Admin.objects.get(usuario = usuario)
        context = {'admin': admin, 
        'universidades': universidades}
        return render(request, "universidadesAdmin.html", context)
    except ('usuario' not in request.session):
        return redirect('aaev:admin')
#se realiza el alta de universidades en la base de datos
def agregarUniversidad(request):    
    form = agregarUniversidadForm(request.POST)
    if form.is_valid():
        nombre = form.cleaned_data['nombre']
        dominiomail = form.cleaned_data['dominiomail']
        ultimo_id = 0
        try: 
            uni = Universidad.objects.latest('iduniversidad')
            ultimo_id = uni.iduniversidad + 1
        except(Universidad.DoesNotExist):
            ultimo_id = 1
        universidad = Universidad(ultimo_id,nombre,dominiomail)
        universidad.save()
        mensaje = "Unidad agregada con exito, tabla actualizada"
        data = {'nombre': universidad.nombre, 'iduniversidad': universidad.iduniversidad,
         'dominiomail': universidad.dominiomail}
        return HttpResponse(json.dumps(data), content_type="application/json")
        #return redirect('aaev:adminUniversidades')
    else:
        return HttpResponse("No valido")

def eliminarUniversidad(request, idUniversidad):
    universidad = Universidad.objects.get(pk = idUniversidad)
    """
    lista = UniversidadHasCarrera.objects.filter(universidad_iduniversidad_id = idUniversidad)
    for u in lista:
        u.delete()
    """
    universidad.delete()
    return HttpResponse(u"Universidad eliminada con éxito")

#detalles de universidad para editar, devuelve el formulario de edicion
def detallesUniversidad(request,idUniversidad):
    universidad = Universidad.objects.get(pk=idUniversidad)
    context = {'universidad': universidad}
    return render(request, "editarUniversidad.html", context)


def editarUniversidad(request,idUniversidad):
    universidad = Universidad.objects.get(pk = idUniversidad)
    form = request.POST
    nombre = form.get('nombre')
    dominiomail = form.get('dominiomail')

    if nombre != '' and nombre != universidad.nombre:
        universidad.nombre = nombre
    if dominiomail != '' and dominiomail != universidad.dominiomail:
        universidad.dominiomail = dominiomail

    universidad.save()
    mensaje = u"Universidad actualizada con éxito"
    data = {'iduniversidad': universidad.iduniversidad,'mensaje': mensaje, 
    'nombre': universidad.nombre} #agrego datos para el response
    return HttpResponse(json.dumps(data), content_type="application/json")# devuelvo diccionario

def adminCarreras(request):
    universidades = Universidad.objects.all()
    carreras = Carrera.objects.all()
    try:
        admin = getAdmin(request.session['usuario'])
        context= {'universidades': universidades, 'carreras': carreras,'admin':admin}
        return render(request, "carrerasAdmin.html", context)
    except('usuario' not in request.session):
        return redirect('aaev:admin')

def agregarCarrera(request):
    form = agregarCarreraForm(request.POST)
    if form.is_valid():
        nombre = form.cleaned_data['nombre']
        cantidadAnios = form.cleaned_data['cantidadanios']
        universidad = form.cleaned_data['iduniversidad']
        ultimo_id = 0
        try: 
            ultima_carrera = Carrera.objects.latest('idcarrera')
            ultimo_id = ultima_carrera.idcarrera + 1
        except(Carrera.DoesNotExist):
            ultimo_id = 1
        carrera = Carrera(ultimo_id,nombre,cantidadAnios,universidad.iduniversidad)
        carrera.save()
        mensaje = u"Carrera agregada con éxito, tabla actualizada"
        data = {'nombre': carrera.nombre, 'idcarrera': carrera.idcarrera,
         'cantidadanios': carrera.cantidadanios}
        return HttpResponse(json.dumps(data), content_type="application/json")
        #return redirect('aaev:adminUniversidades')
    else:
        return HttpResponse("No valido")

def eliminarCarrera(request, idCarrera):
    carrera = Carrera.objects.get(pk = idCarrera)
    """
    lista = UniversidadHasCarrera.objects.filter(carrera_idcarrera_id = idCarrera)
    for u in lista:
        u.delete()
    """
    carrera.delete()
    return HttpResponse(u"Carrera eliminada con éxito")

def detallesCarrera(request,idCarrera):
    carrera = Carrera.objects.get(pk=idCarrera)
    universidades = Universidad.objects.all()
    context = {'carrera': carrera, 'universidades': universidades}
    return render(request, "editarCarrera.html", context)

def editarCarrera(request,idCarrera):
    carrera = Carrera.objects.get(pk = idCarrera)
    form = request.POST
    nombre = form.get('nombre')
    cantidadanios = form.get('cantidadanios')
    iduniversidad = int(form.get('iduniversidad'))
    
    if nombre != '' and nombre != carrera.nombre:
        carrera.nombre = nombre
    if cantidadanios != '' and cantidadanios != carrera.cantidadanios:
        carrera.cantidadanios = cantidadanios
    universidadCarrera = carrera.iduniversidad
    if iduniversidad != universidadCarrera.iduniversidad:
        universidad = Universidad.objects.get(pk=iduniversidad)
        carrera.iduniversidad = universidad 

    carrera.save()
    mensaje = u"Carrera actualizada con éxito"
    data = {'idcarrera': carrera.idcarrera,'mensaje': mensaje, 
    'nombre': carrera.nombre} #agrego datos para el response
    return HttpResponse(json.dumps(data), content_type="application/json")# devuelvo diccionario


def adminMaterias(request):
    materias = Materia.objects.all()
    universidades = Universidad.objects.all()
    carreras = Carrera.objects.all()
    admin = getAdmin(request.session['usuario'])
    context ={'admin': admin,'universidades': universidades, 
    'carreras':carreras,'materias':materias}
    return render(request,"materiasAdmin.html",context)

def agregarMateria(request):
    form = agregarMateriaForm(request.POST)
    if form.is_valid():
        nombre = form.cleaned_data['nombre']
        anioCarrera = form.cleaned_data['aniocarrera']
        carrera = form.cleaned_data['idcarrera']
        ultimo_id = 0
        try: 
            ultima_materia = Materia.objects.latest('idmateria')
            ultimo_id = ultima_materia.idmateria + 1
        except(Materia.DoesNotExist):
            ultimo_id = 1
        materia = Materia(ultimo_id,nombre,anioCarrera,carrera.idcarrera)
        materia.save()
        messages.add_message(request,messages.SUCCESS,u"Materia agregada con éxito, tabla actualizada")
        data = {'nombre': materia.nombre, 'idmateria': materia.idmateria,
         'aniocarrera': materia.aniocarrera}
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        return redirect("aaev:admin")

def eliminarMateria(request, idMateria):
    materia = Materia.objects.get(pk = idMateria)
    materia.delete()
    #messages.add_message(request,messages.SUCCESS, u"Materia eliminada con éxito")
    return HttpResponse(True)

def detallesEditarMateria(request,idMateria):
    materia = Materia.objects.get(pk=idMateria)
    universidades = Universidad.objects.all()
    universidad = materia.idcarrera.iduniversidad
    carreras = universidad.carrera_set.all() #solo de la universidad en que esta la materia
    carrera = materia.idcarrera
    context = {'materia': materia,'carreras':carreras, 'carrera':carrera, 'universidades': universidades}
    return render(request, "editarMateria.html", context)

def editarMateria(request,idMateria):
    materia = Materia.objects.get(pk = idMateria)
    form = request.POST
    nombre = form.get('nombre')
    aniocarrera = form.get('aniocarrera')
    idcarrera = form.get('idcarrera')

    if idcarrera:
        idcarrera = int(idcarrera)
    
    if nombre != '' and nombre != materia.nombre:
        materia.nombre = nombre
    if aniocarrera != '' and aniocarrera != materia.aniocarrera:
        materia.aniocarrera = aniocarrera
    carreraMateria = materia.idcarrera
    if idcarrera != carreraMateria.idcarrera and idcarrera != '':
        try:
            carrera = Carrera.objects.get(pk=idcarrera)
        except:
            return HttpResponse(idcarrera)
        materia.idcarrera = carrera 

    materia.save()
    mensaje = u"Materia actualizada con éxito"
    data = {'idmateria': materia.idmateria,'mensaje': mensaje, 
    'materia': materia.nombre} #agrego datos para el response
    return HttpResponse(json.dumps(data), content_type="application/json")# devuelvo diccionario

def traerCarrerasAdmin(request,idUniversidad):
    universidad = Universidad.objects.get(pk=idUniversidad)
    carreras = universidad.carrera_set.all()
    if carreras:
        data = {'carreras': carreras, 'iduniversidad': idUniversidad}     
        return render(request, "AjaxCarreras.html", data)
    else:
        mensaje= "No hay carreras disponibles en esta universidad"
        data = {'mensaje': mensaje}
        return render(request, "AjaxCarreras.html", data) 


def solicitudesAdmin(request):
    solicitudesMateria = SolicitudMateria.objects.all()
    solicitudesRegistro = SolicitudRegistro.objects.all()
    admin = getAdmin(request.session['usuario'])
    universidades = Universidad.objects.all()
    context = {'admin': admin, 
    'solicitudesMateria': solicitudesMateria, 
    'solicitudesRegistro': solicitudesRegistro,
    'universidades': universidades}
    return render(request, 'solicitudesAdmin.html', context)

def detallesSolicitudRegistro(request, idSolicitud):
    solicitud = SolicitudRegistro.objects.get(idsolicitud_registro= idSolicitud)
    universidades = Universidad.objects.all()
    context = {'solicitud': solicitud, 'universidades': universidades}
    return render(request,'detallesSolicitud.html',context)

def detallesSolicitudMateria(request,idSolicitud):
    solicitud = SolicitudMateria.objects.get(idsolicitud_materia= idSolicitud)
    universidades = Universidad.objects.all()
    docente = solicitud.docente_iddocente
    context = {'solicitud': solicitud,'docente':docente, 'universidades': universidades}
    return render(request,'detallesSolicitudMateria.html',context)    



def rechazarSolicitudRegistro(request,idSolicitud):
    solicitud = SolicitudRegistro.objects.get(idsolicitud_registro = idSolicitud)
    solicitud.delete() #elimino la solicitud en la base de datos
    return HttpResponse(u"Solicitud rechazada con éxito")

def rechazarSolicitudMateria(request,idSolicitud):
    solicitud = SolicitudMateria.objects.get(idsolicitud_materia = idSolicitud)
    solicitud.delete() #elimino la solicitud en la base de datos
    return HttpResponse(u"Solicitud rechazada con éxito")

def aceptarSolicitudRegistro(request, idSolicitud,idMateria):
    solicitud = SolicitudRegistro.objects.get(idsolicitud_registro = idSolicitud)
    ultimoId = 0
    ultimoIdLogin = 0
    try:
        ultimo_docente = Docente.objects.latest('iddocente')
        ultimoId = ultimo_docente.iddocente + 1 
    except:
        ultimoId = 1
    try:
        ultimo_login = Login.objects.latest('idlogin')
        ultimoIdLogin = ultimo_login.idlogin + 1 
    except:
        ultimoIdLogin = 1
    #armado de la clave para el docente, compuesta de inicial del primer nombre + apellido
    inicialNombre = solicitud.nombre[0] #la inicial del primer nombre ingresado
    apellido = "" #el apellido solo se conforma de UN SOLO apellido, en caso de 2 apellidos o mas
    for letra in solicitud.apellido: #aca agarro solamente el primer apellido 
        if letra != ' ':
            apellido += letra
        else:
            break
    #armado final de la clave
    clave = inicialNombre + apellido 
    clave = clave.lower() #lo pongo en minusculas
    #creacion de objeto login (id,mail,clave,privilegio,activado)
    login = Login(ultimoIdLogin, solicitud.mail, clave, 2, True)
    login.save() #registro de objeto login
    #creacion de objeto docente(id,nombre,apellido,mail,dni, el ID de su usuario)
    docente = Docente(ultimoId, solicitud.nombre, solicitud.apellido, solicitud.mail, solicitud.dni, login.idlogin)
    docente.save()
    dhm = DocenteHasMateria(autoIncrementarIdDHM(),docente.iddocente,idMateria)
    dhm.save()
    solicitud.delete() #borro la solicitud dado que fue aceptada
    return HttpResponse(u"Solicitud aceptada con éxito")

def aceptarSolicitudMateria(request,idSolicitud,idMateria):
    solicitud = SolicitudMateria.objects.get(pk=idSolicitud)
    docente = solicitud.docente_iddocente
    try:
        materia = solicitud.materia_idmateria
    except: #si el docente no ingreso la materia e indico mensaje
        materia = Materia.objects.get(pk=idMateria)
    idObjeto = autoIncrementarIdDHM()  
    objeto = DocenteHasMateria(idObjeto,docente.iddocente,materia.idmateria)
    objeto.save()
    solicitud.delete()
    return HttpResponse(u"Solicitud aceptada con éxito")

def rechazarTodasSolicitudes(request):
    if request.method == 'POST':
        solicitudes = SolicitudRegistro.objects.all()
        for solicitud in solicitudes:
            solicitud.delete()
        return HttpResponse(u"Todas las solicitudes fueron rechazadas con éxito")
    else:
        return redirect('aaev:inicioAdmin')

def rechazarTodasSolicitudesMateria(request):
    if request.method == 'POST':
        solicitudes = SolicitudMateria.objects.all()
        for solicitud in solicitudes:
            solicitud.delete()
        return HttpResponse(u"Todas las solicitudes fueron rechazadas con éxito")
    else:
        return redirect('aaev:inicioAdmin')

def gestionDocentes(request):
    try:
        docentes = Docente.objects.all()
        try:
            admin = getAdmin(request.session['usuario'])
            context = {'admin': admin, 'docentes': docentes}
            return render(request,'gestionDocentes.html',context)
        except('usuario' not in request.session):
            return redirect('aaev:inicio') 
    except('usuario' not in request.session):
        return redireccionarAdmin(request)
        
def detallesDocente(request,idDocente):
    if request.method == 'POST':
        docente = Docente.objects.get(pk=idDocente)
        context = {'docente': docente}
        return render(request,'detallesDocente.html',context)
    else:
        return redireccionarAdmin(request)

#elimina el docente indicado del sistema
def eliminarDocente(request,idDocente):
    if request.method == 'POST':
        docente = Docente.objects.get(pk=idDocente)
        login = docente.idlogin #usuario y contraseña para entrar
        #materias donde tengo docente inscripto
        listaMaterias = DocenteHasMateria.objects.filter(iddocente = docente.iddocente)
        for registro in listaMaterias:
            registro.delete()
        docente.delete()
        login.delete()
        return HttpResponse(u'Docente eliminado con éxito')
    else:
        return redireccionarAdmin(request)

#elimina todos los docentes registrados del sistema
def eliminarTodosDocentes(request):
    if request.method == 'POST':
        docentes = Docente.objects.all() #todos mis docentes
        #materias donde tengo docentes inscriptos
        listaMaterias = DocenteHasMateria.objects.all() 
        logins = Login.objects.filter(privilegio = 2) #solo logins de docentes
        #procedo a eliminar de la BD
        for registro in listaMaterias:
            registro.delete()
        for docente in docentes:
            docente.delete()
        for login in logins:
            login.delete()
        return HttpResponse(u'Docentes eliminados con éxito')
    else:
        return redireccionarAdmin(request)

def inicioAlumno(request):
    try:
        #if request.session['usuario']:
        nombreUsuario = request.session['usuario']
        usuario = Login.objects.get(mail=nombreUsuario)
        try:
            alumno = Alumno.objects.get(idlogin = usuario.idlogin)
        except:
            return redirect('aaev:index')
        #materias solicitadas y aceptadas 
        try:
            materias = AlumnoHasMateria.objects.filter(idalumno = alumno.idalumno).exclude(habilitado = False)
            materias = Materia.objects.filter(alumnohasmateria = materias)
        except (AlumnoHasMateria.DoesNotExist, Materia.DoesNotExist):
            materias=None #si no existen agrego None
        #materias solicitadas pero no aceptadas
        try:
            materiasSolicitadas = AlumnoHasMateria.objects.filter(idalumno = alumno.idalumno).exclude(habilitado = True)
            materiasSolicitadas = Materia.objects.filter(alumnohasmateria = materiasSolicitadas)
        except (AlumnoHasMateria.DoesNotExist, Materia.DoesNotExist):
            materiasSolicitadas = None
        universidades = Universidad.objects.all()
        context = {'alumno': alumno, 'materias': materias,
        'materiasSolicitadas': materiasSolicitadas, 'universidades': universidades}
        return render(request,'inicioAlumno.html', context)
    except KeyError:
        return redirect('aaev:index')

def detallesMateria(request, idMateria): #el alumno selecciona una materia y observa los detalles de la misma
    materia = Materia.objects.get(pk=idMateria);
    dhm = DocenteHasMateria.objects.filter(idmateria = idMateria)
    docentes = Docente.objects.filter(docentehasmateria = dhm)
    context = {'docentes': docentes, 'materia': materia}
    return render(request, 'detallesMateria.html',context)

def inscripcionMateria(request,idMateria):
#el alumno solicita inscribirse a una materia, no esta habilitado
    idAlumno = request.session['alumno']
    idAhm = 0 #id del registro nuevo
    try:
        ahm = AlumnoHasMateria.objects.latest('idalumnohasmateria')
        idAhm  = ahm.idalumnohasmateria + 1
    except(AlumnoHasMateria.DoesNotExist):
        idAhm = 1
    alumnohasmateria = AlumnoHasMateria(idAhm, idAlumno,idMateria, False)
    alumnohasmateria.save()
    return HttpResponse(u"Solicitud enviada con éxito")

#El alumno ingresa el nombre del examen (completo o parcial) para poder encontrarlo mas rapido 
#en la vista, devuelve uno o varios examenes que tienen la palabra en el nombre
def buscarExamen(request, nombreExamen):
    #icontains en el query es como un like sin ser case sensitive, en caso de que
    # se busque la palabra en el medio o al final del STRING
    examenes = Examen.objects.filter(nombre__icontains = nombreExamen).exclude(visible=False)
    context = {'examenesBusqueda':examenes}
    if examenes: #encontro al menos 1 examen
        return render(request,"ajaxResultadoBusquedaExamenes.html",context)
    else:
        return HttpResponse(None)

#carga un div con la lista de examenes de la materia solicitada por el alumno
#devuelve un HTML para popular un div de inicioAlumno.html, que muestra los examenes
#y la funcion para redireccionar al examen mismo
def verExamenesAlumno(request,idMateria):
    materia = Materia.objects.get(pk=idMateria)
    examenes = materia.examen_set.exclude(visible = False)
    context = {'examenes': examenes, 'materia': materia}
    return render(request,'ajaxExamenAlumno.html',context)

#la funcion prepara el examen para el alumno, y la lista de preguntas aleatorias
#que se van a usar, el HTML que devuelve la funcion se encarga de usar los tipos

def realizarExamen(request,idMateria):
    form = request.POST
    idExamen = None
    try:
        idExamen = int(form['idExamenRealizar'])
    except: # en caso de que sea una recarga y el examen no se mande bien en request
        return redirect('aaev:inicioAlumno')
    examen = Examen.objects.get(pk=idExamen)
    #los seteos del examen, con la cantidad de preguntas por unidad y tipo, y valores
    seteosPreguntas = examen.unidadhasexamen_set.all()
    listaAleatorias = []
    #aca a traves de todos los seteos agarro las preguntas aleatoriamente
    #y las meto en la lista, para luego volcarlas en el HTML
    for seteo in seteosPreguntas:
        cantidad = seteo.cantPreguntas
        listaPreguntas = Pregunta.objects.filter(idunidad = seteo.unidad_idunidad, idtipopregunta = seteo.tipopregunta_idtipopregunta)
        #segun la cantidad de preguntas pedidas en el seteo, agarro X aleatoriamente del
        #queryset y meto esas X en la lista
        listaAleatorias.extend(random.sample(listaPreguntas, cantidad))    
    #ver funciones.py
     
    alumno = getAlumno(request)
    context = {'examen': examen,'preguntas': listaAleatorias, 'alumno':alumno}
    return render(request, 'examenAlumno.html', context)
    
def corregirExamen(request,idMateria,idExamen):
    form = request.POST
    idRespuestas = form.getlist('idRespuesta[]')
    idPreguntas = form.getlist('idPregunta[]')
    examen = Examen.objects.get(pk=idExamen)
    #valor para aprobar
    nota = 0
    valorPasar = (60 * examen.totalpuntos)/100 #para pasar >= 60%
    valorSuma = 0.0 #sumatoria de las respuestas que se respondieron bien
    preguntaAux = None #aca guardamos la pregunta que estamos recorriendo actualmente en la correccion
    correctas = True #flag que sirve para saber si entre algunas de las respuestas hubo o no una incorrecta
    listaRespuestas = [] #lista de respuestas enviadas de la pregunta que estoy recorriendo
    listaCorregir = []
    contador = 0
    if idRespuestas:
        for idRespuesta in idRespuestas: #recorro todas las respuestas 
        #y las meto en una lista, si hay n respuestas a una pregunta se meten como sublistas
            if idRespuesta != '':
                contador = contador + 1
                respuesta = Respuesta.objects.get(pk = int(idRespuesta))
                idPregunta = respuesta.idpregunta_id
                if not preguntaAux: #primera vez que recorro ciclo?
                    #preguntaAux = idPregunta
                    preguntaAux = Pregunta.objects.get(pk=int(idPregunta))
                if preguntaAux.idpregunta == idPregunta: #estoy todavia agarrando respuestas de la misma pregunta?
                    listaRespuestas.append(respuesta) #agrego a lista de respuestas
                else:
                    listaCorregir.append(listaRespuestas)
                    listaRespuestas = []
                    respuesta = Respuesta.objects.get(pk=int(idRespuesta)) 
                    listaRespuestas.append(respuesta)
                    preguntaAux =  Pregunta.objects.get(pk=respuesta.idpregunta_id)
                    #return HttpResponse(len(idPreguntas))
            #else:
                #return HttpResponse("Hay datos vacios")
        #la ultima se itera pero no se agrega
        listaCorregir.append(listaRespuestas)
        contador = 0
        contarCorrectas = 0
        listaIncorrectas = []

        for respuestas in listaCorregir:
            contador = contador + 1
            primerRespuesta = respuestas[:1]
            for respuesta in respuestas:
                pregunta = respuesta.idpregunta
                break
            if len(respuestas) == len(pregunta.getCorrectas()):
                #si cambie de pregunta, vamos a corregir la anterior
                #en el "elif": ¿Logre enviar todas las respuestas necesarias para que sea correcta?
                if pregunta.idtipopregunta_id == 1 or pregunta.idtipopregunta_id == 2 or pregunta.idtipopregunta_id == 3: 
                #Verdadero o Falso, MC, MC imagen
                    for respuestaEnviada in respuestas: 
                        if not respuestaEnviada.correcta: #son correctas todas estas respuestas enviadas?
                            correctas = False #hay una que no, no se suman puntos
                            listaIncorrectas.append(pregunta.idpregunta)
                            break
                else:
                    conceptos = pregunta.getCorrectas()
                    i = 0
                    for definicion in respuestas:
                        concepto = conceptos[i]
                        if definicion.idRespuesta_correcta_id != concepto.idRespuesta:
                            correctas = False
                            listaIncorrectas.append(pregunta.idpregunta)
                            break
                        i= i + 1
                if correctas: #Logre enviar todas las correctas y ninguna incorrecta? (ver if arriba)
                    contarCorrectas = contarCorrectas + 1
                    seteo = UnidadHasExamen.objects.get(examen_idexamen_id = examen.idexamen, unidad_idunidad_id = pregunta.idunidad_id, tipopregunta_idtipopregunta_id = pregunta.idtipopregunta_id)
                    valorSuma = valorSuma + (seteo.valorTotal/seteo.cantPreguntas)
                    #traigo seteo para obtener cuanto vale esa pregunta y lo sumo a la suma total de puntos
                correctas = True #reasigno el flag para la proxima lista
        if contarCorrectas == examen.totalpreguntas:
            nota = 10
        else:
            nota = (valorSuma/examen.totalpuntos)*10 #del 1 al 10 es la nota, por eso divido por total y multiplico por 10
    alumno = getAlumno(request) #traigo al alumno del diccionario
    estado = ''
    if valorSuma >= valorPasar: #si el puntaje conseguido supera el necesario esta aprobado, sino desaprobado
        estado = 'Aprobado'
    else:
        estado = 'Desaprobado'
    try: #si este examen fue hecho, lo modifico
        examenRealizado = ExamenHasAlumno.objects.get(idexamen = examen.idexamen, idalumno = alumno.idalumno)
        if examenRealizado.estado != 'Aprobado' and nota > examenRealizado.nota:
            examenRealizado.estado = estado
            examenRealizado.nota = round(nota)
            examenRealizado.nrointentos = examenRealizado.nrointentos + 1 
            examenRealizado.save()
        else:
            examenRealizado.nrointentos = examenRealizado.nrointentos + 1 
            examenRealizado.save()
    except(ExamenHasAlumno.DoesNotExist): #el examen no fue hecho, lo creo
        idExHasAlumno = autoIncrementarIdEHA()
        objeto = ExamenHasAlumno(idExHasAlumno,examen.idexamen,alumno.idalumno,round(nota),1,estado)
        objeto.save()
    if estado == 'Aprobado':
        estilo = "aprobado" #nombre de la clase que va a estilizar el mensaje
        mensaje= u"Felicidades, lograste aprobar el examen superando el 60% del puntaje"
    elif estado == 'Desaprobado':
        estilo ="desaprobado" #nombre de la clase que va a estilizar el mensaje
        mensaje= u"Lamentablemente, desaprobaste el examen por no superar el 60% del puntaje"
    context = {'alumno': alumno, 'nota':int(round(nota)),'mensaje':mensaje, 'estilo': estilo}
    return render(request,'Resultado.html',context) #muestro msj desaprobacion

def inicioDocente(request):
#se carga la pantalla de inicio del docente
    try:
        if request.session['usuario']:
            nombreUsuario = request.session['usuario']
            usuario = Login.objects.get(mail=nombreUsuario)
            try:
                docente = Docente.objects.get(idlogin = usuario.idlogin)
            except:
                return redirect('aaev:index')
            mensaje = ''
            try:
                mensaje = request.session['mensajeExito'] #si vengo de una solicitud agarro el mensaje
                del request.session['mensajeExito'] #borro la entrada de diccionario
            except (KeyError): # si no hay mensaje
                mensaje = None
            try:
                materias = DocenteHasMateria.objects.filter(iddocente=docente.iddocente)
                materias = Materia.objects.filter(docentehasmateria=materias) #materias del docente
                universidades = Universidad.objects.all() 
            except (DocenteHasMateria.DoesNotExist, Materia.DoesNotExist):
                materias=None #si no existen agrego None
            context = {'usuario': usuario, 'docente': docente, 'materias': materias, 'universidades': universidades,
            'mensaje': mensaje}
            return render(request,'inicioDocente.html', context)
        else:
            return redirect('aaev:index')
    except KeyError:
        return redirect('aaev:index')

def indexAdmin(request):
    return render(request,'indexAdmin.html',None)

def logoutAdmin(request):
    del request.session['usuario']
    return redirect('aaev:admin')

def logout(request):
    #try:#si estoy logeado
    usuario = request.session['usuario']
    usuario = Login.objects.get(mail=usuario)
    privilegio = usuario.privilegio
    del request.session['usuario']
    if privilegio == 2:# si soy docente
        del request.session['docente']
    elif privilegio == 3: #sisoy alumno
        del request.session['alumno']
    return redirect('aaev:index')
    #except:
        #return redirect('aaev:index')

def enviarSolicitudMateria(request):
    if request.method == 'POST':
        form = envioSolicitud(request.POST)
        if form.is_valid():
            iddocente = int(request.session['docente'])
            docente = traerDocente(iddocente)
            
            mensaje = form.cleaned_data['mensaje']
            if not mensaje: #si el docente decidio no enviar ningun mensaje...
                mensaje='El docente no ha enviado ningun mensaje'
            ultimo_id = 0 #el ultimo id de la tabla
            try:
                ultima_solicitud = SolicitudMateria.objects.latest('idsolicitud_materia')
                ultimo_id = ultima_solicitud.idsolicitud_materia
            except(SolicitudMateria.DoesNotExist): #si este es la primera solicitud en la tabla...
                ultimo_id = 0
            idsolicitud = ultimo_id + 1
           

            diaHoy = datetime.datetime.now().date() #fecha de hoy (DD/MM/AAAA)
            #datetime.datetime.strptime(str(diaHoy), "%Y-%m-%d").strftime("%d-%m-%Y") #formateo fecha de YYYY/MM/DD a DD/MM/YYYY
            materia = form.cleaned_data['idmateria']
            if materia == 0:
                solicitud = SolicitudMateria(idsolicitud,None,iddocente,diaHoy,mensaje)
            else:
                try:
                    objetoMateria = Materia.objects.get(pk=materia)
                    solicitud = SolicitudMateria(idsolicitud, objetoMateria.idmateria,iddocente,diaHoy,mensaje)
                except(Materia.DoesNotExist):
                    solicitud = SolicitudMateria(idsolicitud, None ,iddocente,diaHoy,mensaje)
                solicitud.save() #guardo en base de datos
                messages.add_message(request, messages.SUCCESS, "Tu solicitud se ha enviado con exito")
            return redirect('aaev:inicioDocente') #vuelvo a cargar el inicio de docente (como si fuera un submit)
        else:
            return redirect('aaev:inicioDocente')
    else:
        return redirect('aaev:inicioDocente')

@ensure_csrf_cookie
def registro(request):
    lista_universidades= Universidad.objects.all()
     #traigo universidades
    context= {'universidades': lista_universidades}
    return render(request, 'Registro.html', context)

"""
def registrar(request):
    if request.method == 'POST':
         form = UserCreationForm(request.POST)
         if form.is_valid():
             if form.privilegio==1:
                 alumno = Alumno(form.nombre, form.apellido, form.dni, form.email, form.clave, form.clave2)

                 return HttpResponseRedirect(reverse_lazy('aaev:formularioRegistro'))
             else:
                 solicitudDocente = SolicitudRegistro(form.nombre, form.apellido, form.dni, form.emailDocente, form.mensaje)
                 solicitudDocente.save()
                 return HttpResponseRedirect(reverse_lazy('aaev:formularioRegistro'))
    else:
        return redirect('aaev:registro')
"""
def traerCarrerasId(request, iduniversidad):
    #if request.method == 'POST':
    iddocente=  int(request.session['docente'])
    docente = Docente.objects.get(pk=iddocente)
    idBusqueda=iduniversidad #agarro el id de la universidad que envio ajax
    universidad = Universidad.objects.get(pk=iduniversidad)
    carreras = universidad.carrera_set.all()
    #uhc= UniversidadHasCarrera.objects.filter(universidad_iduniversidad=idBusqueda)
    #if uhc:
    #   carreras = Carrera.objects.filter(universidadhascarrera=uhc).distinct() #consultas
    if carreras:
        data = {'carreras': carreras, 'iduniversidad': idBusqueda}     
            #return HttpResponse(json.dumps(data), content_type='application/json') #envio el html guardado como cadena de texto
        return render(request, "AjaxCarreras.html", data)
    else:
        mensaje= "No hay carreras disponibles en esta universidad"
        data = {'mensaje': mensaje}
        return render(request, "AjaxCarreras.html", data) 
    """
    else:
        mensaje= "No hay carreras disponibles en esta universidad"
        data = {'mensaje': mensaje}
        return render(request, "AjaxCarreras.html", data)
    """
   # else:
        #error= "Error al ejecutar el request"
        #return HttpResponse(json.dumps(error), content_type='application/json') #envio el html guardado como cadena de texto;

def traerMateriasId(request, iduniversidad, idcarrera): #aca se hace la validacion final de inscripcion
    if request.is_ajax() and request.method=='POST': # si es ajax y post
        #materias = Materia.objects.filter(universidadhascarrera=UniversidadHasCarrera.objects.filter(carrera_idcarrera=idcarrera)) # filtro materias por carrera
        carrera = Carrera.objects.get(pk=idcarrera)
        materias = carrera.materia_set.all()
        docente = traerDocente(int(request.session['docente']))
        materias_noImpartidas = verificarMateriasObtenidas(docente, materias) #saco las materias que tiene acreditadas el docente
        materias_finales = verificarMateriasSolicitadas(docente, materias_noImpartidas) 
        #saco las materias que el docente solicito (evito spam) y termino con una lista con materias limpias
        if materias_finales: #si materias tiene AL MENOS UNA MATERIA
            form = envioSolicitud()
            context = {'materias': materias_finales, 'iduniversidad': iduniversidad, 'idcarrera': idcarrera,
             'mensaje': ''} #agrego uni y carrera para el form
            return render(request, "AjaxMaterias.html", context) #muestro el resultado
        else: # sino...

            mensaje= "No se encuentran materias a las que puedas inscribirte en esta carrera"
            context = {'mensaje': mensaje, 'materias': None, 
            'iduniversidad': iduniversidad, 'idcarrera': idcarrera} #agrego el mensaje a mostrar
            return render(request, "AjaxMaterias.html", context) #cargo html con todas las variables.  
    else:
        return redirect('aaev:inicioDocente')

def traerCarrerasRegistro(request, iduniversidad):
    #if request.is_ajax() and request.method == 'POST':
    idBusqueda=iduniversidad #agarro el id de la universidad que envio ajax
    #uhc= UniversidadHasCarrera.objects.filter(universidad_iduniversidad=idBusqueda)
    #carreras = Carrera.objects.filter(universidadhascarrera=uhc).distinct() #consultas
    universidad = Universidad.objects.get(pk=iduniversidad)
    carreras = universidad.carrera_set.all()
    context = {'carreras': carreras, 'iduniversidad': idBusqueda} 
    return render(request, "AjaxCarrerasRegistro.html", context) #envio el html guardado como cadena de texto
    #else:
     #   return redirect('aaev:index') #envio el html guardado como cadena de texto;

def traerMateriasRegistro(request, iduniversidad, idcarrera): #aca se hace la validacion final de inscripcion
    if request.is_ajax() and request.method=='POST': # si es ajax y post
        #materias = Materia.objects.filter(universidadhascarrera=UniversidadHasCarrera.objects.filter(carrera_idcarrera=idcarrera)) # filtro materias por carrera
        carrera = Carrera.objects.get(pk=idcarrera)
        materias = carrera.materia_set.all()
        context = {'materias': materias, 'iduniversidad': iduniversidad, 'idcarrera': idcarrera,
         'mensaje': ''} #agrego uni y carrera para el form
        return render(request, "AjaxMateriasRegistro.html", context) #muestro el resultado
    else:
        return redirect('aaev:index')

#carga la vista para las solicitudes de alumnos a la materia designada
def solicitudesDeAlumnos(request, idMateria):
    solicitudes = AlumnoHasMateria.objects.filter(idmateria = idMateria, habilitado = False)
    docente = traerDocente(request.session['docente'])
    materia = Materia.objects.get(pk=idMateria)
    context = {'docente': docente, 
    'solicitudes': solicitudes, 
    'materia': materia}
    return render(request, 'solicitudes.html', context)


#muestra detalles de la solicitud del alumno (carga AJAX)
def detallesSolicitud(request, idMateria, idSolicitud):
    solicitud = AlumnoHasMateria.objects.get(idalumnohasmateria= idSolicitud)
    alumno = solicitud.idalumno
    context = {'solicitud': solicitud, 'alumno': alumno}
    return render(request,'detallesSolicitudAlumno.html',context)  
#eliminar el registro donde el alumno tiene la inscripcion parcial a la materia
#debido a que fue rechazado
def rechazarSolicitud(request,idMateria, idSolicitud):
    solicitud = AlumnoHasMateria.objects.get(idalumnohasmateria = idSolicitud)
    solicitud.delete() #elimino la solicitud en la base de datos
    return HttpResponse(u"Solicitud rechazada con éxito")

#cambia el campo 'habilitado' del registro de la inscripcion del alumno a la materia
#dado que fue aceptado
def aceptarSolicitud(request,idMateria ,idSolicitud):
    solicitud = AlumnoHasMateria.objects.get(idalumnohasmateria = idSolicitud)
    solicitud.habilitado = True
    solicitud.save()
    return HttpResponse(u"Solicitud aceptada con éxito")

#rechazo todas las solicitudes de alumno, eliminando todas las inscripciones
def rechazarTodasSolicitudesAlu(request,idMateria):
    if request.method == 'POST':
        solicitudes = AlumnoHasMateria.objects.filter(idmateria = idMateria, habilitado = False)
        for solicitud in solicitudes:
            solicitud.delete()
        return HttpResponse(u"Todas las solicitudes fueron rechazadas con éxito")
    else:
        return redireccionarDocente()
#acepto todas las solicitudes de los alumnos de la materia, habilitandoles el acceso
# a los examenes
def aceptarTodasSolicitudesAlu(request,idMateria):
    if request.method == 'POST':
        solicitudes = AlumnoHasMateria.objects.filter(idmateria = idMateria)
        for solicitud in solicitudes: 
            solicitud.habilitado = True #habilito la solicitud para que el alumno pueda entrar
            solicitud.save()
        return HttpResponse(u"Todas las solicitudes fueron aceptadas con éxito")
    else:
        return redireccionarDocente()


def gestionAlumnos(request, idMateria):
    try:
        registros = AlumnoHasMateria.objects.filter(idmateria = idMateria)
        alumnos = []
        materia = Materia.objects.get(pk=idMateria)
        for registro in registros:
            alumnos.append(registro.idalumno)
        try:
            docente = traerDocente(request.session['docente'])
            context = {'docente': docente, 'alumnos': alumnos, 'materia': materia}
            return render(request,'gestionAlumnos.html',context)
        except('usuario' not in request.session):
            return redirect('aaev:inicio') 
    except('usuario' not in request.session):
        return redireccionarDocente(request)

def detallesAlumno(request,idMateria,idAlumno):
    if request.method == 'POST':
        alumno = Alumno.objects.get(pk=idAlumno)
        materia = Materia.objects.get(pk=idMateria)
        context = {'alumno': alumno, 'materia': materia}
        return render(request,'detallesAlumno.html',context)
    else:
        return redireccionarDocente(request)

def eliminarAlumno(request,idMateria,idAlumno):
    if request.method == 'POST':
        alumno = Alumno.objects.get(pk=idAlumno)
        #materias donde tengo docente inscripto
        alumno_materia = AlumnoHasMateria.objects.filter(idalumno = alumno.idalumno, idmateria = idMateria)
        alumno_materia.delete()
        return HttpResponse(u'Alumno eliminado con éxito')
    else:
        return redireccionarDocente(request)

#elimina todos los alumnos registrados del sistema
def eliminarTodosAlumnos(request, idMateria):
    if request.method == 'POST':
        alumnos = Alumno.objects.all() #todos mis alumnos
        #materias donde tengo alumnos inscriptos
        listaInscriptos = AlumnoHasMateria.objects.filter(idmateria = idMateria) 
        #procedo a eliminar de la BD
        for registro in listaInscriptos:
            registro.delete()
        return HttpResponse(u'Alumnos eliminados de la materia con éxito')
    else:
        return redireccionarDocente(request)

def verUnidadesMateria(request, idMateria):
    try:
        try:
            materia = Materia.objects.get(pk=idMateria) #traigo materia
            unidades = materia.unidad_set.all() #traigo unidades de mi materia
            iddocente = str(request.session['docente'])
            docente = Docente.objects.get(pk=iddocente)
            context = {'materia': materia, 'unidades': unidades, 'docente': docente}
            return render(request, 'unidad.html', context)
        except(Materia.DoesNotExist):
            messages.add_message(request, messages.ERROR, "ERROR: Esa materia no existe.")
            return redirect('aaev:inicioDocente')
    except('docente' not in request.session):
        return redirect('aaev:index')

def agregarUnidad(request,idMateria,nombre):
    if request.method == 'POST' and request.is_ajax():
        ultimo_id = 0 #el ultimo id de la tabla
        try:
            ultima_unidad = Unidad.objects.latest('idunidad')
            ultimo_id = ultima_unidad.idunidad
        except(Unidad.DoesNotExist): #si esta es la primera unidad en la tabla...
            ultimo_id = 0
        idunidad = ultimo_id + 1
        unidad = Unidad(idunidad,nombre,idMateria)
        unidad.save()

        #messages.add_message(request,messages.SUCCESS, u'Unidad agregada con éxito')
        mensaje = "Unidad agregada con exito, tabla actualizada"
        data = {'nombre': nombre, 'mensaje': mensaje, 'idunidad': idunidad}
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        return redirect('aaev:inicioDocente')
#TODO
def eliminarUnidad(request,idMateria,idUnidad):
    if request.method == 'POST' and request.is_ajax(): 
        unidad = Unidad.objects.get(pk=idUnidad)
        materia = Materia.objects.get(pk=idMateria) #traigo materia
        unidades = materia.unidad_set.all() #traigo unidades de mi materia
        iddocente = str(request.session['docente'])
        docente = Docente.objects.get(pk=iddocente)
        context = {'materia': materia, 'unidades': unidades, 'docente': docente}
        examenes = Examen.objects.all()
        examenesEliminar = []
        total = 0
        unidad.delete()
        for examen in examenes: #reviso si se eliminaron seteos de preguntas del examen
            total = 0
            unidadesExamen = examen.unidadhasexamen_set.all()
            for uhe in unidadesExamen:
                total = total + uhe.cantPreguntas #cuento con cuantas preguntas cuenta
                #el examen actualmente
            if examen.totalpreguntas != total: #si se cumple esta condicion es que hay
                examenesEliminar.append(examen) #que borrar el examen
        for examen in examenesEliminar:
            examen.delete()
        return HttpResponse("Unidad eliminada con éxito")
    else:
        return redirect('aaev:inicioDocente')

def editarUnidad(request,idMateria,idUnidad,nombre):
    if request.method == 'POST':
        unidad = Unidad.objects.get(pk=idUnidad)
        unidad.nombre = nombre
        unidad.save() #actualizo el nombre de la unidad.
        mensaje = u"Unidad actualizada con éxito"
        data = {'idUnidad': idUnidad, 'mensaje': mensaje, 'nombre': nombre} #agrego datos para el response
        return HttpResponse(json.dumps(data), content_type="application/json")# devuelvo diccionario
    else:
        return redirect('aaev:inicioDocente')

def verPreguntasMateria(request,idMateria):
    #if request.method=='POST':  
    materia = Materia.objects.get(pk=idMateria)
    if traerCantUnidadesMateria(materia) > 0:
        unidades = materia.unidad_set.all()
        preguntas = []
        for unidad in unidades:
            preguntas.extend(unidad.pregunta_set.all())
        tiposPregunta= Tipopregunta.objects.all()
        docente = traerDocente(request.session['docente'])
        context = {'preguntas': preguntas, 'materia': materia, 'tipos': tiposPregunta, 'unidades':unidades, 'docente': docente}
        return render(request, "preguntas.html", context)
    else:
        context = {vacio: 'True'}
        return render(request, "preguntas.html", context)
    #else:
    #    return redirect('aaev:inicioDocente')

#segun el tipo de pregunta, carga el formulario correspondiente
def formularioTipo(request, idMateria, idTipo):
    if request.method=='POST':
        tipo = Tipopregunta.objects.get(pk=idTipo)
        if tipo.idtipopregunta == 2:
            return render(request, 'formMultiple.html',None)
        if tipo.idtipopregunta == 3:
            return render(request, 'formMultipleImagenes.html', None)
        if tipo.idtipopregunta == 4:
            return render(request, 'formUnion.html',None)
    else:
        return HttpResponse(None)

#realiza el alta de preguntas y sus opciones en la base de datos y devuelve la vista de 
#preguntas, depende el tipo como se ejecuta el algoritmo, ver abajo
def agregarPregunta(request, idMateria):
    form = request.POST
    texto = form['texto']
    idTipo = form['idTipoAgregar']
    unidad = form['idUnidadAgregar']
    mensaje = u"Pregunta agregada con éxito"
    if int(idTipo) == 1: #Tipo: V/F
        opcion = form['opciones']
        if int(opcion) == 1:
            nombreOpcion = "Verdadero"
        elif int(opcion) == 2:
            nombreOpcion = "Falso"
        else:
            messages.add_message(request, messages.ERROR, u"ERROR cargando opciones de V/f")
            return redirect('aaev:verPreguntasMateria', idMateria)
        ultimoId = 0 
        try:
            ultimaPregunta = Pregunta.objects.latest('idpregunta')
            ultimoId = ultimaPregunta.idpregunta + 1
        except(Pregunta.DoesNotExist):
            ultimoId = 1
        pregunta = Pregunta(ultimoId,texto,int(idTipo),int(unidad))
        pregunta.save()
        ultimoId = 0 
        try:
            ultimaRespuesta = Respuesta.objects.latest('idRespuesta')
            ultimoId = ultimaRespuesta.idRespuesta + 1
        except(Respuesta.DoesNotExist):
            ultimoId = 1
        if nombreOpcion == "Verdadero":
            opcionVerdadero = Respuesta(ultimoId, nombreOpcion, True,None,None,None,pregunta.idpregunta)
            opcionFalso = Respuesta(ultimoId + 1, "Falso", False,None,None,None,pregunta.idpregunta)    
            opcionVerdadero.save()
            opcionFalso.save()
        elif nombreOpcion == "Falso":
            opcionVerdadero = Respuesta(ultimoId, "Verdadero", False,None,None,None,pregunta.idpregunta)
            opcionFalso = Respuesta(ultimoId + 1, nombreOpcion, True,None,None,None,pregunta.idpregunta)    
            opcionVerdadero.save()
            opcionFalso.save()
        messages.add_message(request, messages.SUCCESS, mensaje)
        return redirect('aaev:verPreguntasMateria', idMateria)
    if int(idTipo) == 2: #tipo Multiple Choice
        listaCorrectas = form.getlist("respuestasCorrectas[]")
        listaIncorrectas = form.getlist("respuestasIncorrectas[]")
        #return HttpResponse(texto)
        listaRespuestas = []
        #return HttpResponse(listaIncorrectas)
        try:
            ultimaPregunta = Pregunta.objects.latest('idpregunta')
            ultimoId = ultimaPregunta.idpregunta + 1
        except(Pregunta.DoesNotExist):
            ultimoId = 1
        pregunta = Pregunta(ultimoId,texto,int(idTipo),int(unidad))
        pregunta.save()

        for respuesta in listaCorrectas:
            #ultimo_id = autoIncrementarIdRespuesta() + contador
            texto = respuesta
            correcta = True
            objeto = Respuesta(0,texto,correcta,None,None,None,pregunta.idpregunta)
            listaRespuestas.append(objeto)

        for respuesta in listaIncorrectas:
            texto = respuesta
            correcta = False
            objeto = Respuesta(0,texto,correcta,None,None,None,pregunta.idpregunta)
            listaRespuestas.append(objeto)

        #listaRespuestas = listaCorrectas + listaIncorrectas
        shuffle(listaRespuestas) #mezclo lso elementos para que no aparezcan ordenadas las respuestas
        for respuesta in listaRespuestas:
            respuesta.idRespuesta = autoIncrementarIdRespuesta()
            respuesta.save()
        messages.add_message(request, messages.SUCCESS, mensaje)
        return redirect('aaev:verPreguntasMateria', idMateria)
    if int(idTipo) == 3:#tipo multiple choice de imagenes
        formArchivos = request.FILES

    
        listaCorrectas = []
        listaIncorrectas = [] 
        
        for archivo in request.FILES.getlist('imagenesCorrectas'):
            listaCorrectas.append(archivo)
        
        for archivo in request.FILES.getlist('imagenesIncorrectas'):
            listaIncorrectas.append(archivo)
   
        listaRespuestas = []
        descripcionesCorrectas = form.getlist('descripcionesCorrectas[]')
        descripcionesIncorrectas = form.getlist('descripcionesIncorrectas[]')
       
        try:
            ultimaPregunta = Pregunta.objects.latest('idpregunta')
            ultimoId = ultimaPregunta.idpregunta + 1
        except(Pregunta.DoesNotExist):
            ultimoId = 1
        pregunta = Pregunta(ultimoId,texto,int(idTipo),int(unidad))
        pregunta.save()
        i = 0
        #guardo imagenes correctas
        for imagen in listaCorrectas:
            #ultimo_id = autoIncrementarIdRespuesta() + contador
            try:
                descripcion = descripcionesCorrectas[i]
            except:
                descripcion = ''
            correcta = True
            #set_imagen(imagen)
            objeto = Respuesta(0,'Sin texto',correcta,imagen,descripcion,None,pregunta.idpregunta)
            imagenObjeto = objeto.imagen
            objeto.set_imagen(imagenObjeto.read()) #codeo la imagen para guardar en BLOB
            listaRespuestas.append(objeto)
            i = i + 1
        i = 0 #reinicio contador
        #guardo imagenes incorrectas
        for imagen in listaIncorrectas:
            try:
                descripcion = descripcionesIncorrectas[i] #agarro en el mismo indice la descripcion
            except:
                descripcion = ''
            correcta = False
            objeto = Respuesta(0,'Sin texto',correcta,imagen,descripcion,None,pregunta.idpregunta)
            objeto.set_imagen(objeto.imagen.read()) #codeo la imagen para guardar en BLOB
            listaRespuestas.append(objeto)
            i = i + 1

        shuffle(listaRespuestas) #mezclo los elementos para que no aparezcan ordenadas las respuestas
        for respuesta in listaRespuestas:
            respuesta.idRespuesta = autoIncrementarIdRespuesta()
            respuesta.save()
        messages.add_message(request, messages.SUCCESS, mensaje)
        return redirect('aaev:verPreguntasMateria', idMateria)

    if int(idTipo) == 4: #tipo Union de conceptos
        conceptos = form.getlist("conceptos[]")
        definiciones = form.getlist("definiciones[]")
        listaObjetos = [] #guarda definiciones encapsuladas en objetos
        try:
            ultimaPregunta = Pregunta.objects.latest('idpregunta')
            ultimoId = ultimaPregunta.idpregunta + 1
        except(Pregunta.DoesNotExist):
            ultimoId = 1
        pregunta = Pregunta(ultimoId,texto,int(idTipo),int(unidad))
        pregunta.save()

        if len(conceptos) == len(definiciones):
            i = 0
            for concepto in conceptos:
                definicion = definiciones[i]
                definicion = Respuesta(0,definicion,False,None,None,None,pregunta.idpregunta)
                concepto = Respuesta(0,concepto,False,None,None,None,pregunta.idpregunta)
                concepto.idRespuesta = autoIncrementarIdRespuesta()
                definicion.idRespuesta_correcta = concepto
                concepto.save()
                listaObjetos.append(definicion)
                i= i + 1

            shuffle(listaObjetos)
            for definicion in listaObjetos:
                definicion.idRespuesta = autoIncrementarIdRespuesta()
                definicion.save()
            messages.add_message(request, messages.SUCCESS, mensaje)
            return redirect('aaev:verPreguntasMateria', idMateria)
    messages.add_message(request,messages.ERROR,"ERROR")
    return redirect('aaev:verPreguntasMateria', idMateria)
    #return redirect('aaev:verPreguntasMateria', idMateria)
def eliminarPregunta(request,idMateria,idPregunta):
    pregunta = Pregunta.objects.get(pk=idPregunta)
    #opciones = pregunta.respuesta_set.all()
    #de mi examen
    materia = Materia.objects.get(pk=idMateria)
    tipo = pregunta.idtipopregunta
    unidad = pregunta.idunidad
    cantidad = 0
    #saco la cantidad de preguntas del mismo tipo que la eliminada
    #para verificar que pueden cumplir con los encabezados de los examenes
    pregunta.delete() #elimino pregunta
    for pregunta in unidad.pregunta_set.all():
        if pregunta.idtipopregunta_id == tipo.idtipopregunta:
            cantidad = cantidad + 1

    mensaje = ""
    unidadesExamen = UnidadHasExamen.objects.filter(unidad_idunidad_id = unidad.idunidad, tipopregunta_idtipopregunta_id = tipo.idtipopregunta)
    for uhe in unidadesExamen:
        if uhe.cantPreguntas > cantidad: #si lo que exijo de preguntas sobrepasa la cantidad disponible
            mensaje = u"Pregunta eliminada con éxito, se han modificado las cantidades de pregunta de uno o más tipos de pregunta incluidos en los exámenes"
            #resto la cantidad de preguntas con lo que falta para llegar al minimo (diferencia entre cantidad existente y pedida)
            uhe.cantPreguntas = uhe.cantPreguntas - abs(cantidad - uhe.cantPreguntas) 
            if(uhe.cantPreguntas > 0):
                uhe.save()
            else:
                examen = uhe.examen_idexamen
                unidadesDelExamen = UnidadHasExamen.objects.filter(unidad_idunidad_id = unidad.idunidad, tipopregunta_idtipopregunta_id = tipo.idtipopregunta, examen_idexamen = examen)
                valor = uhe.valorTotal
                uhe.delete()    
                if(len(unidadesDelExamen) <= 0):
                    examen.delete() #borro el examen si queda vacio
                else:
                    examen.totalpuntos = examen.totalpuntos - valor
                    examen.totalpreguntas = examen.totalpreguntas - abs(cantidad - uhe.cantPreguntas)
                    examen.save()
    if mensaje == "":
        mensaje = "Pregunta eliminada con éxito"
    return HttpResponse(mensaje)

def detallesPregunta(request, idMateria, idPregunta):
    pregunta = Pregunta.objects.get(pk=idPregunta)
    respuestas = pregunta.respuesta_set.all()
    idTipoPregunta = pregunta.idtipopregunta_id
    unidades = (Materia.objects.get(pk=idMateria)).unidad_set.all()
    context= {'pregunta': pregunta, 'respuestas': respuestas, 'idTipo': idTipoPregunta,
    'unidades': unidades}
    return render(request, 'editarPregunta.html', context)

#edita y guarda en la base de datos los atributos de la pregunta, redirije a la vista de preguntas
#con un mensaje de exito
def editarPregunta(request,idMateria, idPregunta):
    pregunta = Pregunta.objects.get(pk=idPregunta)
    respuestas = pregunta.respuesta_set.all()
    unidad = pregunta.idunidad
    form = request.POST
    idTipo = form['idTipoEditar']
    idUnidad = form['idUnidadEditar']
    texto = form['textoEditar']

    #edicion de pregunta

    if pregunta.texto != texto and texto != '':
        pregunta.texto = texto

    if pregunta.idunidad_id != int(idUnidad):
        unidad = Unidad.objects.get(pk=int(idUnidad))
        pregunta.idunidad = unidad

    pregunta.save()

    #-----------------------
    #edicion de respuestas de la pregunta

    if int(idTipo) == 1:
        nombreOpcion = ""
        opcion = int(form['opcion'])
        if int(opcion) == 1:
            nombreOpcion = "Verdadero"
        elif int(opcion) == 2:
            nombreOpcion = "Falso"
        for respuesta in respuestas:
            #si elijo verdadero y la correcta es falsa invierto
            if respuesta.correcta and respuesta.texto != nombreOpcion:
                respuesta.correcta = False
            #si es la opcion equivocada y seleccione esa en el formulario para que 
            # sea correcta
            if not respuesta.correcta and respuesta.texto == nombreOpcion:
                respuesta.correcta = True
            respuesta.save() #actualizo
        messages.add_message(request,messages.SUCCESS, "Pregunta editada con éxito")
        return redirect("aaev:verPreguntasMateria", idMateria)
    
    elif int(idTipo) == 2:
        listaCorrectas = form.getlist('correctas[]') #lista con textos de respuestas correctas
        listaIncorrectas = form.getlist('incorrectas[]')#lista con textos de respuestas incorrectas
        listaIdCorrectas = form.getlist('idCorrectas[]') #lista con los id de las correctas
        listaIdIncorrectas = form.getlist('idIncorrectas[]') #lista con los id de las incorrectas
        #i  se usa como indice para sacar la respuesta acorde al texto de la misma
        i = 0

        for correcta in listaCorrectas:
            idCorrecta = int(listaIdCorrectas[i])
            respuesta = Respuesta.objects.get(pk=idCorrecta)
            if respuesta.texto != correcta and correcta != '':
                respuesta.texto = correcta
                respuesta.save()
            i = i + 1
        i = 0
        for incorrecta in listaIncorrectas:
            idIncorrecta = int(listaIdIncorrectas[i])
            respuesta = Respuesta.objects.get(pk=idIncorrecta)
            if respuesta.texto != incorrecta and incorrecta != '':
                respuesta.texto = incorrecta
                respuesta.save()
            i = i + 1
       
        messages.add_message(request,messages.SUCCESS, "Pregunta editada con éxito")
        return redirect("aaev:verPreguntasMateria", idMateria)
    #Fin de bloque Multiple Choice
    elif int(idTipo) == 3:
        #listaCorrectas = form.getlist('correctas[]') #lista con textos de respuestas correctas
        #listaIncorrectas = form.getlist('incorrectas[]')#lista con textos de respuestas incorrectas
        listaCorrectas = []
        listaIncorrectas = []
        listaIdCorrectas = form.getlist('idCorrectas[]') #lista con los id de las correctas
        listaIdIncorrectas = form.getlist('idIncorrectas[]') #lista con los id de las incorrectas
        #i  se usa como indice para sacar la respuesta acorde al texto de la misma
        i = 0
        #imagenesCorrectasEditar
        #imagenesIncorrectasEditar
        for archivo in request.FILES.getlist('imagenesCorrectasEditar'):
            listaCorrectas.append(archivo)
        #return HttpResponse(len(formArchivos.getlist('imagenesCorrectas')))
        for archivo in request.FILES.getlist('imagenesIncorrectasEditar'):
            listaIncorrectas.append(archivo)

        descripcionesCorrectas = form.getlist('descripcionesCorrectasEditar[]')
        descripcionesIncorrectas = form.getlist('descripcionesIncorrectasEditar[]')
        
        for imagen in listaCorrectas:
            idCorrecta = int(listaIdCorrectas[i])
            respuesta = Respuesta.objects.get(pk=idCorrecta)
            if imagen != None:
                correctaBase64 = base64.encodestring(imagen.read())
                if respuesta.imagen != correctaBase64 and correctaBase64 != None:
                    respuesta.imagen = correctaBase64
                    respuesta.save()
            i = i + 1
        
        i = 0
        for descripcion in descripcionesCorrectas:
            idCorrecta = int(listaIdCorrectas[i])
            respuesta = Respuesta.objects.get(pk=idCorrecta)
            if respuesta.descripcionimagen != descripcion and descripcion != '':
                respuesta.descripcionimagen = descripcion
                respuesta.save()
            i = i + 1

        i = 0
        for descripcion in descripcionesIncorrectas:
            idIncorrecta = int(listaIdIncorrectas[i])
            respuesta = Respuesta.objects.get(pk=idIncorrecta)
            if respuesta.descripcionimagen != descripcion and descripcion != '':
                respuesta.descripcionimagen = descripcion
                respuesta.save()
            i = i + 1
        i = 0
        for imagen in listaIncorrectas:
            idIncorrecta = int(listaIdIncorrectas[i])
            respuesta = Respuesta.objects.get(pk=idIncorrecta)
            incorrectaBase64 = base64.encodestring(imagen.read())
            if respuesta.imagen != incorrectaBase64 and incorrectaBase64 != None:
                respuesta.imagen = incorrectaBase64
                
                #respuesta.set_imagen(imagen.read())
                respuesta.save()
                #return HttpResponse(respuesta.imagen)
            i = i + 1
        

        messages.add_message(request,messages.SUCCESS, "Pregunta editada con éxito")
        return redirect('aaev:verPreguntasMateria', idMateria)
        #return HttpResponse(pregunta)
    elif int(idTipo) == 4: #inicio de bloque union
        conceptosEditados = form.getlist('conceptos[]')
        definicionesEditadas = form.getlist('definiciones[]')
        idConceptos = form.getlist('idConceptos[]')
        idDefiniciones = form.getlist('idDefiniciones[]')
        respuestas = pregunta.respuesta_set.all()

        i = 0
        for concepto in conceptosEditados:
            respuesta = Respuesta.objects.get(pk = int(idConceptos[i]))
            if not respuesta.idRespuesta_correcta: #es un concepto
                if concepto != respuesta.texto and concepto != '':
                    respuesta.texto = concepto
                    respuesta.save()
            i = i + 1

        i = 0
        for definicion in definicionesEditadas:
            respuesta = Respuesta.objects.get(pk = int(idDefiniciones[i]))
            if respuesta.idRespuesta_correcta:
                if definicion != respuesta.texto and definicion != '':
                    respuesta.texto = definicion
                    respuesta.save()   
            i = i + 1
        messages.add_message(request,messages.SUCCESS, "Pregunta editada con éxito")
        return redirect('aaev:verPreguntasMateria', idMateria)

    #Fin de bloque union
    else:
        return HttpResponse("No es tipo 1 ni 2")

#carga los examenes de la materia, devuelve la vista de examenes donde se pueden gestionar
def verExamenesMateria(request, idMateria):
    try:
        materia = Materia.objects.get(pk=idMateria)
        examenes = materia.examen_set.all()
        unidades = materia.unidad_set.all()
        docente = traerDocente(request.session['docente'])
        tipos = Tipopregunta.objects.all()
        for examen in examenes:
            if examen.fechacierre <= date.today() and not examen.cerrado:
                examen.visible = 0
                examen.cerrado = 1
                examen.save() #actualizo el examen si su fecha de cierre paso 
        context = {'examenes': examenes, 'materia': materia,
         'docente': docente, 'unidades':unidades, 'tipos': tipos}
        return render(request, "examenes.html", context)
    except ('usuario' not in request.session, 'docente' not in request.session):
        return redirect('aaev:index')

def cambiarVisibilidad(request,idMateria, idExamen):
    if request.method == 'POST':
        examen = Examen.objects.get(pk=idExamen)
        examen.visible = not examen.visible
        examen.save()
        return HttpResponse("Hecho")
    else:
        if 'docente' in request.session:
            return redirect('aaev:inicioDocente')
        else:
            return redirect('aaev:index')

def exportarExamen(request,idMateria,idExamen):
    # Crear para devolver tipo PDF
    examen = Examen.objects.get(pk=idExamen)
    nombreArchivo = examen.nombre
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="' + nombreArchivo + '.pdf"'
    #configuro el archivo
    seteosPreguntas = examen.unidadhasexamen_set.all()
    listaAleatorias = []
    #aca a traves de todos los seteos agarro las preguntas aleatoriamente
    #y las meto en la lista, para luego volcarlas en el HTML
    for seteo in seteosPreguntas: #agarro las preguntas aleatorias y las meto en una lista
        cantidad = seteo.cantPreguntas
        listaPreguntas = Pregunta.objects.filter(idunidad = seteo.unidad_idunidad, idtipopregunta = seteo.tipopregunta_idtipopregunta)
        #segun la cantidad de preguntas pedidas en el seteo, agarro X aleatoriamente del
        #queryset y meto esas X en la lista
        listaAleatorias.extend(random.sample(listaPreguntas, cantidad))    
    """
        style = ParagraphStyle( #estilizado de parrafos
            name='Normal',
            fontSize=11,
        )

    for pregunta in listaAleatorias: #recorro preguntas y las escribo en PDF
        # Creo 1 hoja del doc para el PDF
        #pagesize es el tamaño de la hoja, por default se va a usar A4
        #bottomup invierte el sistema de coordenadas, si esta en True el (0,0) es abajo a la 
        #izquierda
        p = canvas.Canvas(response, pagesize = A4, bottomup = False)
        if(p.getPageNumber() == 1): #si es la primer pagina
            titulo = "Examen: " + examen.nombre
            p.drawCentredString(300,50,titulo)
        

            p.setFont("Helvetica", 14)
            #el canvas es una hoja de papel basicamente
        
            p.saveState() #para recuperar el estilo en la prox pagina
        else:
            p.restoreState() #restauro el estilo
        
        if (pregunta.idtipopregunta_id == 1): #si es V/F
            texto = pregunta.texto + ":"
            p.drawString(10, 150,texto)
            opciones = pregunta.respuesta_set.all()
            y = 175
            for opcion in opciones: #recorro opciones de la pregunta
                texto = opcion.texto
                #p.circle(0,y,0.1,0,1)
                p.drawString(40,y,texto)
                #agrego al parrafo
                y = y + 20
        # Dibujo, aca es donde se genera el PDF.
        #p.drawString(10, 10, "Hola mundo.")

        # cierre del PDF.
        p.showPage()
        p.save()
    """
    doc = SimpleDocTemplate(response,pagesize=letter,
                            rightMargin=72,leftMargin=72,
                            topMargin=72,bottomMargin=18)
    Story=[]
    styles=getSampleStyleSheet()#obtengo hojas de estilo
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
    #agrego estilos justificado y centrado para poder hacer el output necesario

    cont = 0 
    texto = '<font size=16>%s</font>' % examen.nombre #nombre del examen
    Story.append(Paragraph(texto,styles["Center"])) #agrego el nombre y lo centro
    Story.append(Spacer(1,30)) #espacio (30 inches)
    for pregunta in listaAleatorias: #voy volcando las preguntas del examen
        #Es V/F o MC? (ambas son iguales en cuanto a como se escriben algoritmicamente)
        if (pregunta.idtipopregunta_id == 1 or pregunta.idtipopregunta_id == 2):
            #escribo enunciado
            ptext = '<font size=12>%s:</font>' % pregunta.texto 
            Story.append(Paragraph(ptext, styles["Normal"]))
            Story.append(Spacer(1, 12))
            opciones = pregunta.respuesta_set.all()
            for opcion in opciones: #escribo las opciones de la pregunta
                ptext2= '<font size=10>%s</font>' % opcion.texto
                #guardo como item de lista
                Story.append(Paragraph(ptext2, styles["Normal"], bulletText = '-'))
                Story.append(Spacer(1,8)) 
        #para Multiple choice de imagen
        if (pregunta.idtipopregunta_id == 3):
            ptext = '<font size=12>%s:</font>' % pregunta.texto 
            Story.append(Paragraph(ptext, styles["Normal"]))
            Story.append(Spacer(1, 12))
            opciones = pregunta.respuesta_set.all()
            for opcion in opciones: #escribo las opciones de la pregunta
                #imagen = base64.decodestring(opcion.imagen)
                imagen = opcion.imagen
                imagen = base64.decodestring(imagen)
                tempBuff = StringIO.StringIO()
                tempBuff.write(imagen)
                tempBuff.seek(0) #need to jump back to the beginning before handing it off to PIL
                #imagen = Image.open(tempBuff)
                #imagen = Image.open(imagen)
                imagen = Image(tempBuff, 2*inch, 2*inch)
                #ptext2= '<font size=10>%s</font>' % opcion.texto
                #guardo como item de lista
                if opcion.descripcionimagen != '':
                    #Story.append(Paragraph('<font size=10>-</font>', styles["Normal"]))
                    Story.append(imagen)
                    Story.append(Paragraph(opcion.descripcionimagen, styles["Normal"], bulletText = '-'))
                else:
                    #Story.append(Paragraph('<font size=10>-</font>', styles["Normal"]))
                    Story.append(imagen)
                Story.append(Spacer(1,8)) 
        #Para la union de conceptos
        if (pregunta.idtipopregunta_id == 4):
            ptext = '<font size=12>%s:</font>' % pregunta.texto 
            Story.append(Paragraph(ptext, styles["Normal"]))
            Story.append(Spacer(1, 12))
            opciones = pregunta.respuesta_set.all()
            listaTabla = []
            listaConceptos = []

            listaDefiniciones = []
            i = 1
            for opcion in opciones:
                if not opcion.idRespuesta_correcta:
                    #numero conceptos para que en un futuro el alumno no tenga problemas uniendo
                    listaConceptos.append(str(i) + ": " + opcion.texto)
                    #le damos un espacio asi no aparecen pegados
                else:
                    listaDefiniciones.append(opcion.texto)
                i = i + 1
            i = 0
            fila = [] 
            for conc in listaConceptos:
                fila.append(conc)
                fila.append(listaDefiniciones[i])
                listaTabla.append(fila)
                fila = []
                i = i + 1
            tabla = Table(listaTabla) #armo tabla
            tabla.setStyle(TableStyle())
            Story.append(tabla) #la agrego al doc
        Story.append(Spacer(1, 20)) #dejo espacio para la siguiente pregunta
    doc.build(Story)

    
    # cierre del PDF.
    #p.showPage()
    #p.save()
    return response
 
def eliminarExamen(request,idMateria,idExamen):
    examen = Examen.objects.get(pk=idExamen)
    lista = UnidadHasExamen.objects.filter(examen_idexamen = idExamen) #traigo las unidades y tipos de pregunta
    #de mi examen
    for unidad in lista:
        unidad.delete() #elimino todas las unidades que se eligieron para el examen
        #evitando basura en la base de datos
    examen.delete() #elimino el encabezado del examen
    return HttpResponse(u"Examen eliminado con éxito")

def agregarExamen(request,idMateria):
    form = request.POST #formulario de alta de examen 
    ultimoId = 0
    try:
        ultimoExamen = Examen.objects.latest('idexamen') #el ultimo examen para permitir realizar la carga
        ultimoId = ultimoExamen.idexamen + 1
    except(Examen.DoesNotExist):
        ultimoId = 1
    
    nombre = form['nombre']
    duracion = ''
    if form['horas'] == '' and form['minutos'] == '': #reviso si el docente ingreso o no duracion
        duracion = '00:00:00'
    else:
        horas = form['horas']#duracion del examen
        minutos = form['minutos']
        duracion = corregirDuracion(horas,minutos)
    
    descripcion = request.POST.get('desc', u'No hay descripción disponible')
    # ^ corrijo en caso de horas y minutos erroneos, ver funciones.py
    fechaCierre = form['fechaCierre'] #agarro fecha como string
    fecha = datetime.datetime.strptime(fechaCierre, "%Y-%m-%d").date()  
    # ^ convierto de string a fecha 
    esVisible = int(form['visibilidad']) #visibilidad del examen.

    unidades = request.POST.getlist('unidades[]') #unidades elegidas
    tiposUnidades = request.POST.getlist('datos[]') #los tipos de unidades para las unidades especificas
    #junto con las mismas
    cantidadesPreguntas = []
    cantidadesPreguntas = request.POST.getlist('cantidadPreguntas[]') #saco la cantidad de preguntas
    valores = []
    valores = filter(bool, request.POST.getlist('valores[]'))
    cantidadesPreguntas = filter(bool, cantidadesPreguntas)

    totalPreguntas = 0
    totalPuntos = 0
    #return HttpResponse(valores)

    for cantidad in cantidadesPreguntas: #calculo el total de preguntas
        if cantidad != '': #aca ignoro la basura que trae el request
            
            totalPreguntas = totalPreguntas + int(cantidad)
        else:
            cantidadesPreguntas.remove(cantidad)
    
    for valor in valores: # calculo el total de puntos 
        if valor != '': #aca ignoro la basura que trae el request
            totalPuntos = totalPuntos + int(valor) 
        else:
            valores.remove(valor)

    examen = Examen(ultimoId,nombre,totalPreguntas,totalPuntos,descripcion,duracion,fecha,esVisible,False,idMateria)
    idExamen = examen.idexamen
    examen.save() #guardo la cabecera
    num = 0
    data = {'unidades': len(tiposUnidades), 'valores': len(valores)
    , 'preguntas': len(cantidadesPreguntas)}
    i=0
    listaDenegados = []
    #probar luego con tiposUnidades
    for unidad in tiposUnidades: #aca lo que hago es guardar en la tabla intermedia las unidades,
    #los tipos elegidos para cada una y la cantidad de preguntas de cada una, para este examen.
        idUhe = autoIncrementarIdUHE()
        array = unidad.split(";") #se crea un array separando en base a la ;
        unidadId = int(array[0]) #el primer elemento tiene el idUnidad
        tipoId = int(array[1]) #el segundo tiene el ID del tipo de pregunta
        if cantidadesPreguntas[i] != '' and valores[i] != '':
            numeroPreguntas = int(cantidadesPreguntas[i]) #recorro a la vez la lista
            # con las cantidades de preguntas
            #return HttpResponse("asd")
            valor = int(valores[i]) # recorro a la vez la lista con el valor del tipo elegido
            objeto = UnidadHasExamen(idUhe,idExamen,unidadId,tipoId,numeroPreguntas,valor)
            objeto.save() #guardo el row en la base de datos
            #i = i + 1 #auto incremento indice para recorrer la lista
        i = i + 1
    messages.add_message(request, messages.SUCCESS, u"Examen agregado con éxito")
    return redirect('aaev:verExamenesMateria', idMateria) #redirijo a vista examenes

    #datos contiene el id de unidad y tipo de pregunta de la siguiente manera:
    # idUnidad;idTipo , idUnidad;idTipo
    # cada nodo es 1 id de unidad y de tipo, la "," separa los nodos y ";" los ID

def detallesExamen(request,idMateria,idExamen):
    examen = Examen.objects.get(pk=idExamen)
    uhe = UnidadHasExamen.objects.filter(examen_idexamen=idExamen)
    unidades = Unidad.objects.filter(idmateria= idMateria)
    tipos =Tipopregunta.objects.all()
    lista = []
    tiposAdentro = []
    for unidad in unidades:
        elemento = [unidad]
        tiposAdentro = []
        for tipo in tipos:
            try:
                unihex = UnidadHasExamen.objects.get(examen_idexamen_id = idExamen, unidad_idunidad_id = unidad.idunidad, tipopregunta_idtipopregunta_id = tipo.idtipopregunta)
            except(UnidadHasExamen.DoesNotExist):   
                preguntas = Pregunta.objects.filter(idunidad = unidad.idunidad, idtipopregunta = tipo.idtipopregunta)
                if preguntas:
                    tiposAdentro.append(tipo)
        if elemento:
            elemento.append(tiposAdentro)
            lista.append(elemento)
        else:
            pass

    for elemento in lista:
        if not elemento[1]:
            lista.remove(elemento)

    context = {'examen': examen, 'unidadesExamen': uhe, 'tipos':tipos,
    'unidades': unidades,'disponibles': lista}
    return render(request,'editarExamen.html',context)
    #return HttpResponse(lista)

def editarExamen(request,idMateria,idExamen):
    form = request.POST #formulario de alta de examen 
    examen = Examen.objects.get(pk=idExamen)
    nombre = form.get('nombre', '')
    descripcion = form.get('descripcionEditar', '')
    duracion = ''
    if form.get('horas', '') == '' and form.get('minutos', '') == '': #reviso si el docente ingreso o no duracion
        duracion = ''
    else:
        horas = form.get('horas', '')#duracion del examen
        minutos = form.get('minutos', '')
        duracion = corregirDuracion(horas,minutos)
    # ^ corrijo en caso de horas y minutos erroneos, ver funciones.py
    
    fechaCierre = form.get('fechaCierre', '') #agarro fecha como string
    fecha = datetime.datetime.strptime(fechaCierre, "%Y-%m-%d").date() if fechaCierre != '' else None 
    # ^ convierto de string a fecha 
    
    examen.nombre = nombre if nombre != '' and nombre != examen.nombre else examen.nombre
    #asignaciones con if acotados en caso que el usuario no haya ingresado el campo
    examen.descripcion = descripcion if descripcion != '' and descripcion != examen.descripcion else examen.descripcion
    examen.tiempoLimite = duracion if duracion != '' else examen.tiempoLimite
    examen.fechacierre = fecha if fecha else examen.fechacierre
    
    #si el docente modifico los seteos registrados (cant preguntas y valores)
    seteosRegistrados = examen.unidadhasexamen_set.all()
    cantPregEditadas = request.POST.getlist('cantidadesEditar[]')
    totalPreguntas = 0
    totalPuntos = 0
    i=0
    #actualizo los seteos que fueron modificados
    for seteo in seteosRegistrados:
        if seteo.cantPreguntas != int(cantPregEditadas[i]):
            seteo.cantPreguntas = int(cantPregEditadas[i])
            seteo.save()
        totalPreguntas = totalPreguntas + seteo.cantPreguntas 
        i = i + 1
    examen.totalpreguntas = totalPreguntas 

    puntosModificados = request.POST.getlist('valoresEditar[]')
    i=0
    for seteo in seteosRegistrados:
        if seteo.valorTotal != int(puntosModificados[i]):
            seteo.valorTotal = int(puntosModificados[i])
            seteo.save()
        totalPuntos = totalPuntos + seteo.valorTotal
        i = i + 1

    examen.totalpuntos = totalPuntos
    examen.save()

    #en caso de que el docente quiera agregar mas preguntas/tipos y unidades al examen...

    #valores = request.POST.getlist('valoresAgregar[]')
    #cantidadesPreguntas = request.POST.getlist('cantidadAgregar[]')
    valores = request.POST.getlist('nuevosValores[]')
    cantidadesPreguntas = request.POST.getlist('nuevasCantidades[]')
    tiposUnidades = request.POST.getlist('nuevosDatos[]')
    #return HttpResponse(len(valores))
    #en caso de que se salte una fila de la tabla de las unidades y tipos disponibles 
    #se limpia la basura de la lista (los campos vacios)
    #return HttpResponse(len(valores))
    valores  = [x for x in valores if not x == '']
    cantidades  = [x for x in cantidadesPreguntas if not x == '']
    if valores and cantidadesPreguntas: #verifico si el docente quiso agregar tiposPregunta a su examen
        for cantidad in cantidadesPreguntas: #calculo el total de preguntas
            if cantidad == '': #aca ignoro la basura que trae el request
                pass
            else: 
                examen.totalpreguntas = examen.totalpreguntas + int(cantidad)
        
        for valor in valores: # calculo el total de puntos 
            if valor == '': #aca ignoro la basura que trae el request
                pass
            else: 
                examen.totalpuntos = examen.totalpuntos + int(valor)

        #tiposUnidades = request.POST.getlist('datosAgregar[]')
        
        i=0
        for unidad in tiposUnidades: #aca lo que hago es guardar en la tabla de intermedia las unidades,
        #los tipos elegidos para cada una y la cantidad de preguntas de cada una, para este examen.
            if cantidadesPreguntas[i] != '' and valores[i] != '':
                idUhe = autoIncrementarIdUHE()
                array = unidad.split(";") #se crea un array separando en base a la ;
                unidadId = array[0] #el primer elemento tiene el idUnidad
                tipoId = array[1] #el segundo tiene el ID del tipo de pregunta
                numeroPreguntas = cantidadesPreguntas[i] #recorro a la vez la lista
                # con las cantidades de preguntas
                valor = valores[i]# recorro a la vez la lista con el valor del tipo elegido
                objeto = UnidadHasExamen(idUhe,idExamen,unidadId,tipoId,numeroPreguntas,valor)
                objeto.save() #guardo el row en la base de datos
            i = i + 1 #auto incremento indice para recorrer la lista
    

    examen.save() #actualizo examen
    messages.add_message(request, messages.SUCCESS, u"Examen editado con éxito")
    return redirect('aaev:verExamenesMateria', idMateria)

def quitarUnidadTipoExamen(request, idMateria, idUnidadHasExamen):
    unidad = UnidadHasExamen.objects.get(pk=idUnidadHasExamen)
    cantidadPreguntas = unidad.cantPreguntas
    totalPuntos = unidad.valorTotal
    examen = unidad.examen_idexamen
    examen.totalpreguntas = examen.totalpreguntas - cantidadPreguntas
    examen.totalpuntos = examen.totalpuntos - totalPuntos
    examen.save() #actualizo puntos y preguntas totales de examen restandole de la parte eliminada
    unidad.delete()
    return HttpResponse(u"Unidad eliminada con éxito, al recargar la página aparecerá en la lista de unidades a agregar")


#------------------------METODOS PARA TEMPLATES--------------------
@register.filter
def contarUniversidades():
    return len(Universidad.objects.all())

@register.filter
def contarCarreras():
    return len(Carrera.objects.all())

@register.filter
def contarMaterias():
    return len(Materia.objects.all())


@register.filter
def contarPreguntas(materia):
    return traerCantPreguntasMateria(materia)

@register.filter
def contarUnidades(materia):
    return traerCantUnidadesMateria(materia)

@register.filter
def contarInscriptos(materia):
    return traerCantInscriptosMateria(materia)

@register.filter
def contarSolicitantes(materia):
    return traerCantSolicitantesMateria(materia)

@register.filter
def contarExamenes(materia):
    return traerCantExamenesMateria(materia)

@register.filter
def vacio(numero):
    if numero==0:
        return True
    else:
        return False

@register.filter
def contarRespuestas(pregunta):
    return len(pregunta.respuesta_set.all())

@register.filter
def traerCarreras(universidad):
    carreras = universidad.carrera_set.all()
    """
    iduniversidad = universidad.iduniversidad
    try:
        uhc= UniversidadHasCarrera.objects.filter(universidad_iduniversidad=iduniversidad)
        carreras = Carrera.objects.filter(universidadhascarrera=uhc).distinct()
    except:
        return None
    """
    return carreras

@register.filter
def traerMaterias(carrera):
    materias = carrera.materia_set.all()
    """
    try:
        uhc = UniversidadHasCarrera.objects.filter(carrera_idcarrera=carrera.idcarrera)
        materias = Materia.objects.filter(universidadhascarrera=uhc).distinct()
    except:
        return None
    """
    return materias
#los filtros de template solo aceptan un solo parametro, por eso se pasa una cadena de texto
@register.filter
def contarPreguntasPorTipo(unidad, tipo): #cuantas preguntas de que tipo hay en esta unidad?
    #los parametros son de tipo objeto
    idTipo = tipo.idtipopregunta#obtengo id del objeto TipoPregunta
    id = unidad.idunidad #saco id del objeto unidad
    preguntas = Pregunta.objects.filter(idunidad=id, idtipopregunta=idTipo)
    return len(preguntas) #hay X preguntas de este tipo en esta Unidad

@register.filter 
def contarTodosTipos(unidad): #cuantas preguntas de cualquier tipo hay en esta unidad?
    #cuantas preguntas de que tipo hay en esta unidad?
    #los parametros son de tipo objeto
    id = unidad.idunidad #saco id del objeto unidad
    preguntas = Pregunta.objects.filter(idunidad=id)
    return len(preguntas) #hay X preguntas de este tipo en esta Unidad

@register.filter
def tieneUnidad(idExamen,idUnidad): #me fijo si el examen tiene la unidad que se busca
    try:
        unidadesConTipos = UnidadHasExamen.objects.filter(examen_idexamen=idExamen).filter(unidad_idunidad=idUnidad)
        #reviso si esta mi unidad integrada en el examen
        return 1
    except(UnidadHasExamen.DoesNotExist):
        return 0

@register.filter
def estaInscripto(materia, alumno):
    idmateria = materia.idmateria
    idalumno = alumno.idalumno
    try:
        ahm = AlumnoHasMateria.objects.get(idmateria = idmateria, idalumno = idalumno)
        if ahm and not ahm.habilitado:
            return False
        else:
            return True
    except(AlumnoHasMateria.DoesNotExist):
        return False

@register.filter
def getNombreMateria(idMateria):
    materia = Materia.objects.get(pk=idMateria)
    return materia.nombre

@register.filter
def getIdUnidad(elemento):
    return elemento[0].idunidad

@register.filter
def getNombreUnidad(elemento):
    return elemento[0].nombre

@register.filter
def getNombreTipoPregunta(elemento):
    array = elemento.split(";") 
    idTipoPregunta = array[0]
    tipo = Tipopregunta.objects.get(pk=idTipoPregunta)
    return tipo.nombretipo

@register.filter
def getUnidad(elemento):
    return elemento[0]

@register.filter
def cantidadPreguntasLista(elemento):
    array = elemento.split(";")
    idUnidad = array[0]
    idtipo = array[1]
    preguntas = Pregunta.objects.filter(idunidad = idUnidad).filter(idtipopregunta = idtipo)
    return len(preguntas)

@register.filter
def obtenerSublista(elemento):
    return elemento[1]

@register.filter
def contarPreguntasEnSublista(unidad, tipo):
    idUnidad = unidad[0].idunidad
    idtipo = tipo.idtipopregunta
    preguntas = Pregunta.objects.filter(idunidad = idUnidad).filter(idtipopregunta = idtipo)
    return len(preguntas)

@register.filter
def getCarreras(universidad):
    return universidad.carrera_set.all()

@register.filter
def getCarrera(materia):
    return materia.idcarrera

@register.filter
def getPreguntas(unidad):
    return unidad.pregunta_set.all()

@register.filter
def sonIguales(variable1, variable2):
    return variable1 == variable2

@register.filter
def getImagen(respuesta):
    return respuesta.get_imagen(respuesta.imagen)


@register.filter
def getUnidadesExamen(examen):
    lista = examen.unidadhasexamen_set.all().distinct()
    nombres = []
    #evito duplicidad de unidades para mostrar
    for elemento in lista:
        if elemento.unidad_idunidad.nombre not in nombres:
            nombres.append(elemento.unidad_idunidad.nombre)
            
    return nombres
@register.filter
def getRespuestas(pregunta):
    return pregunta.respuesta_set.all()

@register.filter
def getConceptos(pregunta):
    lista = pregunta.respuesta_set.filter(idRespuesta_correcta = None)
    return lista

@register.filter
def getDefiniciones(pregunta):
    return pregunta.respuesta_set.all().exclude(idRespuesta_correcta = None)

@register.filter
def contarExamenesHechos(materia, alumno):
    lista = ExamenHasAlumno.objects.filter(idalumno = alumno.idalumno)
    devolver = []
    for exa in lista:
        if exa.idexamen.idmateria.idmateria == materia.idmateria:
            devolver.append(exa)
    return len(devolver)

@register.filter
def a_char(valor):
    return chr(98-valor)