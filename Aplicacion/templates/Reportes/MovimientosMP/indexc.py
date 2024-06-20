from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, date
from django.contrib.auth.models import Group
# LLAMAR ARCHIVOS LOCALES
from Aplicacion.forms import *
from Aplicacion.models import *
from Aplicacion.views import servicioActivo, estadoPago, registrarPago
from django.db import connection
from django.db.models import Q
import mysql.connector
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TABLAS DE REPORTES >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# ---------------------------------------------------REPORTES DE SERVIDOS---------------------------------------------------


def reporteMovSalidaMP(request):
    FechaDeHoy = date.today().strftime('%Y-%m-%d')
    FContenedores = tblContenedoresMateriaPrima.objects.all()

    if request.method == 'POST':
        if 'reportes' in request.POST:
            Contenedor = request.POST.get('contenedor')
            Fecha = request.POST.get('fecha1')
            Fecha2 = request.POST.get('fecha2')
            if Contenedor == 'todos':
                consulta_sql = """SELECT Aplicacion_tblsalidamp.IDFolio, Aplicacion_tblsalidamp.fecha, 
                Aplicacion_tblmateriaprima.Descripcion, Aplicacion_tblsalidamp.cantidad, 
                Aplicacion_tblcontenedoresmateriaprima.Cliente, Aplicacion_tblsalidamp.Notas
                FROM Aplicacion_tblsalidamp
                INNER JOIN Aplicacion_tblmateriaprima ON Aplicacion_tblmateriaprima.ID = Aplicacion_tblsalidamp.IDMateriaPrima_id
                INNER JOIN Aplicacion_tblcontenedoresmateriaprima ON Aplicacion_tblcontenedoresmateriaprima.ID = Aplicacion_tblsalidamp.IDAlmacen_id
                WHERE (Aplicacion_tblsalidamp.Fecha BETWEEN %s AND %s) ORDER BY Aplicacion_tblsalidamp.Fecha"""
                with connection.cursor() as cursor:
                    cursor.execute(consulta_sql, [Fecha, Fecha2])
                    reprotes = cursor.fetchall()
                Nombre = 'Se trajeron todos los clientes'
                Contenedor = 'todos'
                return render(request, 'Reportes/MovimientosMP/SalidaMP.html', {'reprotes': reprotes,
                                                                                'FContenedores': FContenedores, 'Nombre': Nombre, 'Contenedor': Contenedor, 'Fecha': Fecha, 'Fecha2': Fecha2})
            else:
                consulta_sql = """SELECT Aplicacion_tblsalidamp.IDFolio, Aplicacion_tblsalidamp.fecha, Aplicacion_tblmateriaprima.Descripcion, 
                Aplicacion_tblsalidamp.cantidad, Aplicacion_tblcontenedoresmateriaprima.Cliente, Aplicacion_tblsalidamp.Notas
                FROM Aplicacion_tblsalidamp
                INNER JOIN Aplicacion_tblmateriaprima ON Aplicacion_tblmateriaprima.ID = Aplicacion_tblsalidamp.IDMateriaPrima_id
                INNER JOIN Aplicacion_tblcontenedoresmateriaprima ON Aplicacion_tblcontenedoresmateriaprima.ID = Aplicacion_tblsalidamp.IDAlmacen_id
                WHERE Aplicacion_tblcontenedoresmateriaprima. IDCliente_id_id = %s AND (Aplicacion_tblsalidamp.Fecha  BETWEEN  %s AND  %s ) ORDER BY Aplicacion_tblsalidamp.Fecha"""
                with connection.cursor() as cursor:
                    cursor.execute(consulta_sql, [Contenedor, Fecha, Fecha2])
                    reportes = cursor.fetchall()
                TEContenedores = tblContenedoresMateriaPrima.objects.get(
                    IDCliente_id_id=Contenedor)
                Nombre = TEContenedores.Cliente
                return render(request, 'Reportes/MovimientosMP/SalidaMP.html', {'reportes': reportes,
                                                                                'FContenedores': FContenedores, 'Nombre': Nombre, 'Contenedor': Contenedor, 'Fecha': Fecha, 'Fecha2': Fecha2})
    else:
        consulta_sql = """SELECT Aplicacion_tblmovimientoanimales.Folio, Aplicacion_tblmovimientoanimales.Fecha, 
        Aplicacion_tblclientes.Nombre, Aplicacion_tblcorrales.Descripcion, Aplicacion_tbltipomov.Descripcion AS TipoMov
        FROM Aplicacion_tblmovimientoanimales
        INNER JOIN Aplicacion_tblclientes ON Aplicacion_tblmovimientoanimales. IDCliente_id_id = Aplicacion_tblclientes.ID
        INNER JOIN Aplicacion_tbltipomov ON Aplicacion_tblmovimientoanimales.IDMovimiento_id_id = Aplicacion_tbltipomov.ID 
        INNER JOIN Aplicacion_tblcorrales ON  Aplicacion_tblmovimientoanimales.IDCorral_id =Aplicacion_tblcorrales.ID
        WHERE  (Aplicacion_tblmovimientoanimales.Fecha BETWEEN '2023-08-08' AND '2023-08-09')
        ORDER BY Aplicacion_tblmovimientoanimales.Folio"""

        consulta_sql = """SELECT TT.CLIENTE, 0, TT.ENTRADAS, TT.SALIDAS, TT.ENTRADAS-TT.SALIDAS AS TOTA
        FROM (SELECT  Aplicacion_tblclientes.Nombre AS CLIENTE,
        SUM(case WHEN Aplicacion_tblmovimientoanimales.IDMovimiento_id = 0 AND Aplicacion_tblmovimientoanimales.Fecha BETWEEN Aplicacion_tblcorrales.FechaAsigna 
        AND '2023-08-08' THEN  Aplicacion_tbldetallemovanimales.Cantidad ELSE 0 END) AS ENTRADAS,
        SUM(case WHEN  Aplicacion_tblmovimientoanimales.IDMovimiento_id = 1 AND Aplicacion_tblmovimientoanimales.Fecha BETWEEN Aplicacion_tblcorrales.FechaAsigna 
        AND '2023-08-08' THEN  Aplicacion_tbldetallemovanimales.Cantidad ELSE 0 END) AS SALIDAS
        FROM  Aplicacion_tblmovimientoanimales
        INNER JOIN Aplicacion_tblclientes ON Aplicacion_tblclientes.ID = Aplicacion_tblmovimientoanimales. IDCliente_id 
        INNER JOIN Aplicacion_tblcorrales ON  Aplicacion_tblcorrales.ID = Aplicacion_tblmovimientoanimales.IDCorral_id 
		INNER JOIN Aplicacion_tbldetallemovanimales ON  Aplicacion_tblmovimientoanimales.Folio = Aplicacion_tbldetallemovanimales.IDFolio
        WHERE  Aplicacion_tblmovimientoanimales. IDCliente_id IN (SELECT Aplicacion_tblcorrales.IDCliente_id FROM Aplicacion_tblcorrales WHERE Aplicacion_tblcorrales.IDCliente_id  > 1 )
        GROUP BY Aplicacion_tblmovimientoanimales. IDCliente_id) AS  TT ORDER BY TT.CLIENTE"""

        consulta_sql = """SELECT TT.CORRAL, TT.FECHA, TT.ENTRADAS, TT.SALIDAS, TT.ENTRADAS-TT.SALIDAS AS TOTA
        FROM (SELECT Aplicacion_tblcorrales.Descripcion AS CORRAL ,tblCorrales.FechaAsigna AS FECHA,
        SUM(case WHEN   Aplicacion_tblmovimientoanimales.IDMovimiento = 0 AND  Aplicacion_tblmovimientoanimales.Fecha BETWEEN Aplicacion_tblcorrales.FechaAsigna 
            AND '$Fecha2' THEN   Aplicacion_tblmovimientoanimales.Cantidad ELSE 0 END) AS ENTRADAS,
        SUM(case WHEN   Aplicacion_tblmovimientoanimales.IDMovimiento = 1 AND  Aplicacion_tblmovimientoanimales.Fecha BETWEEN Aplicacion_tblcorrales.FechaAsigna 
            AND '$Fecha2' THEN   Aplicacion_tblmovimientoanimales.Cantidad   ELSE 0 END) AS SALIDAS
        FROM   Aplicacion_tblmovimientoanimales
        INNER JOIN Aplicacion_tblclientes ON Aplicacion_tblclientes.ID =  Aplicacion_tblmovimientoanimales.IDCliente_id 
        INNER JOIN Aplicacion_tblcorrales ON  Aplicacion_tblcorrales.ID =  Aplicacion_tblmovimientoanimales.IDCorral_id
        WHERE   Aplicacion_tblmovimientoanimales.IDCorral_id IN 
            (SELECT Aplicacion_tblcorrales.ID FROM Aplicacion_tblcorrales WHERE Aplicacion_tblcorrales.IDCliente_id = 2) 
            AND  Aplicacion_tblmovimientoanimales.IDCliente_id = 1
        GROUP BY  Aplicacion_tblmovimientoanimales.IDCorral_id) AS  TT
        ORDER BY TT.CORRAL"""

        consulta_sql = """SELECT Aplicacion_tblclientes.Nombre, Aplicacion_tblcorrales.Descripcion,
        SUM(case WHEN  Aplicacion_tblmovimientoanimales.IDMovimiento_id = 0 AND Aplicacion_tblmovimientoanimales.Fecha 
            BETWEEN Aplicacion_tblcorrales.FechaAsigna AND '2023-08-01' THEN  Aplicacion_tbldetallemovanimales.Cantidad ELSE 0 END) - 
        SUM(case WHEN  Aplicacion_tblmovimientoanimales.IDMovimiento_id = 1 AND Aplicacion_tblmovimientoanimales.Fecha  
            BETWEEN Aplicacion_tblcorrales.FechaAsigna AND '2023-08-01' THEN  Aplicacion_tbldetallemovanimales.Cantidad   ELSE 0 END) AS INICIAL,
        SUM(case WHEN  Aplicacion_tblmovimientoanimales.IDMovimiento_id = 0 AND Aplicacion_tblmovimientoanimales.Fecha 
            BETWEEN '2023-08-01' AND '2023-08-11' THEN  Aplicacion_tbldetallemovanimales.Cantidad ELSE 0 END) AS ENTRADA,
        SUM(case WHEN  Aplicacion_tblmovimientoanimales.IDMovimiento_id = 1 AND Aplicacion_tblmovimientoanimales.Fecha 
            BETWEEN '2023-08-01' AND '2023-08-11' THEN  Aplicacion_tbldetallemovanimales.Cantidad  ELSE 0 END) AS SALIDA
        FROM  Aplicacion_tblmovimientoanimales
        INNER JOIN Aplicacion_tblclientes ON Aplicacion_tblclientes.ID = Aplicacion_tblmovimientoanimales. IDCliente_id_id 
        INNER JOIN Aplicacion_tblcorrales ON  Aplicacion_tblcorrales.ID = Aplicacion_tblmovimientoanimales.IDCorral_id
        INNER JOIN Aplicacion_tbldetallemovanimales ON  Aplicacion_tblmovimientoanimales.Folio = Aplicacion_tbldetallemovanimales.IDFolio
        WHERE  Aplicacion_tblmovimientoanimales.IDCorral_id IN (SELECT  Aplicacion_tblcorrales.ID FROM Aplicacion_tblcorrales)
        GROUP BY Aplicacion_tblmovimientoanimales.IDCorral_id"""

        consulta_sql = """
        SELECT  DESCRIP, II, ENTRADAS, SALIDAS,  II+ENTRADAS-SALIDAS AS TOTAL
        FROM(SELECT  MP.MP_DES AS DESCRIP , MP.Cantidad +
                    SUM(CASE WHEN Aplicacion_tblentradamp.Fecha BETWEEN  MP.FECHA_INV  AND DATE('$fcha INTERVAL -1 day')  
                            AND  Aplicacion_tblentradamp.IDAlmacen_id = MP.ALMACEN	THEN tblMovimientosMP.Cantidad ELSE 0 END) - 
                    SUM(CASE WHEN tblMovimientosMP.TipoMov = 1 AND tblMovimientosMP.FechaMov BETWEEN  MP.FECHA_INV  AND DATE('$fcha INTERVAL -1 day') 
                            AND  tblMovimientosMP.IDAlmacen =  MP.ALMACEN 	THEN tblMovimientosMP.Cantidad ELSE 0 END) AS II,
                    SUM(CASE WHEN tblMovimientosMP.TipoMov = 0 AND tblMovimientosMP.FechaMov BETWEEN  '$fcha'  AND  '$fcha' 
                            AND  tblMovimientosMP.IDAlmacen =  MP.ALMACEN	THEN tblMovimientosMP.Cantidad ELSE 0 END) AS ENTRADAS,
                    SUM(CASE WHEN tblMovimientosMP.TipoMov = 1 AND tblMovimientosMP.FechaMov BETWEEN  '$fcha'  AND '$fcha'   
                            AND  tblMovimientosMP.IDAlmacen =  MP.ALMACEN  THEN tblMovimientosMP.Cantidad ELSE 0 END) AS SALIDAS
            FROM (  SELECT IDMP AS IDMP, tblMateriaPrima.Descripcion  AS MP_DES, MAX(tblInventarioInicialesMP.Fecha) AS FECHA_INV, Cantidad, '3' AS ALMACEN
                    FROM tblInventarioInicialesMP
                    INNER JOIN tblMateriaPrima ON tblMateriaPrima.ID = tblInventarioInicialesMP.IDMP
                    WHERE tblInventarioInicialesMP.IDContenedor = '0'
                    GROUP BY IDMP ) AS MP
            LEFT JOIN tblMovimientosMP  ON   tblMovimientosMP.IDMP = MP.IDMP
            GROUP BY MP.IDMP
            ) AS PPAL"""
        consulta_sql = """"
        SELECT Aplicacion_tblcorrales.Descripcion, Aplicacion_tblproductos.Descripcion, Aplicacion_tblunidades.Abreviacion, 
        SUM(Aplicacion_tblservido.CantidadServida)
        FROM Aplicacion_tblservido
        INNER JOIN Aplicacion_tblclientes ON Aplicacion_tblservido.IDCliente_id = Aplicacion_tblclientes.ID 
        INNER JOIN Aplicacion_tblproductos ON Aplicacion_tblservido.IDProducto_id = Aplicacion_tblproductos.ID
        INNER JOIN Aplicacion_tblcorrales ON Aplicacion_tblservido.IDCorral_id	= Aplicacion_tblcorrales.ID     
        INNER JOIN  Aplicacion_tblunidades ON Aplicacion_tblproductos.IDUnidadMedida_id = Aplicacion_tblunidades.ID  
        WHERE  Aplicacion_tblclientes.ID = 2 AND  (Aplicacion_tblservido.Fecha BETWEEN '2023-09-08' AND '2023-09-06' )
        GROUP BY  Aplicacion_tblproductos.Descripcion, Aplicacion_tblservido.IDCorral_id 
        ORDER BY Aplicacion_tblcorrales.Descripcion"""
