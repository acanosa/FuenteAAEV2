# -*- coding: utf-8 -*-
from aaev.models import *
from django.shortcuts import redirect #redireccionar a una url 

def validarLogin(usuario, clave):
    try:
        usuario = Login.objects.get(mail=usuario)
        if clave == usuario.clave:
            return True #si la contraseña coincide
        else:
            return False #si no coincide
    except (Login.DoesNotExist):
        return False #si no existe usuario

def validarLoginAdmin(usuario, clave):
    try:
        usuario = Admin.objects.get(usuario=usuario)
        if clave == usuario.clave:
            return True #si la contraseña coincide
        else:
            return False #si no coincide
    except (Admin.DoesNotExist):
        return False #si no existe usuario
"""
def queryCarreras(idBusqueda,docente):
    idBusqueda=iduniversidad #agarro el id de la universidad que envio ajax
    uhc= UniversidadHasCarrera.objects.filter(universidad_iduniversidad=idBusqueda)
    carreras = Carrera.objects.filter(universidadhascarrera=uhc) #consultas
    data = {'carreras': carreras, 'iduniversidad': idBusqueda}
"""
def traerDocente(idDocente):
    try:
        docente= Docente.objects.get(pk=idDocente)
    except:
        docente= None;    
    return docente

def verificarMateriasSolicitadas(docente, materias):
    try: #evito el spam de solicitudes de materia (osea enviar 20 solicitudes para UNLa/Sistemas/Mate I)
        materias_solicitadas = SolicitudMateria.objects.filter(docente_iddocente = docente.iddocente) # agarro materias que estan en solicitud
        materias_models = Materia.objects.filter(solicitudmateria = materias_solicitadas)
        materias_actualizadas = [x for x in materias if x not in materias_models] #agrego las materias que no fueron solicitadas
        return materias_actualizadas
    except(SolicitudMateria.DoesNotExist): #si no hay registros en esa tabla
        return materias

def verificarMateriasObtenidas(docente, materias):
    try: # aca busco las materias que el docente YA imparte, para evitar mandar solicitudes de materias donde ya esta
        materias_docente = DocenteHasMateria.objects.filter(iddocente=docente.iddocente) #filtro por docente, aca tengo los registros
        #de la  tabla varios a varios
        materias_lista = Materia.objects.filter(docentehasmateria = materias_docente)
        #aca arriba comparo la "foreign key" oculta de django a la tabla intermedia donde saco las materias que saque en
        #materias_docente
        materias_actualizadas = [x for x in materias if x not in materias_lista] #agrego las materias qe no estan en las del docente
        return materias_actualizadas 
    except(DocenteHasMateria.DoesNotExist):
        return materias

def traerInscriptosMateria(materia):
    try:
        lista_alumnos_habilitados= AlumnoHasMateria.objects.filter(idmateria=materia).exclude(habilitado = False)
        habilitados = Alumno.objects.filter(alumnohasmateria=lista_alumnos_habilitados)
        #traigo alumnos y excluyo a los que ya estan habilitados
    except:
        return None
    return habilitados

def traerCantInscriptosMateria(materia):
    try:
        lista = traerInscriptosMateria(materia)
        cantidad = len(lista)
    except:
        return 0
    return cantidad


def traerSolicitantesMateria(materia):
    try:
        lista_solicitantes = AlumnoHasMateria.objects.filter(idmateria=materia).exclude(habilitado = True)
        solicitantes = Alumno.objects.filter(alumnohasmateria=lista_solicitantes)
        #traigo alumnos y excluyo a los que ya estan habilitados
    except:
        return None
    return solicitantes

def traerCantSolicitantesMateria(materia):
    try:
        lista = AlumnoHasMateria.objects.filter(idmateria=materia).exclude(habilitado = True)
        #traigo alumnos y excluyo a los que ya estan habilitados
        cantidad = len(lista)
    except:
        return 0
    return cantidad

def traerCantUnidadesMateria(materia): #traigo cantidad de unidades
    try:
        unidades = materia.unidad_set.all()
        unidadesCant=len(unidades)
    except:
        return 0
    return unidadesCant

def traerUnidadesMateria(materia): #traigo las unidades
    try:
        unidades = materia.unidad_set.all()
    except:
        return None
    return unidades

def traerExamenesMateria(materia): #traigo examenes
    try:
        examenes = materia.pregunta_set.all()
    except:
        return None
    return examenes

def traerCantExamenesMateria(materia): #obtengo cantidad de examenes
    try:    
        examenes= materia.examen_set.all()
        examenesCant= len(examenes)
        return examenesCant
    except:
        return 0



def traerCantPreguntasUnidad(unidad): #traigo cantidad de preguntas
    try:
        preguntas = unidad.pregunta_set.all()
        preguntasCant=len(preguntas)
    except:
        return 0
    return preguntasCant

def traerCantPreguntasMateria(materia):
    unidades = materia.unidad_set.all()
    preguntas= []
    cantPreguntas = 0
    for unidad in unidades:
        preguntas = unidad.pregunta_set.all()
        cantPreguntas = cantPreguntas + len(preguntas)
    return cantPreguntas

    

def traerCarrerasId(request):
    iduniversidad=request.POST['iduniversidad'] #agarro el id de la universidad que envio ajax
    universidad = Universidad.objects.get(pk=iduniversidad)
    carreras = universidad.carrera_set.all()
    """
    try:
        uhc= UniversidadHasCarrera.objects.filter(universidad_iduniversidad=iduniversidad)
        carreras = Carrera.objects.filter(universidadhascarrera=uhc)
    except:
        return None
    """
    return carreras

def diccionarioModelosUltimosId(nombreModelo):
    return {
        'docente': traerUltimoIdDocente(),
        'login': traerUltimoIdLogin(),
        'solicitudmateria': traerUltimoIdSolicitudMateria(),
        'solicitudregistro': traerUltimoIdSolicitudRegistro(),
    }[nombreModelo]

#redirecciona al inicio del administrador, o al inicio de la pag web si no esta logeado
def redireccionarAdmin(request):
    try:
        request.session['usuario']
        request.session['docente']
        return redirect('aaev:inicioDocente')
    except ('usuario' not in request.session, 'docente' not in request.session):
        return redirect('aaev:inicio')

def redireccionarDocente(request):
    try:
        request.session['usuario']
        return redirect('aaev:inicioAdmin')
    except ('usuario' not in request.session):
        return redirect('aaev:inicio')

def traerUltimoIdDocente():
    docente = Docente.objects.latest('iddocente')
    return docente.iddocente

def traerUltimoIdLogin():
    login = Login.objects.latest('idlogin')
    return login.idlogin

def traerUltimoIdSolicitudRegistro():
    solicitud = SolicitudRegistro.objects.latest('idsolicitud_registro')


def traerUltimoIdSolicitudMateria():
    solicitud = SolicitudMateria.objects.latest('idsolicitud_materia')

def corregirDuracion(horas, minutos):
    """la funcion se centra en establecer un 
    limite de horas y controlar que la cantidad de minutos no se exceda
    del limite (60 obviamente) y corregir la cadena de texto en caso de caracteres faltantes
    """
    if int(horas) > 5:
        horas = "5"
        minutos = "00"
    if len(horas) == 1:
        horas = "0" + horas
    if len(minutos) == 1:
        minutos = "0" + minutos
    if int(minutos) >= 60 and int(horas) < 5:
        horas = str(int(horas) + 1)
        minutos = str(int(minutos) - 60)
    elif int(minutos) > 59:
        minutos = "00"
    duracion = horas + ":" + minutos + ":00"
    return duracion
    
#autoincrementer Unidad_has_examen
def autoIncrementarIdUHE():
    try:
        ultimo = UnidadHasExamen.objects.latest('idunidadhasexamen')
        idUhe = ultimo.idunidadhasexamen + 1
        return idUhe
    except(UnidadHasExamen.DoesNotExist):
        idUhe = 1
        return idUhe

#autoincrementer Docente_has_materia
def autoIncrementarIdDHM():
    try:
        ultimo = DocenteHasMateria.objects.latest('iddocentehasmateria')
        idDhm = ultimo.iddocentehasmateria + 1
        return idDhm
    except(DocenteHasMateria.DoesNotExist):
        idDhm = 1
        return idDhm
def autoIncrementarIdRespuesta():
    try:
        ultimo = Respuesta.objects.latest('idRespuesta')
        idRta = ultimo.idRespuesta + 1
        return idRta
    except(Respuesta.DoesNotExist):
        idRta = 1
        return idRta
#autoincrementar Examen_Has_Alumnov
def autoIncrementarIdEHA():
    try:
        ultimo = ExamenHasAlumno.objects.latest('idexamenhasalumno')
        idEHA = ultimo.idexamenhasalumno + 1
        return idEHA
    except(ExamenHasAlumno.DoesNotExist):
        return 1

#devuelve el admin logeado
def getAdmin(usuario):
    return Admin.objects.get(usuario = usuario)



#Devuelve el alumno que esta logeado
#si no hay nadie logeado devuelve un objeto nulo
def getAlumno(request):
    try:
        nombreUsuario = request.session['usuario']
        usuario = Login.objects.get(mail=nombreUsuario)
        alumno = Alumno.objects.get(idlogin = usuario.idlogin)
        return alumno
    except:
        return None
"""
def set_imagen(data):
        return base64.encodestring(data)

    def get_imagen(self,data):
        return base64.decodestring(data)
"""
def obtenerPrimerElemento(lista):
    if lista:
        for elemento in lista:
            return elemento
    else:
        return None