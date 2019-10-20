from django.contrib import admin
from django.contrib.admin.models import LogEntry,DELETION
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import Sesion,Paquete_Inscrito,Alumno,Tipo_de_Paquete
from datetime import timedelta
from admin_auto_filters.filters import AutocompleteFilter
from import_export.admin import ImportExportModelAdmin
from import_export import resources
import  import_export

# Register your models here

class SesionAdmin(admin.ModelAdmin):
    #resource_class = SesionResource
    list_display =('paquete_inscrito_','tiempo_de_inicio','tiempo_de_salida','tiempo_de_sesion',)
    list_filter = [('paquete_inscrito',admin.RelatedFieldListFilter)]
    search_fields=('paquete_inscrito__alumno__nombre','paquete_inscrito__alumno__apellido')
    list_per_page=15

    def paquete_inscrito_(self,instance):
        return instance.paquete_inscrito

class PaquetesInscritosInline(admin.TabularInline):
    model = Paquete_Inscrito
    extra=0

class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('apellido','nombre','nivel_academico',)
    list_filter = ('nombre','apellido')
    search_fields=('nombre', 'apellido',)
    inlines = [PaquetesInscritosInline]
    list_per_page=15


class Paquete_inscritoResource(resources.ModelResource):
     #horas_consumidas = import_export.fields(attribute="_horas_consumidas", column_name="Horas consumidas")
     #alumno = import_export.Field(column_name='alumno',attribute='alumno', widget=ForeignKeyWidget(Alumno, 'Alumno'))
     #tipo_de_paquete = import_export.Field(column_name='tipo_de_paquete',attribute='tipo_de_paquete', widget=ForeignKeyWidget(Tipo_de_Paquete, 'Tipo_de_Paquete'))

     class Meta:
         model = Paquete_Inscrito
         report_skipped = True
         fields = ('alumno__nombre','alumno__apellido','fecha_de_inscripcion','tipo_de_paquete__horas','horas_consumidas','status')
         export_order = fields


class SesionesInline(admin.TabularInline):
    model= Sesion
    extra=0

class Paquete_InscritoAdmin(ImportExportModelAdmin):
    resource_class = Paquete_inscritoResource
    list_display = ('alumno_name','fecha_de_inscripcion','tipo_de_paquete_','_horas_consumidas','status',)
    list_filter=('status',)
    #list_filter = [('alumno',admin.RelatedFieldListFilter,)]
    search_fields = ('alumno__nombre','alumno__apellido',)
    inlines = [SesionesInline]
    list_per_page=15

    def _horas_consumidas(self,obj):
        return self.calc_hours(obj)

    def calc_hours(self,obj):
        horas = timedelta(days=0,hours=0,minutes=0)
        for tiempo in obj.clases.all():
            if tiempo.tiempo_de_sesion == None:
                return None
            else:
                horas+= tiempo.tiempo_de_sesion
        obj.horas_consumidas = horas
        obj.save()
        limite = obj.tipo_de_paquete.horas
        if horas >= timedelta(days=0,hours=limite,minutes=0):
            obj.status = False
            obj.save()
        else:
            obj.status = True
            obj.save()
        return f'{horas} Horas'

    def alumno_name(self,instance):
        return instance.alumno
    def tipo_de_paquete_(self,instance):
        return instance.tipo_de_paquete


class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'
    readonly_fields = ('action_time',)
    list_filter = ['user']
    search_fields = ['object_repr', 'change_message']
    list_display = ['__str__', 'content_type', 'action_time', 'user', 'object_link']

    # keep only view permission
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = obj.object_repr
        else:
            ct = obj.content_type
            try:
                link = mark_safe('<a href="%s">%s</a>' % (
                                 reverse('admin:%s_%s_change' % (ct.app_label, ct.model),
                                         args=[obj.object_id]),
                                 escape(obj.object_repr),
                ))
            except NoReverseMatch:
                link = obj.object_repr
        return link
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = 'instancia_modificada'
'''
    def queryset(self, request):
        return super(LogEntryAdmin, self).queryset(request) \
            .prefetch_related('content_type')
'''
admin.site.register(Alumno,AlumnoAdmin)
admin.site.register(Sesion,SesionAdmin)
admin.site.register(Paquete_Inscrito,Paquete_InscritoAdmin)
admin.site.register(Tipo_de_Paquete)
admin.site.register(LogEntry,LogEntryAdmin)
