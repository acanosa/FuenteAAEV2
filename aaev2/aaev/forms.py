from django import forms #formularios genericos
from aaev.models import *
from django.forms import ModelForm

##-------------------------FORM DE MODELOS PARA ABM--------------------
class LoginForm(ModelForm):
    class Meta:
        model = Login
        fields = ['mail', 'clave']

class adminLoginForm(ModelForm):
    class Meta:
        model = Admin
        fields = ['usuario', 'clave']

class envioSolicitud(ModelForm): #no hereda de Models.form

    idmateria= forms.IntegerField(required = False)

    class Meta:
        model = SolicitudMateria
        fields= ['idmateria','mensaje']
    
    def clean(self): #limpio datos y verifico si es valido
        cleaned_data= super(envioSolicitud, self).clean()
        idmateria = self.cleaned_data.get('idmateria')
        mensaje = self.cleaned_data.get('mensaje')
        if mensaje or idmateria:
            return cleaned_data
        else:
            raise forms.ValidationError('Escribi un mensaje o elegi una materia.')

class registroAlumnoForm(ModelForm):

    clave = forms.CharField(required = True)
    email = forms.CharField(required = True)
    class Meta:
        model = Alumno
        fields=['nombre','apellido','dni']

    def clean(self): #limpio datos y verifico si es valido
        cleaned_data= super(registroAlumnoForm, self).clean()
        nombre = self.cleaned_data.get('nombre')
        apellido = self.cleaned_data.get('apellido')
        email = self.cleaned_data.get('email')
        dni = self.cleaned_data.get('dni')
        clave = self.cleaned_data.get('clave')
        return cleaned_data

class solicitudRegistroForm(ModelForm):

    idmateria= forms.IntegerField(required = False)
    
    class Meta:
        model = SolicitudRegistro
        fields = ['nombre','apellido','mail', 'dni', 'idmateria', 'solicitud']

    def clean(self):
        cleaned_data = super(solicitudRegistroForm, self).clean()
        nombre = self.cleaned_data.get('nombre')
        apellido = self.cleaned_data.get('apellido')
        email = self.cleaned_data.get('mail')
        dni = self.cleaned_data.get('dni')
        idmateria = self.cleaned_data.get('idmateria')
        solicitud = self.cleaned_data.get('solicitud')
        return cleaned_data

class agregarUnidadForm(ModelForm):
    class meta:
        model = Unidad
        fields = ['nombre']

    def clean(self):
        cleaned_data = super(agregarUnidadForm, self).clean()
        nombre = self.cleaned_data.get('nombre')
        return cleaned_data

class agregarUniversidadForm(ModelForm):
    class Meta:
        model = Universidad
        fields = ['nombre', 'dominiomail']
        
    def clean(self):
        cleaned_data = super(agregarUniversidadForm, self).clean()
        nombre = self.cleaned_data.get('nombre')
        dominiomail = self.cleaned_data.get('dominiomail')
        return cleaned_data

class agregarCarreraForm(ModelForm):

    #iduniversidad = forms.IntegerField(required = True)

    class Meta:
        model = Carrera
        fields = ['nombre', 'cantidadanios','iduniversidad']
        
    def clean(self):
        cleaned_data = super(agregarCarreraForm, self).clean()
        nombre = self.cleaned_data.get('nombre')
        cantidadanios = self.cleaned_data.get('cantidadanios')
        iduniversidad = self.cleaned_data.get('iduniversidad')
        return cleaned_data

class agregarMateriaForm(ModelForm): 

    class Meta:
        model = Materia
        fields = ['nombre', 'aniocarrera','idcarrera']
        
    def clean(self):
        cleaned_data = super(agregarMateriaForm, self).clean()
        nombre = self.cleaned_data.get('nombre')
        aniocarrera = self.cleaned_data.get('aniocarrera')
        idcarrera = self.cleaned_data.get('idcarrera')
        return cleaned_data


