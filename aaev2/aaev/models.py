# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [app_label]'
# into your database. 
from __future__ import unicode_literals 
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

import base64 #para formatear las imagenes en BLOB

class Admin(models.Model):
    idadmin = models.IntegerField(primary_key = True, db_column='idAdmin')
    usuario = models.CharField(db_column = 'usuario', max_length = 45)
    clave = models.CharField(db_column = 'clave', max_length = 45)
    email = models.CharField(db_column = 'email', max_length = 45)
    nombre = models.CharField(db_column = 'nombre', max_length = 45)
    apellido = models.CharField(db_column = 'apellido', max_length = 45)

    class Meta:
        managed = False
        db_table = 'admin'

    def __str__(self):
        return self.usuario

class Alumno(models.Model):
    idalumno = models.IntegerField(primary_key = True, db_column='idAlumno')  # Field name made lowercase.
    nombre = models.CharField(db_column='nombre',max_length=45)
    apellido = models.CharField(db_column='apellido',max_length=45)
    mail = models.CharField(db_column='mail',max_length=45)
    dni = models.CharField(db_column='dni', max_length=10)
    idlogin = models.ForeignKey('Login', db_column='idLogin', on_delete=models.CASCADE)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alumno'


class AlumnoHasMateria(models.Model):
    idalumnohasmateria = models.IntegerField(db_column="idAlumnohasmateria", primary_key = True)
    idalumno = models.ForeignKey(Alumno, db_column='idAlumno', on_delete=models.CASCADE)  # Field name made lowercase.
    idmateria = models.ForeignKey('Materia', db_column='idMateria', on_delete=models.CASCADE)  # Field name made lowercase.
    habilitado = models.BooleanField(db_column = 'habilitado', default = False)

    class Meta:
        managed = False
        db_table = 'alumno_has_materia'


class Carrera(models.Model):
    idcarrera = models.IntegerField(db_column='idCarrera', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=45)
    cantidadanios = models.IntegerField(db_column='cantidadAnios')  # Field name made lowercase.
    iduniversidad = models.ForeignKey('Universidad', db_column='idUniversidad',on_delete=models.CASCADE)
    class Meta:
        managed = False
        db_table = 'carrera'

    def __str__(self):
        return self.nombre


class Docente(models.Model):
    iddocente = models.IntegerField(primary_key=True, db_column='idDocente')  # Field name made lowercase.
    nombre = models.CharField(max_length=45)
    apellido = models.CharField(max_length=45)
    mail = models.CharField(max_length=45)
    dni = models.TextField()
    idlogin = models.ForeignKey('Login', db_column='idLogin', on_delete=models.CASCADE)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'docente'


class DocenteHasMateria(models.Model):
    iddocentehasmateria = models.IntegerField(db_column='idDocenteHasMateria', primary_key=True)
    iddocente = models.ForeignKey('Docente', db_column='idDocente', on_delete=models.CASCADE)  # Field name made lowercase.
    idmateria = models.ForeignKey('Materia', db_column='idMateria', on_delete=models.CASCADE)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'docente_has_materia'

class Examen(models.Model):
    idexamen = models.IntegerField(db_column='idExamen', primary_key = True)  # Field name made lowercase.
    nombre = models.CharField(db_column='nombre', max_length = 70)
    totalpreguntas = models.IntegerField(db_column='totalPreguntas')  # Field name made lowercase.
    totalpuntos = models.FloatField(db_column='totalPuntos')  # Field name made lowercase.
    descripcion = models.TextField(db_column= 'descripcion', blank=True)
    tiempoLimite = models.TimeField(db_column='tiempoLimite')
    fechacierre = models.DateField(db_column='fechaCierre')  # Field name made lowercase.
    visible = models.IntegerField(db_column='visible')
    cerrado = models.IntegerField(db_column='cerrado')
    idmateria = models.ForeignKey('Materia', db_column='idMateria', on_delete=models.CASCADE)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'examen'

    def __str__(self):
        return self.nombre

class ExamenHasAlumno(models.Model):
    idexamenhasalumno = models.IntegerField(db_column='idExamenHasAlumno', primary_key = True)
    idexamen = models.ForeignKey(Examen, db_column='idExamen', on_delete=models.CASCADE)  # Field name made lowercase.
    idalumno = models.ForeignKey(Alumno, db_column='idAlumno', on_delete=models.CASCADE)  # Field name made lowercase.
    nota = models.FloatField()
    nrointentos = models.IntegerField(db_column='nroIntentos')  # Field name made lowercase.
    estado = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'examen_has_alumno'


class Login(models.Model):
    idlogin = models.IntegerField(db_column='idLogin', primary_key=True)  # Field name made lowercase.
    mail = models.CharField(max_length=45)
    clave = models.CharField(max_length=45)
    privilegio = models.IntegerField()
    activo = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'login'

    def __str__(self):
        return self.usuario


class Materia(models.Model):
    idmateria = models.IntegerField(db_column='idMateria', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=45)
    aniocarrera = models.IntegerField(db_column='anioCarrera')  # Field name made lowercase.
    idcarrera = models.ForeignKey('Carrera', db_column='idCarrera', on_delete=models.CASCADE)
    class Meta:
        managed = False
        db_table = 'materia'

    def __str__(self):
        return self.nombre




@python_2_unicode_compatible
class Pregunta(models.Model):
    idpregunta = models.IntegerField(db_column='idPregunta', primary_key="True")  # Field name made lowercase.
    texto = models.TextField(db_column='texto')
    idtipopregunta = models.ForeignKey('Tipopregunta', db_column='idTipoPregunta')  # Field name made lowercase.
    idunidad = models.ForeignKey('Unidad', db_column='idUnidad', on_delete=models.CASCADE)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pregunta'

    def traerUnidad(self):
        return Unidad.objects.get(pk=self.idunidad)

    def __str__(self):
        return self.texto

    def getCorrectas(self):
        if self.idtipopregunta_id != 4:
            return self.respuesta_set.exclude(correcta = False)
        else: #solo devuelve conceptos
            lista = self.respuesta_set.all()
            listaConceptos = []
            for respuesta in lista:
                if not respuesta.idRespuesta_correcta:
                    listaConceptos.append(respuesta)
            return listaConceptos

class Respuesta(models.Model):
    idRespuesta = models.IntegerField(db_column='idRespuesta', primary_key="True")  # Field name made lowercase.
    texto = models.TextField(db_column = 'texto')
    correcta = models.IntegerField(db_column = 'correcta')
    imagen = models.TextField(db_column='imagen', blank=True)
    descripcionimagen = models.CharField(db_column='descripcionImagen', max_length=45, blank=True)  # Field name made lowercase.
    idRespuesta_correcta = models.ForeignKey('self', db_column='idRespuesta_correcta', blank=True, null=True, on_delete=models.CASCADE)  # Field name made lowercase.
    idpregunta = models.ForeignKey('Pregunta', db_column='idPregunta', on_delete=models.CASCADE)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'respuesta'
    
    def __str__(self):
        return self.texto

    def set_imagen(self,data):
        self.imagen = base64.encodestring(data)

    def get_imagen(self,data):
        return base64.decodestring(data)
    """
        _data = models.TextField(
            db_column='data',
            blank=True)

    def set_data(self, data):
        self._data = base64.encodestring(data)

    def get_data(self):
        return base64.decodestring(self._data)

    data = property(get_data, set_data)
    """


class SolicitudMateria(models.Model):
    idsolicitud_materia = models.IntegerField(db_column='idSolicitud_materia', primary_key=True)  # Field name made lowercase.
    materia_idmateria = models.ForeignKey(Materia, db_column='Materia_idMateria', blank = True)  # Field name made lowercase.
    docente_iddocente = models.ForeignKey(Docente, db_column='Docente_idDocente')  # Field name made lowercase.
    fecha = models.DateField()
    mensaje = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'solicitud_materia'


class SolicitudRegistro(models.Model):
    idsolicitud_registro = models.IntegerField(db_column='idSolicitud_Registro', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=45)
    apellido = models.CharField(max_length=45)
    mail = models.CharField(max_length=45)
    dni = models.TextField(max_length=30)
    idmateria = models.IntegerField(blank = True)
    solicitud = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'solicitud_registro'


class Tipopregunta(models.Model):
    idtipopregunta = models.IntegerField(db_column='idTipoPregunta', primary_key=True)  # Field name made lowercase.
    nombretipo = models.CharField(db_column='nombreTipo', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipopregunta'

    def __str__(self):
        return self.nombretipo

@python_2_unicode_compatible
class Unidad(models.Model):
    idunidad = models.IntegerField(db_column='idUnidad', primary_key="True")  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=45)  # Field name made lowercase.
    idmateria = models.ForeignKey(Materia, db_column='idMateria', on_delete=models.CASCADE)  # Field namemade lowercase.

    class Meta:
        managed = False
        db_table = 'unidad'

    def __str__(self):
        return self.nombre


class UnidadHasExamen(models.Model):
    idunidadhasexamen = models.IntegerField(primary_key = True, db_column = 'idUnidadHasExamen')
    examen_idexamen = models.ForeignKey(Examen,  db_column = 'Examen_idExamen', on_delete=models.CASCADE)  # Field name made lowercase.
    unidad_idunidad = models.ForeignKey(Unidad, db_column = 'Unidad_idUnidad', on_delete=models.CASCADE)  # Field name made lowercase.
    tipopregunta_idtipopregunta = models.ForeignKey(Tipopregunta,  db_column='tipoPregunta_idTipoPregunta')
    cantPreguntas = models.IntegerField(db_column='cantPreguntas')
    valorTotal = models.IntegerField(db_column='valorTotal') 
    class Meta:
        managed = False
        db_table = 'unidad_has_examen'

    def __str__(self):
        return str(self.unidad_idunidad)

class Universidad(models.Model):
    iduniversidad = models.IntegerField(db_column='idUniversidad', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=100)  # Field name made lowercase.
    dominiomail = models.CharField(db_column='dominioMail', max_length=45)  # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'universidad'

    def __str__(self):
        return self.nombre


"""
class UniversidadHasCarrera(models.Model):

    universidad_iduniversidad = models.ForeignKey(Universidad, db_column='Universidad_idUniversidad', primary_key=True )  # Field name made lowercase.
    carrera_idcarrera = models.ForeignKey(Carrera, db_column='Carrera_idCarrera', primary_key=True)  # Field name made lowercase.
    materia_idmateria = models.ForeignKey(Materia, db_column='Materia_idMateria', primary_key=True)  # Field name made lowercase.
#Django necesita que las tablas tengan una PK definida, para esto se agrega primery_key=True, sino falla
    class Meta:
        managed = False
        db_table = 'universidad_has_carrera'
    def __str__(self):
        return self.carrera_idcarrera

La consulta en las tablas intermedias es la siguiente
Quiero obtener las carreras de una universidad
carreras_qs = UniversidadHasCarrera.objecs.filter(universidad_iduniversidad=1)
------
osea que primero agarro el queryset de la universidad
luego filtro por el objeto implicito que esta adentro del modelo, si es igual al
queryset saca las carreras que tiene esa uni. Luego se hace:
----
carreras= Carrera.objects.filter(universidadhascarrera=carreras_qs)
"""