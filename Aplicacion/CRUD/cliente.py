from django.shortcuts import render, redirect
# LLAMAR ARCHIVOS LOCALES
from Aplicacion.forms import *
from Aplicacion.models import *
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, date
from django.utils import timezone
from datetime import timedelta
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TABLAS DE CATALOGOS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# --------------------------------------------------------CLIENTES---------------------------------------------------------


def formulario(request):
    corrales = []
    Nombre = []
    email_v = ''
    ultimo_contacto = tblServido.objects.order_by('-ID').first()
    FechaDeHoy = timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')
    FEProductos = tblProductos.objects.all().exclude(ID=1).order_by('Descripcion')

    ultimo_folio = 0
    idCliente = 0

    email_v = request.session.get('email', None)
    if email_v is not None:
        del request.session['email']
        email = True
    elif request.method == 'POST' and 'email' in request.POST:
        email_v = request.POST.get('email')
        email = True
    else:
        email = False

    if email == True:
        try:
            ultimo_contacto = tblServido.objects.order_by('-ID').first()
            if ultimo_contacto:
                ultimo_folio = ultimo_contacto.ID + 1
            else:
                ultimo_folio = 1

            cliente = tblClientes.objects.get(Email=email_v)
            idCliente = cliente.ID
            Nombre = cliente.Nombre
            corrales = tblCorrales.objects.filter(
                IDCliente_id=idCliente).order_by('Descripcion')

        except ObjectDoesNotExist:
            print("Error")

        # Renderiza la vista con el contexto
    return render(request, 'Publico/form.html', {'corrales': corrales, 'Nombre': Nombre, 'email': email_v,
                                                 'FEProductos': FEProductos, 'ultimo_folio': ultimo_folio, 'FechaDeHoy': FechaDeHoy, 'idCliente': idCliente})


def servidos(request):
    servidos = []
    Nombre = []
    email_v = ''
    idCliente = 0

    email_v = request.session.get('email', None)
    if email_v is not None:
        del request.session['email']
        email = True
    elif request.method == 'POST' and 'email' in request.POST:
        email_v = request.POST.get('email')
        email = True
    else:
        email = False

    if email == True:
        try:
            cliente = tblClientes.objects.get(Email=email_v)
            idCliente = cliente.ID
            Nombre = cliente.Nombre
            servidos = tblServido.objects.filter(IDCliente_id=idCliente).values('Folio', 'IDCliente_id__Nombre', 'IDCorral_id__Descripcion', 'IDProducto_id',
                                                                                'IDProducto_id__Descripcion', 'IDEstatus_id__Descripcion', 'CantidadSolicitada', 'CantidadServida', 'Fecha')
        except ObjectDoesNotExist:
            print("Error")
    return render(request, 'Publico/data.html', {'corrales': servidos, 'Nombre': Nombre, 'email': email_v,
                                                 'idCliente': idCliente})


def cliente(request):
    corrales = []
    Nombre = []
    email_v = ''
    idCliente = 0
    if request.method == 'POST' and 'email' in request.POST:
        email_v = request.POST.get('email')
        try:

            cliente = tblClientes.objects.get(Email=email_v)
            idCliente = cliente.ID
            Nombre = cliente.Nombre
            corrales = tblCorrales.objects.filter(
                IDCliente_id=idCliente).order_by('Descripcion')

            # messages.success(
            #     request, f'El email "{email_v}" se ha encontrado exitosamente')

        except ObjectDoesNotExist:
            messages.error(
                request, f'El email "{email_v}" no se encuentra registrado en Ganadera Valmo, lo sentimos')

        # Renderiza la vista con el contexto
    return render(request, 'Publico/cliente.html', {'corrales': corrales, 'Nombre': Nombre, 'email': email_v,
                                                    'idCliente': idCliente})


def guardarSolicitudServidoCliente(request):
    if request.method == 'POST':
        # Un solo producto seleccionado
        folios = request.POST.getlist('folio')
        productos = request.POST.get('producto')

        # Obtener listas de datos desde el formulario
        clientes = request.POST.getlist('cliente[]')
        corrales = request.POST.getlist('corral[]')
        estatuses = request.POST.getlist('estatus[]')
        prioridades = request.POST.getlist('prioridad[]')
        cantidadesSol = request.POST.getlist('cantidadSol[]')
        cantidadesSer = request.POST.getlist('cantidadSer[]')
        fechasSol = request.POST.getlist('fechaSol[]')
        fechasSer = request.POST.getlist('fechaSer[]')
        peticiones = request.POST.getlist('peticion[]')
        emails = request.POST.getlist('email[]')

        fechaCheck = request.POST.getlist('checkFecha[]')
        if fechaCheck == 'hoy':
            FechaDeHoy = timezone.localtime(timezone.now()).strftime('%Y-%m-%d')
        elif fechaCheck == 'mañana':
            fechaMañana = timezone.localtime(timezone.now()) + timedelta(days=1)
            fechaMañana_str = fechaMañana.strftime('%Y-%m-%d')

        solicitudes = []

        for i in range(len(cantidadesSol)):
            if cantidadesSol[i] and float(cantidadesSol[i]) != 0:
                
                solicitud = {
                    'cliente': clientes[i],
                    'corral': corrales[i],
                    'producto': productos,
                    'estatus': estatuses[i],
                    'cantidadSol': cantidadesSol[i],
                    'cantidadSer': cantidadesSer[i],
                    'prioridad': prioridades[i],
                    'fechaSol': fechasSol[i],
                    'fechaSer': fechasSer[i],
                    'peticion': peticiones[i],
                    'email': emails[i],
                }
                solicitudes.append(solicitud)

      # Obtener el último folio
        if tblServido.objects.exists():
            ultimo_folio_str = tblServido.objects.latest('ID').Folio
            ultimo_folio = int(ultimo_folio_str.split('-')[-1])
        else:
            ultimo_folio = 0

        # Aquí puedes guardar las solicitudes en la base de datos o procesarlas como sea necesario.
        for solicitud in solicitudes:
                # Incrementar el folio
                ultimo_folio += 1
                formatoClave = 'F-{:06d}'.format(ultimo_folio)
                
                tblServido.objects.create(
                Folio=formatoClave,
                IDCliente_id=solicitud['cliente'],
                IDCorral_id=solicitud['corral'],
                IDProducto_id=solicitud['producto'],
                IDEstatus_id=solicitud['estatus'],
                CantidadSolicitada=solicitud['cantidadSol'],
                CantidadServida=solicitud['cantidadSer'],
                Prioridad=solicitud['prioridad'],
                Fecha=solicitud['fechaSol'],
                FechaServida=solicitud['fechaSer']
            )
    peticion = 2

    if request.method == 'POST':

        if peticion == 2:
            email = request.POST['email']
            request.session['email'] = email
            return redirect('FP-Cliente')
    else:
        return redirect('T-Solicitud-Servidos')
