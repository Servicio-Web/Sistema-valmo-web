from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.models import Group
from django.db.models import Count, Sum, Q
from collections import defaultdict
from datetime import datetime, timedelta, date
import time
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.http import HttpResponse
from Aplicacion.CRUD.CopiaDeSeguridad import copiaDeSeguridad
# LLAMAR ARCHIVOS LOCALES
from .forms import *
from .models import *
import logging

# WEBHOOKS
import os

import json
import time

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< FUNCION REGISTRO DE USUARIOS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class CustomLoginView(LoginView):
    template_name = 'Acceso/login.html'
    def form_invalid(self, form):
        messages.error(self.request, 'Usuario o contraseña incorrectos.')
        return super().form_invalid(form)

# ------------------------------------------------------------REGISTRO-------------------------------------------------------------
def Register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_bound:  # Verifica si el formulario está enlazado
            form.full_clean()
            data = form.cleaned_data
            # Realiza tus propias validaciones aquí
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            print(first_name)
            print(last_name)

            # Ejemplo de validaciones personalizadas
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Error: El nombre de usuario "{username}" ya está en uso.')
            elif password1 != password2:
                messages.error(request, 'Error: Las contraseñas no coinciden.')
            elif len(password1) < 8:
                messages.error(request, 'Error: La contraseña debe tener al menos 8 caracteres.')
            else:
                # Si todas las validaciones pasan, guarda el usuario
                user = User.objects.create_user(username=username, password=password1, last_name=last_name, first_name=first_name)
                ultimo_usuario = User.objects.latest('id')
                default_group = Group.objects.get(name='Usuario')
                ultimo_usuario.groups.add(default_group)
                
                messages.success(request, f'El Usuario con el nombre de usuario "{username}" ha sido creado')
                return redirect('Login')

            # Si llega aquí, es porque hubo algún error
            return render(request, 'Acceso/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'Acceso/register.html', context)
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# Create your views here.
@login_required
def grupo_user(request):
    user = request.user
    if user.groups.exists():
        grupo = user.groups.first()
        grupos_user = grupo.name
        grupos = grupos_user
        return grupos
    
def servicioActivo():
    ServiciosWeb = tblServiciosWeb.objects.get(ID=1)
    FechaDeHoy = date.today().strftime('%Y-%m-%d')
    FechaDeHoy = date.today()

    if ServiciosWeb.FechaVencimiento <= FechaDeHoy:
        fecha_vencimiento = datetime.combine(
            ServiciosWeb.FechaVencimiento, datetime.min.time())
        diferencia = FechaDeHoy - fecha_vencimiento.date()
        dias_pasados = diferencia.days
        print(dias_pasados)

        EstadoDePago = False
        save_servicio = tblServiciosWeb.objects.get(ID=1)
        save_servicio.EstadoPago = EstadoDePago
        save_servicio.save()

        if ServiciosWeb.EstadoPago == False and dias_pasados >= 5:
            Servicios = False
            save_servicio = tblServiciosWeb.objects.get(ID=1)
            save_servicio.Servicio = Servicios
            save_servicio.save()
    return ServiciosWeb

def estadoPago(request):
    TServicio = tblServiciosWeb.objects.all()
    ServiciosWeb = tblServiciosWeb.objects.get(ID=1)
    FechaDeHoy = date.today().strftime('%Y-%m-%d')
    FechaDeHoy = date.today()

    if ServiciosWeb.FechaVencimiento <= FechaDeHoy:
        fecha_vencimiento = datetime.combine(
            ServiciosWeb.FechaVencimiento, datetime.min.time())
        diferencia = FechaDeHoy - fecha_vencimiento.date()
        dias_pasados = diferencia.days
        EstadoDePago = False
        save_servicio = tblServiciosWeb.objects.get(ID=1)
        save_servicio.EstadoPago = EstadoDePago
        save_servicio.save()
        dias_restantes = 5-dias_pasados


        if ServiciosWeb.EstadoPago == False and dias_pasados >= 5:
            Servicios = False
            save_servicio = tblServiciosWeb.objects.get(ID=1)
            save_servicio.Servicio = Servicios
            save_servicio.save()
    else:
        fecha_vencimiento = datetime.combine(
            ServiciosWeb.FechaVencimiento, datetime.min.time())
        diferenciaVencer = fecha_vencimiento.date() - FechaDeHoy
        dias_faltantes = diferenciaVencer.days
        dias_restantes = dias_faltantes
    return render(request, 'Configuracion/pagos/index.html', {'ServiciosWeb': ServiciosWeb, 'dias_restantes': dias_restantes, 'TServicio': TServicio})


def registrarPago(request):
    id = 1
    save_pago = tblServiciosWeb.objects.get(ID=id)
    fechaVencimiento = save_pago.FechaVencimiento

    if 'aplazar' in request.POST:
        ServicioActivo = True
        PagoActivo = True
        fechaFinal = fechaVencimiento + relativedelta(months=1)
        messages.success(request, f'El pago se ha autorizado correctamente')
    elif 'cancelar'in request.POST:
        ServicioActivo = False
        PagoActivo = False
        fechaFinal = date.today().strftime('%Y-%m-%d')
        messages.error(request, f'El servicio se ha cancelado')

    # Obtener la fecha de vencimiento actual y agregar 30 días
    fechaActualizada = fechaFinal
    save_pago.Servicio = ServicioActivo 
    save_pago.EstadoPago = PagoActivo
    save_pago.FechaVencimiento = fechaActualizada
    save_pago.save()

    return redirect('Pagos')

def notificacion(request):
    id = 1
    if 'Activar' in request.POST:
        Notificacion = False
        activar = tblServiciosWeb.objects.get(ID=id)
        activar.Notificacion = Notificacion
        activar.save()
        messages.success(request, f'Se han activado las notificaciones')
        return redirect('Pagos')
    elif 'Desactivar' in request.POST:
        Notificacion = True
        activar = tblServiciosWeb.objects.get(ID=id)
        activar.Notificacion = Notificacion
        activar.save()
        messages.success(request, f'Se han desactivado las notificaciones')
        return redirect('Pagos')

def NoPago(request):
    ServiciosWeb = servicioActivo()
    return render(request, 'Configuracion/pagos/Nopago.html',{'ServiciosWeb': ServiciosWeb})

def usuarioBloqueado(request):
    ServiciosWeb = servicioActivo()
    return render(request, 'Configuracion/Bloqueados/index.html',{'ServiciosWeb': ServiciosWeb})


def home(request):
    grupos = grupo_user(request)
    try:
        group = Group.objects.get(name='Usuario')
    except Group.DoesNotExist:
            # tecnicos
        Tecnico_v = "No registrado"
        NombreTabla_v = 'Grupo'
        IDFilaTabla_v = "Vacio"
        AreaRegistro_v = 'Configuración'
        IDFila_v = 1
        agregarDatosTecnicos(request, Tecnico_v, NombreTabla_v, IDFilaTabla_v, AreaRegistro_v, IDFila_v)
        group = Group.objects.create(name='Usuario')
    except Exception as e:
        Error = "Error al iniciar servicio"

    try:
        # Verifica si el servicio ya existe
        servicio = tblServiciosWeb.objects.get(ID=1)
    except tblServiciosWeb.DoesNotExist:
        # Si el servicio no existe, créalo
        FechaDeHoy = date.today().strftime('%Y-%m-%d')
        tblServiciosWeb.objects.create(
            Servicio=1, EstadoPago=1, Notificacion=0, FechaVencimiento=FechaDeHoy)       
    except Exception as e:
        Error = "Error al iniciar servicio"
    
    try:
        # Verifica si el servicio ya existe
        configuracion = tblConfiguracion.objects.get(ID=1)
    except tblConfiguracion.DoesNotExist:
        # Si el servicio no existe, créalo
        FechaDescarga_v = timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')
        FechaActualizacion_v = timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')
        tblConfiguracion.objects.create(
            Usuario='Sin resultado', BaseDeDatos='Sin movimientos', FechaDescarga=FechaDescarga_v, FechaActualizacion=FechaActualizacion_v)       
    except Exception as e:
        Error = "Error al iniciar servicio"
    return render(request, 'Publico/index.html', {'grupos': grupos})

def sistema(request):
    grupos = grupo_user(request)    
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< corrales liberador y ocupados >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    corralesLiberados = tblCorrales.objects.filter(IDCliente_id = 1).count()
    corralesAsignados = tblCorrales.objects.exclude(IDCliente_id = 1).count()
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Grafica de cantidad de corrales por clientes >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    corrales = (tblCorrales.objects.values('IDCliente__Nombre').annotate(total=Count('ID')).filter(total__gt=5).exclude(IDCliente=1).order_by('-total'))
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Tolvas cargadas >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    tolvas = tblTolva.objects.values('ID', 'Capacidad', 'Alias').exclude(ID = 1)
    servido_por_tolva = (tblServido.objects.filter(IDEstatus_id=8).values('IDTolva').annotate(total=Sum('CantidadSolicitada')).exclude(IDTolva = 1))
    servido_dict = {item['IDTolva']: item['total'] for item in servido_por_tolva}
    datos_tolvas = []
    for tolva in tolvas:
        id_tolva = tolva['ID']
        capacidad = tolva['Capacidad']
        alias = tolva['Alias']
        cantidad = servido_dict.get(id_tolva, 0)
        porcentaje = round((cantidad / capacidad) * 100, 2) if capacidad > 0 else 0
        datos_tolvas.append({
            'alias': alias,
            'capacidad': capacidad,
            'cantidad': cantidad,
            'porcentaje': porcentaje
        })
 

    labels = [c['IDCliente__Nombre'] for c in corrales]
    data = [c['total'] for c in corrales]

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Conteo de animales >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Traer todos los tipos de animales
    animales_tipo = tblAnimalesTipo.objects.all()

    # Traer todos los detalles de movimientos
    detalle_mov = tblDetalleMovAnimales.objects.values('IDFolio', 'IDAnimales', 'Cantidad')

    # Traer todos los movimientos con su tipo
    movimientos = tblMovimientoAnimales.objects.values('Folio', 'IDMovimiento')

    # Convertir movimientos a un diccionario para fácil acceso
    mov_dict = {m['Folio']: m['IDMovimiento'] for m in movimientos}

    # Calcular conteo por tipo
    conteo_animales = defaultdict(int)

    for d in detalle_mov:
        folio = d['IDFolio']
        tipo = mov_dict.get(folio)
        cantidad = d['Cantidad']
        animal_id = d['IDAnimales']
        if tipo == 1:  # Entrada
            conteo_animales[animal_id] += cantidad
        elif tipo == 2:  # Salida
            conteo_animales[animal_id] -= cantidad

    # Crear lista de resultados con nombre
    resultado_final = []
    for animal in animales_tipo:
        resultado_final.append({
            'nombre': animal.Descripcion,
            'cantidad': conteo_animales.get(animal.ID, 0)
        })
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Conteo de servidos >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    PServidosRegistros = tblServido.objects.all()
    registros = PServidosRegistros.count()
    
    PServidosPendientes = tblServido.objects.filter(Q(IDEstatus_id = 3) | Q(IDEstatus_id=9)).all()
    pendientes = PServidosPendientes.count()

    PServidosManual = tblServido.objects.filter(IDEstatus_id = 7).all()
    manuales = PServidosManual.count()

    PServidosConsolidacion = tblServido.objects.filter(IDEstatus_id= 8).all()
    tolva = PServidosConsolidacion.count()
    
    PServidosConsolidacion = tblServido.objects.filter(Q(IDEstatus_id =  10) | Q(IDEstatus_id = 11)).all()
    servidos = PServidosConsolidacion.count()    
    
    # USUARIOS
    usuarios_con_grupo = []
    TUsuarios = User.objects.all().exclude(username="admin@gmail.com")

    for usuario in TUsuarios:
        is_authenticated = usuario.is_authenticated
        grupos = usuario.groups.exclude(name='Bloqueado')
        usuarios_con_grupo.append({'usuario': usuario, 'is_authenticated': is_authenticated, 'grupos': grupos})
    
    ServiciosWeb = servicioActivo()

    
    # CONFIGURACION
    TConfiguracion = tblConfiguracion.objects.all()
    print(TConfiguracion)
    return render(request, 'include/index.html', { 'grupos': grupos, 'data': json.dumps(data), 'labels': json.dumps(labels), 
    'datos_tolvas':datos_tolvas, 'corralesLiberados': corralesLiberados, 'corralesAsignados':corralesAsignados, 'resultado_animales': resultado_final,
    'manuales':manuales, 'registros':registros, 'pendientes':pendientes, 'servidos':servidos, 'tolva':tolva, 'usuarios_con_grupo': usuarios_con_grupo  ,
    'ServiciosWeb': ServiciosWeb, 'TConfiguracion':TConfiguracion
    })  


def reportes(request):
    grupos = grupo_user(request)
    return render(request, 'Reportes/index.html', {'grupos': grupos})

def perfil(request):
    grupos = grupo_user(request)
    user = request.user 
    full_name = user.first_name + " " + user.last_name
    FTecnicosTablaCatalogos = tblTecnicos.objects.filter(Tecnico__icontains = full_name, AreaRegistro = 'Catalogos').values('NombreTabla').distinct().order_by('NombreTabla')
    FTecnicosTablaProcesos = tblTecnicos.objects.filter(Tecnico__icontains = full_name, AreaRegistro = 'Procesos').values('NombreTabla').distinct().order_by('NombreTabla')
    FTecnicosTablaSubTablas = tblTecnicos.objects.filter(Tecnico__icontains = full_name, AreaRegistro = 'Subtabla').values('NombreTabla').distinct().order_by('NombreTabla')
    ServiciosWeb = servicioActivo()
    
    if request.method == 'POST':
        TablaCatalogos = request.POST.get('tabla1')
        TablaProcesos = request.POST.get('tabla2')
        TablaSubtabla = request.POST.get('tabla3')

        if 'tabla1' in request.POST:
            TablaProcesos = "Buscar..."
            TablaSubtabla = "Buscar..."
            TablaSel = "Catálogos - " + TablaCatalogos
            TTecnicos = tblTecnicos.objects.filter(Tecnico__icontains=full_name, NombreTabla = TablaCatalogos)
            return render(request, 'Configuracion/perfil/index.html', {'grupos': grupos, 'TTecnicos':TTecnicos, 'ServiciosWeb': ServiciosWeb,
            'FTecnicosTablaCatalogos':FTecnicosTablaCatalogos, 'FTecnicosTablaProcesos':FTecnicosTablaProcesos, 'FTecnicosTablaSubTablas':FTecnicosTablaSubTablas,
            'TablaCatalogos':TablaCatalogos, 'TablaProcesos':TablaProcesos, 'TablaSubtabla':TablaSubtabla,
            'tablaseleccionada':TablaSel
            })
        if 'tabla2' in request.POST:
            TablaCatalogos = "Buscar..."
            TablaSubtabla = "Buscar..."
            TablaSel = "Procesos - " + TablaProcesos
            TTecnicos = tblTecnicos.objects.filter(Tecnico__icontains=full_name, NombreTabla = TablaProcesos)
            return render(request, 'Configuracion/perfil/index.html', {'grupos': grupos, 'TTecnicos':TTecnicos, 'ServiciosWeb': ServiciosWeb,
            'FTecnicosTablaCatalogos':FTecnicosTablaCatalogos, 'FTecnicosTablaProcesos':FTecnicosTablaProcesos,'FTecnicosTablaSubTablas':FTecnicosTablaSubTablas,
            'TablaCatalogos':TablaCatalogos, 'TablaProcesos':TablaProcesos, 'TablaSubtabla':TablaSubtabla,
            'tablaseleccionada':TablaSel
             })
        if 'tabla3' in request.POST:
            TablaCatalogos = "Buscar..."
            TablaProcesos = "Buscar..."
            TablaSel = "Subtablas - " + TablaSubtabla
            TTecnicos = tblTecnicos.objects.filter(Tecnico__icontains=full_name, NombreTabla = TablaSubtabla)
            return render(request, 'Configuracion/perfil/index.html', {'grupos': grupos, 'TTecnicos':TTecnicos, 'ServiciosWeb': ServiciosWeb,
            'FTecnicosTablaCatalogos':FTecnicosTablaCatalogos, 'FTecnicosTablaProcesos':FTecnicosTablaProcesos, 'FTecnicosTablaSubTablas':FTecnicosTablaSubTablas,
            'TablaCatalogos':TablaCatalogos, 'TablaProcesos':TablaProcesos, 'TablaSubtabla':TablaSubtabla,
            'tablaseleccionada':TablaSel
            })
    else:
        TablaCatalogos = "Buscar..."
        TablaProcesos = "Buscar..."
        TablaSubtabla = "Buscar..."
        TTecnicos = tblTecnicos.objects.filter(Tecnico='').all
        return render(request, 'Configuracion/perfil/index.html', {'grupos': grupos, 'TTecnicos':TTecnicos, 'ServiciosWeb': ServiciosWeb,
        'FTecnicosTablaCatalogos':FTecnicosTablaCatalogos, 'FTecnicosTablaProcesos':FTecnicosTablaProcesos, 'FTecnicosTablaSubTablas':FTecnicosTablaSubTablas,
        'TablaCatalogos':TablaCatalogos, 'TablaProcesos':TablaProcesos, 'TablaSubtabla':TablaSubtabla,
        'tablaseleccionada':TablaCatalogos,'tablaseleccionada':TablaProcesos,'tablaseleccionada':TablaSubtabla
        })
    
def agregarDatosTecnicos(request, Tecnico_v, NombreTabla_v, IDFilaTabla_v, AreaRegistro_v, IDFila_v):
    try:
        Acciones_v = 'Agregado'
        Fecha_v  = timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')
        
        tblTecnicos.objects.create(
            Tecnico = Tecnico_v, NombreTabla = NombreTabla_v, IDFilaTabla = IDFilaTabla_v, 
            Acciones = Acciones_v, Fecha = Fecha_v, AreaRegistro = AreaRegistro_v, IDFila = IDFila_v
        )
    except Exception as e:
        print("Error ", e)
        
def editarDatosTecnicos(request, TecnicoEditor_v, NombreTabla_v, IDFilaTabla_v):
    try:
        Acciones_v = 'Editado'
        FechaEditor_v   = timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')
        
        tecnicos_editor = tblTecnicos.objects.get(IDFila=IDFilaTabla_v, NombreTabla=NombreTabla_v)
        tecnicos_editor.TecnicoEditor = TecnicoEditor_v
        tecnicos_editor.FechaActualizado = FechaEditor_v
        tecnicos_editor.AccionesEditado = Acciones_v
        tecnicos_editor.save()
    except Exception as e:
        print("Error ", e)
        

def agregarTecnicos(request):
    grupos = grupo_user(request)
    ServiciosWeb = servicioActivo()
    if request.method == 'POST':
        usuario_v = request.POST.get('usuario')
        full_name = request.POST.get('full_name')

        usuario = User.objects.get(id=usuario_v)
        catalogosUL = tblTecnicos.objects.filter(Tecnico__icontains = full_name, AreaRegistro = 'Catalogos', Acciones = 'Agregado').values('NombreTabla').distinct().order_by('NombreTabla')
        procesosUL = tblTecnicos.objects.filter(Tecnico__icontains = full_name, AreaRegistro = 'Procesos', Acciones = 'Agregado').values('NombreTabla').distinct().order_by('NombreTabla')
        subtablaUL = tblTecnicos.objects.filter(Tecnico__icontains = full_name, AreaRegistro = 'Subtabla', Acciones = 'Agregado').values('NombreTabla').distinct().order_by('NombreTabla')
        
        if 'tabla' in request.POST:
            tabla_v = request.POST.get('tabla')
            contenidoTabla = tblTecnicos.objects.filter(Tecnico__icontains = full_name, NombreTabla = tabla_v, Acciones = 'Agregado') 
            return render(request, "Configuracion/Tecnicos/Agregados.html", {'grupos': grupos, 'catalogosUL': catalogosUL, 'ServiciosWeb': ServiciosWeb,
            'procesosUL':procesosUL,'subtablaUL':subtablaUL,'tabla_v':tabla_v, 'usuario':usuario, 'contenidoTabla':contenidoTabla})
        else:
            tabla_v = "No se ha seleccionado ninguna tabla"
            return render(request, "Configuracion/Tecnicos/Agregados.html", {'grupos': grupos, 'catalogosUL': catalogosUL, 'ServiciosWeb': ServiciosWeb,
            'procesosUL':procesosUL,'subtablaUL':subtablaUL,'tabla_v':tabla_v, 'usuario':usuario})

def editadoTecnicos(request):
    grupos = grupo_user(request)
    ServiciosWeb = servicioActivo()
    
    if request.method == 'POST':
        usuario_v = request.POST.get('usuario')
        full_name = request.POST.get('full_name')

        usuario = User.objects.get(id=usuario_v)
        catalogosUL = tblTecnicos.objects.filter(Tecnico__icontains = full_name, AreaRegistro = 'Catalogos', AccionesEditado = 'Editado').values('NombreTabla').distinct().order_by('NombreTabla')
        procesosUL = tblTecnicos.objects.filter(Tecnico__icontains = full_name, AreaRegistro = 'Procesos', AccionesEditado = 'Editado').values('NombreTabla').distinct().order_by('NombreTabla')
        subtablaUL = tblTecnicos.objects.filter(Tecnico__icontains = full_name, AreaRegistro = 'Subtabla', AccionesEditado = 'Editado').values('NombreTabla').distinct().order_by('NombreTabla')

        if 'tabla' in request.POST:
            tabla_v = request.POST.get('tabla')
            contenidoTabla = tblTecnicos.objects.filter(Tecnico__icontains = full_name, NombreTabla = tabla_v, AccionesEditado = 'Editado') 
            return render(request, "Configuracion/Tecnicos/Editados.html", {'grupos': grupos,'catalogosUL': catalogosUL, 'ServiciosWeb': ServiciosWeb,
            'procesosUL':procesosUL, 'subtablaUL':subtablaUL,'tabla_v':tabla_v, 'usuario':usuario, 'contenidoTabla':contenidoTabla})
        else:
            tabla_v = "No se ha seleccionado ninguna tabla"
            return render(request, "Configuracion/Tecnicos/Editados.html", {'grupos': grupos, 'catalogosUL': catalogosUL, 'ServiciosWeb': ServiciosWeb,
            'procesosUL':procesosUL, 'subtablaUL':subtablaUL,'tabla_v':tabla_v, 'usuario':usuario})
        
# ---------------------------------------------------CONSULTA PARA LAS TABLAS DE USUARIOS---------------------------------------------------

def TablaUsuarios(request):
    usuarios_con_grupo = []
    TUsuarios = User.objects.all()

    for usuario in TUsuarios:
        is_authenticated = usuario.is_authenticated
        grupos = usuario.groups.exclude(name='Bloqueado')
        usuarios_con_grupo.append(
            {'usuario': usuario, 'is_authenticated': is_authenticated, 'grupos': grupos})
    ServiciosWeb = servicioActivo()
    return render(request, 'Configuracion/Tecnicos/index.html', {'ServiciosWeb': ServiciosWeb,
    'usuarios_con_grupo': usuarios_con_grupo})


def edicionUsuario(request, id):
    TEUser = User.objects.get(id=id)
    grupos = TEUser.groups.all()
    grupos_restantes = Group.objects.exclude(user=TEUser)
    ServiciosWeb = servicioActivo()
    return render(request, "Configuracion/Tecnicos/edit.html", {'ServiciosWeb': ServiciosWeb, 'TEUser': TEUser, 'grupos': grupos, 'grupos_restantes': grupos_restantes})

def actualizarUsuario(request):
    id = request.POST['id']
    nombre = request.POST['nombre'].title().strip()
    apellido = request.POST['apellido'].title().strip()
    roles = request.POST['roles']
    email = request.POST['email']

    # En esta variable depéndera al template al que se redireccionara
    vista = request.POST['vista']
    
    email_existente = User.objects.exclude(
        id=id).filter(username=email).exists()
    if email_existente:
        messages.error(
            request, f'El email "{email}" ya ha sido registrado anteriormente.')
    else:
        if 'bloqueado' in request.POST:
            roles = 'Bloqueado'
            usuario = User.objects.get(id=id)
            default_group = Group.objects.get(name=roles)
            usuario.groups.clear()
            usuario.groups.add(default_group)
            usuario.save()
        else:
            usuario = User.objects.get(id=id)
            default_group = Group.objects.get(name=roles)
            usuario.groups.clear()
            usuario.groups.add(default_group)
            usuario.first_name = nombre
            usuario.last_name = apellido
            usuario.username = email
            usuario.save()
            messages.success(
                request, f'El usuario "{email}" se ha actualizado exitosamente.')
    if vista == '1':
        return redirect('perfil')
    elif vista == '2':
        return redirect('TUsuarios')
    elif vista == '3':
        return redirect('TUsuarios')
    return redirect('TUsuarios')

# ---------------------------------------------------CONSULTA PARA LAS TABLAS DE GRUPOS---------------------------------------------------
def FormularioGrupos(request):
    grupos = grupo_user(request)
    ultimo_id = Group.objects.order_by('-id').first()
    if ultimo_id:
        ultimo_folio = ultimo_id.id + 1
    else:
        ultimo_folio = 1
    ServiciosWeb = servicioActivo()
    return render(request, 'Configuracion/Grupos/form.html',{'grupos': grupos,'ServiciosWeb': ServiciosWeb,
    'ultimo_folio': ultimo_folio})
    
def agregarGrupos(request):
    id = request.POST['id']
    descripcion_v = request.POST['descripcion'].title()

    # tecnicos
    Tecnico_v = request.POST['tecnico'].title()
    NombreTabla_v = 'Grupo'
    IDFilaTabla_v = "Vacio"
    AreaRegistro_v = 'Configuración'
    IDFila_v = id

    existente = Group.objects.filter(name=descripcion_v).exists()
    if existente:
        errorCol = 'error'
        messages.error(request, f'El Grupo {descripcion_v} ya ha sido registrado antreriormente')
        columnas = {'ultimo_folio': id, 'errorCol':errorCol}
        return render(request, "Configuracion/Grupos/form.html", columnas)
    else:
        Group.objects.create( name = descripcion_v )
        agregarDatosTecnicos(request, Tecnico_v, NombreTabla_v, IDFilaTabla_v, AreaRegistro_v, IDFila_v)
        messages.success(request, f'El Grupo {descripcion_v} se ha registrado exitosamente')

    if request.method == 'POST':
        if 'salir' in request.POST:
            return redirect('T-Grupos')
        elif 'agregar' in request.POST:
            return redirect('F-Grupos')
    else:
        return redirect('T-Grupos')
    
def TablaGrupos(request):
    grupos = grupo_user(request)
    ultimo_id = Group.objects.order_by('-id').first()
    if ultimo_id:
        ultimo_folio = ultimo_id.id + 1
    else:
        ultimo_folio = 1
    TGrupos = Group.objects.all()
    ServiciosWeb = servicioActivo()
    return render(request, 'Configuracion/Grupos/index.html',{'grupos': grupos,
    'ServiciosWeb': ServiciosWeb,'TGrupos': TGrupos, 'ultimo_folio':ultimo_folio})

def editarGrupos(request, ID):
    grupos = grupo_user(request)
    TEGrupos = Group.objects.get(id=ID)
    return render(request, "Configuracion/Grupos/edit.html",{'grupos': grupos,'TEGrupos': TEGrupos})

def actualizarGrupo(request):
    id = request.POST['id']
    descripcion_v = request.POST['descripcion'].title()

   # tecnicos
    TecnicoEditor_v = request.POST['tecnico'].title()
    NombreTabla_v = 'Grupo'
    IDFilaTabla_v = id

    nombre_existente = Group.objects.filter(name=descripcion_v).exclude(id=id).exists()
    if nombre_existente:
        messages.error(request, f'El Grupo "{descripcion_v}" ya ha sido registrado anteriormente.')
    else:
        grupo = Group.objects.get(id=id)
        grupo.name = descripcion_v
        grupo.save()
        editarDatosTecnicos(request, TecnicoEditor_v, NombreTabla_v, IDFilaTabla_v)
        messages.success(request, f'El Grupo "{descripcion_v}" se ha actualizado exitosamente.')
    return redirect('T-Grupos')

def TablaPermisos(request):
    grupos = grupo_user(request)
    TPermisos = Permission.objects.exclude(name__icontains = 'Restringido')
    ServiciosWeb = servicioActivo()
    return render(request, 'Configuracion/Permisos/permisos.html',{'grupos': grupos,
    'ServiciosWeb': ServiciosWeb,'TPermisos': TPermisos})

def TablaTiposDeRol(request):
    grupos = grupo_user(request)
    usuario = request.user
    grupos_usuario = usuario.groups.all()

    for grupo in grupos_usuario:
        TPermisos = grupo.permissions.all()
        

    ServiciosWeb = servicioActivo()
    return render(request, 'Configuracion/perfil/TiposRol.html',{'grupos': grupos,
    'ServiciosWeb': ServiciosWeb,'TPermisos': TPermisos})

def TablaPermisosAsignaElimina(request):
    grupos = grupo_user(request)
    ServiciosWeb = servicioActivo()
    FGrupos = Group.objects.all()
    GrupoID = request.POST.get('grupo', '')
    if GrupoID is not None and GrupoID != '':
        Grupo_Select = Group.objects.get(id=GrupoID)
        grupoPost = [{'id': Grupo_Select.id, 'name': Grupo_Select.name}]
    else:
        grupoPost = [{'id': ''}]

    if GrupoID is not None and GrupoID != '':
        grupo = Group.objects.get(id=GrupoID)
        TPermisosAsignados = grupo.permissions.all()
        TPermisosLibres = Permission.objects.exclude(id__in=TPermisosAsignados.values_list('id', flat=True))
    else:
        TPermisosLibres = Permission.objects.all()
        TPermisosAsignados = Group.objects.all()

    asignar = request.POST.get('asignar', '')
    if asignar is not None and asignar != '':
        grupo = request.POST['grupo']
        permiso = request.POST['permiso']
        grupoPost = [{'id': Grupo_Select.id, 'name': Grupo_Select.name}]

        # # Obtener el grupo y el permiso
        # grupo = Group.objects.get(id=grupo)
        # permiso = Permission.objects.get(id=idpermiso)

        # # Agregar el permiso al grupo
        # grupo.permissions.add(permiso)

        grupo_id = request.POST['grupo']
        grupo = Group.objects.get(id=grupo_id)
        
        permisos_seleccionados = request.POST.getlist('permisos_seleccionados')
        for permiso_id in permisos_seleccionados:
            permiso = Permission.objects.get(id=permiso_id)
            grupo.permissions.add(permiso)
            
        messages.success(request, f'Permisos asignados exitosamente')

        return render(request, 'Configuracion/Permisos/index.html',{'grupos': grupos,
        'grupos': grupos, 'ServiciosWeb':ServiciosWeb, 
        'TPermisosLibres': TPermisosLibres, 'TPermisosAsignados':TPermisosAsignados,
        'FGrupos':FGrupos, 'grupoPost': grupoPost})
    
    liberar = request.POST.get('liberar', '')
    if liberar is not None and liberar != '':
        grupo = request.POST['grupo']
        permiso = request.POST['permiso']
        grupoPost = [{'id': Grupo_Select.id, 'name': Grupo_Select.name}]

        # # Obtener el grupo y el permiso
        # grupo = Group.objects.get(id=grupo)
        # permiso = Permission.objects.get(id=idpermiso)

        # # Agregar el permiso al grupo
        # grupo.permissions.remove(permiso)

        grupo_id = request.POST['grupo']
        grupo = Group.objects.get(id=grupo_id)
        
        permisos_seleccionados = request.POST.getlist('permisos_seleccionados')
        for permiso_id in permisos_seleccionados:
            permiso = Permission.objects.get(id=permiso_id)
            grupo.permissions.remove(permiso)
            
        messages.success(request, f'Permisos eliminados exitosamente')

        return render(request, 'Configuracion/Permisos/index.html',{'grupos': grupos,
        'grupos': grupos, 'ServiciosWeb':ServiciosWeb, 
        'TPermisosLibres': TPermisosLibres, 'TPermisosAsignados':TPermisosAsignados,
        'FGrupos':FGrupos, 'grupoPost': grupoPost})
    
    return render(request, 'Configuracion/Permisos/index.html',{'grupos': grupos, 'ServiciosWeb':ServiciosWeb, 
    'TPermisosLibres': TPermisosLibres, 'TPermisosAsignados':TPermisosAsignados, 'FGrupos':FGrupos, 'grupoPost': grupoPost})

def editarPermisos(request, ID):
    grupos = grupo_user(request)
    TEPermisos = Permission.objects.get(id=ID)
    return render(request, "Configuracion/Permisos/edit.html",{'grupos': grupos,'TEPermisos': TEPermisos })

def actualizarPermiso(request):
    id = request.POST['id']
    descripcion_v = request.POST['descripcion'].title()

    nombre_existente = Permission.objects.filter(name=descripcion_v).exclude(id=id).exists()
    if nombre_existente:
        messages.error(request, f'El permiso "{descripcion_v}" ya ha sido registrado anteriormente.')
    else:
        permiso = Permission.objects.get(id=id)
        permiso.name = descripcion_v
        permiso.save()
        messages.success(request, f'El Grupo "{descripcion_v}" se ha actualizado exitosamente.')
    return redirect('T-Permisos')