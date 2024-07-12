from django.template.loader import render_to_string
from io import BytesIO
from xhtml2pdf import pisa
from django.templatetags.static import static
from datetime import datetime, timedelta, date
from Aplicacion.forms import *
from Aplicacion.models import *
from django.http import HttpResponse

# -----------------------------------------------------------INCREMENTADOR DE FOLIOS POR PDF-----------------------------------------------------------
def cargar_folio(valor):
    Folio = tblConfiguracion.objects.get(ID = 1)
    if valor == 1:
        GFolio = Folio.FolioSalMaquila
        clave_int = int(GFolio[2:])
        clave_int += 1  
        formatoClave = 'F-{:06d}'.format(clave_int)
        Folio.FolioSalMaquila = formatoClave
    elif valor == 2:
        GFolio = Folio.FolioEntProducto
        clave_int = int(GFolio[2:])
        clave_int += 1  
        formatoClave = 'F-{:06d}'.format(clave_int)
        Folio.FolioEntProducto = formatoClave
    elif valor == 3:
        GFolio = Folio.FolioSalProducto
        clave_int = int(GFolio[2:])
        clave_int += 1
        formatoClave = 'F-{:06d}'.format(clave_int)
        Folio.FolioSalProducto = formatoClave
    elif valor == 4:
        GFolio = Folio.FolioEntMatPrima
        clave_int = int(GFolio[2:])
        clave_int += 1
        formatoClave = 'F-{:06d}'.format(clave_int)
        Folio.FolioEntMatPrima = formatoClave
    elif valor == 5:
        GFolio = Folio.FolioSalMatPrima
        clave_int = int(GFolio[2:])
        clave_int += 1
        formatoClave = 'F-{:06d}'.format(clave_int)
        Folio.FolioSalMatPrima = formatoClave        
    Folio.save()
    return formatoClave

# -------------------------------------------------------------PDF PARA SERVIDOS DE TOLVA--------------------------------------------------------------
def cargamento_tolva(request):
    valor = 1
    formatoClave = cargar_folio(valor)
    fecha_actual = datetime.today()
    formatted_fecha_actual = fecha_actual.strftime("%Y-%m-%d %H-%M-%S")
    user = request.user
    logo_url = request.build_absolute_uri(static('assets/img/inicio/valmo.png'))
    
    tolva = request.POST.get('tolva', '')
    if tolva is not None and tolva != '':
        TTolva = tblTolva.objects.get(ID=tolva)
        alias = TTolva.Alias
        producto = TTolva.IDProducto.ID
        FiltradoProducto= tblProductos.objects.get(ID=producto)
        unidad_id = FiltradoProducto.IDUnidadMedida.ID
        Filtradounidad= tblUnidades.objects.get(ID=unidad_id)
        TContenido = tblServido.objects.filter(IDEstatus_id = 8, IDTolva_id = tolva).order_by('ID').values('Folio',
        'IDCliente_id__Nombre', 'IDCorral_id__Descripcion','CantidadSolicitada', 'CantidadServida')

    html_string = render_to_string('Descargas/PDF/Salida Maquila/index.html', {'logo_url': logo_url, 'Filtradounidad':Filtradounidad, 'folio': formatoClave,
                'alias':alias, 'user': user,  'TContenido': TContenido, 'fecha_actual': fecha_actual, 'FiltradoProducto':FiltradoProducto})

    # Create a BytesIO buffer to receive the PDF
    pdf_buffer = BytesIO()

    # Generate the PDF using xhtml2pdf
    pisa.CreatePDF(html_string, dest=pdf_buffer)

    # Get the PDF content from the buffer
    pdf_file = pdf_buffer.getvalue()

    # Create an HTTP response with the attached PDF file
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Servidos {formatted_fecha_actual}.pdf"'
        # response['Content-Disposition'] = 'attachment; filename="Sálida-' + \
    #     Folio+" "+Nombre+'.pdf"'
    return response

# ------------------------------------------------------------PDF PARA ENTRADA DE PRODUCTOS------------------------------------------------------------
def entradaBasculas(request):
    valor = 2
    formatoClave = cargar_folio(valor)
    fecha_actual = datetime.today()
    formatted_fecha_actual = fecha_actual.strftime("%Y-%m-%d %H-%M-%S")
    user = request.user
    logo_url = request.build_absolute_uri(static('assets/img/inicio/valmo.png'))
    
    entradaBascula = request.POST.get('entradaBascula', '')
    if entradaBascula is not None and entradaBascula != '':
        chofer = tblOtrosDatosMovMP.objects.filter(IDMovMP = entradaBascula).values('ID', 'IDMovMP', 'Costo', 'Flete',
                                                'Maniobra', 'Camion', 'Chofer', 'Placas', 'IDOperador_id__first_name')

        entradaBascula = tblEntradaProductos.objects.filter(IDFolio = entradaBascula).values(
                    'ID', 'IDFolio', 'IDProveedor_id__Nombre', 'IDAlmacen_id__Proveedor', 'IDProductos_id__Descripcion', 
                    'IDPresentacion_id__Descripcion', 'IDPresentacion_id', 'cantidad', 'referencia', 'fecha', 'notas'
        )
    # Render the HTML template with the data
    html_string = render_to_string('Descargas/PDF/EntradaProductos/index.html', {'logo_url': logo_url,
    'formatoClave':formatoClave, 'fecha_actual': fecha_actual, 'entradaBascula':entradaBascula, 'chofer':chofer})

    # Create a BytesIO buffer to receive the PDF
    pdf_buffer = BytesIO()

    # Generate the PDF using xhtml2pdf
    pisa.CreatePDF(html_string, dest=pdf_buffer)

    # Get the PDF content from the buffer
    pdf_file = pdf_buffer.getvalue()

    # Create an HTTP response with the attached PDF file
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Servidos {formatted_fecha_actual}.pdf"'
    return response

# ------------------------------------------------------------PDF PARA SALIDAS DE PRODUCTOS------------------------------------------------------------
def salidaBasculas(request):
    valor = 3
    formatoClave = cargar_folio(valor)
    fecha_actual = datetime.today()
    formatted_fecha_actual = fecha_actual.strftime("%Y-%m-%d %H-%M-%S")
    user = request.user
    logo_url = request.build_absolute_uri(static('assets/img/inicio/valmo.png'))
    
    salidaBascula= request.POST.get('salidaBascula', '')
    if salidaBascula is not None and salidaBascula != '':
        chofer = tblOtrosDatosSalXBas.objects.filter(IDSalida = salidaBascula).values('ID', 'IDSalida', 'Camion', 'Chofer', 'Placas', 'IDOperador')

        clientes = tblSalidaProductos.objects.filter(IDFolio = salidaBascula).values_list('IDCliente__Nombre', flat=True).distinct()
        for cliente in clientes:
            procedencia = cliente
        
        salidaBascula = tblSalidaProductos.objects.filter(IDFolio = salidaBascula).values(
                    'ID', 'IDFolio', 'IDCliente__Nombre', 'IDAlmacen__Proveedor', 'IDProductos_id__Descripcion', 
                    'IDPresentacion_id__Descripcion', 'IDPresentacion_id', 'cantidad', 'referencia', 'fecha', 'notas'
        )

    # Render the HTML template with the data
    html_string = render_to_string('Descargas/PDF/SalidaProductos/index.html', {'logo_url': logo_url,
    'formatoClave':formatoClave, 'fecha_actual': fecha_actual, 'salidaBascula':salidaBascula, 'chofer':chofer,
    'procedencia': procedencia})

    # Create a BytesIO buffer to receive the PDF
    pdf_buffer = BytesIO()

    # Generate the PDF using xhtml2pdf
    pisa.CreatePDF(html_string, dest=pdf_buffer)

    # Get the PDF content from the buffer
    pdf_file = pdf_buffer.getvalue()

    # Create an HTTP response with the attached PDF file
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Servidos {formatted_fecha_actual}.pdf"'
    return response

# ---------------------------------------------------------PDF PARA ENTRADA DE MATERIAS PRIMAS---------------------------------------------------------
def entradaMateriaPrima(request):
    valor = 4
    formatoClave = cargar_folio(valor)
    fecha_actual = datetime.today()
    formatted_fecha_actual = fecha_actual.strftime("%Y-%m-%d %H-%M-%S")
    user = request.user
    logo_url = request.build_absolute_uri(static('assets/img/inicio/valmo.png'))
    
    entradaMateriaPrima = request.POST.get('entradaMateriaPrima', '')
    if entradaMateriaPrima is not None and entradaMateriaPrima != '':
        chofer = tblOtrosDatosMovMP.objects.filter(IDMovMP = entradaMateriaPrima).values('ID', 'IDMovMP', 'Costo', 'Flete',
                                                'Maniobra', 'Camion', 'Chofer', 'Placas', 'IDOperador_id__first_name')
        proveedores = tblEntradaMP.objects.filter(IDFolio=entradaMateriaPrima).values_list('IDProveedor_id__Nombre', flat=True).distinct()
        for proveedor in proveedores:
            procedencia = proveedor

        entradaMatPrima = tblEntradaMP.objects.filter(IDFolio = entradaMateriaPrima).values(
            'ID', 'IDFolio', 'IDProveedor_id__Nombre', 'IDAlmacen_id__Cliente', 'IDMateriaPrima_id__Descripcion', 'IDPresentacion_id__Descripcion',
            'IDPresentacion_id', 'cantidad', 'referencia', 'fecha', 'notas')
        
    # Render the HTML template with the data
    html_string = render_to_string('Descargas/PDF/EntradaMateriaPrima/index.html', {'logo_url': logo_url, 'procedencia':procedencia, 
    'formatoClave':formatoClave, 'fecha_actual': fecha_actual, 'entradaMatPrima':entradaMatPrima, 'chofer':chofer})

    # Create a BytesIO buffer to receive the PDF
    pdf_buffer = BytesIO()

    # Generate the PDF using xhtml2pdf
    pisa.CreatePDF(html_string, dest=pdf_buffer)

    # Get the PDF content from the buffer
    pdf_file = pdf_buffer.getvalue()

    # Create an HTTP response with the attached PDF file
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Entrada Materia Prima {formatted_fecha_actual}.pdf"'
    return response


# ---------------------------------------------------------PDF PARA SALIDAS DE MATERIAS PRIMAS---------------------------------------------------------
def salidaMateriaPrima(request):
    valor = 5
    formatoClave = cargar_folio(valor)
    fecha_actual = datetime.today()
    formatted_fecha_actual = fecha_actual.strftime("%Y-%m-%d %H-%M-%S")
    user = request.user
    logo_url = request.build_absolute_uri(static('assets/img/inicio/valmo.png'))
    
    salidaBascula= request.POST.get('salidaBascula', '')
    if salidaBascula is not None and salidaBascula != '':
        chofer = tblOtrosDatosSalXBas.objects.filter(IDSalida = salidaBascula).values('ID', 'IDSalida', 'Camion', 'Chofer', 'Placas', 'IDOperador')

        clientes = tblSalidaMP.objects.filter(IDFolio = salidaBascula).values_list('IDCliente__Nombre', flat=True).distinct()
        for cliente in clientes:
            procedencia = cliente
        
        salidaBascula = tblSalidaMP.objects.filter(IDFolio = salidaBascula).values(
            'ID', 'IDFolio', 'IDCliente_id__Nombre', 'IDAlmacen_id__Cliente', 'IDMateriaPrima_id__Descripcion', 
            'IDPresentacion_id__Descripcion',   'IDPresentacion_id', 'cantidad', 'referencia', 'fecha', 'notas'
        )

    # Render the HTML template with the data
    html_string = render_to_string('Descargas/PDF/SalidaMateriaPrima/index.html', {'logo_url': logo_url,
    'formatoClave':formatoClave, 'fecha_actual': fecha_actual, 'salidaBascula':salidaBascula, 'chofer':chofer,
    'procedencia': procedencia})

    # Create a BytesIO buffer to receive the PDF
    pdf_buffer = BytesIO()

    # Generate the PDF using xhtml2pdf
    pisa.CreatePDF(html_string, dest=pdf_buffer)

    # Get the PDF content from the buffer
    pdf_file = pdf_buffer.getvalue()

    # Create an HTTP response with the attached PDF file
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Servidos {formatted_fecha_actual}.pdf"'
    return response

