from django.db import models
import uuid
import datetime
 # name of the foreign key field

class Sesion(models.Model):
    paquete_inscrito = models.ForeignKey('Paquete_Inscrito',related_name="clases",on_delete=models.CASCADE,null=True)
    asignatura = models.CharField(max_length=100)
    tiempo_de_inicio = models.DateTimeField(null=True,blank=True)
    tiempo_de_salida = models.DateTimeField(null=True,blank=True)
    observaciones = models.CharField(max_length=200,null=True,blank=True)


    def _get_tiempo_de_sesion(self):
        if self.tiempo_de_salida == None:
            return None
        return self.tiempo_de_salida - self.tiempo_de_inicio

    tiempo_de_sesion = property(_get_tiempo_de_sesion)

    class Meta:
        verbose_name = ("Sesion")
        verbose_name_plural = ("Sesiones")
        ordering = ['-tiempo_de_inicio']
    def __str__(self):
        return f'{self.asignatura}: duración: { self.tiempo_de_sesion}'


class Tipo_de_Paquete(models.Model):
    horas = models.IntegerField(default=1)


    class Meta:
        verbose_name = ("Tipo de Paquete")
        verbose_name_plural = ("Tipos de Paquetes")

    def __str__(self):
        return f'{self.horas} Horas'


class Alumno(models.Model):
    nombre =  models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    NIVEL_STATUS = (
         ('k','Kinder'),
         ('p','Primaria'),
         ('s','Secundaria'),
         ('b','bachillerato'),
         ('u','universidad'))
    nivel_academico = models.CharField(max_length=1,choices=NIVEL_STATUS,blank=True,help_text='Elige el nivel académico del alumno')

    def __str__(self):
        return f'{self.nombre} { self.apellido}'

class Paquete_Inscrito(models.Model):
     id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="id del Paquete")
     #related_name='_clases_concluidas'
     alumno = models.ForeignKey('Alumno',on_delete=models.CASCADE,null=True)
     fecha_de_inscripcion = models.DateField(null=True,blank=True)
     horas_consumidas = models.DurationField(default=datetime.timedelta(days=0,hours=0,minutes=0))
     ESTADO_STATUS =(
     (True,'Activo'),
     (False,'Finalizado')
     )

     tipo_de_paquete = models.ForeignKey('Tipo_de_Paquete', on_delete=models.SET_NULL, null=True,help_text='Elige el tipo de paquete del alumno')
     #sesiones = models.ForeignKey('Sesion',on_delete=models.SET_NULL,null=True)
     status = models.BooleanField(default=True,choices=ESTADO_STATUS,blank=True,help_text="Elige el estado del paquete")

     class Meta:
         verbose_name = ("Paquete Inscrito")
         verbose_name_plural = ("Paquetes Inscritos")
         ordering = ['alumno__nombre']


     def __str__(self):
         if self.status == True:
             return f'{self.alumno} | Status: Activo'
         else:
            return f'{self.alumno} | Status: Finalizado'
