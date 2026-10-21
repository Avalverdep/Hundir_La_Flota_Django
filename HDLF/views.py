from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import servicios
from .models import Partida


def partida_de_sesion(request):
    partida_id = request.session.get("partida_id")
    if partida_id is None:
        return None
    return Partida.objects.filter(pk=partida_id).first()


def coordenada_valida(texto):
    return texto.isdigit() and 0 <= int(texto) <= 9


def inicio(request):
    partida = partida_de_sesion(request)
    jugando = partida is not None and partida.estado == Partida.Estado.EN_CURSO
    disparos, propio, barcos_maquina, barcos_jugador = servicios.datos_para_pintar(partida)
    flota_jugador, flota_maquina = servicios.flotas(partida)
    contexto = {
        "tablero": disparos,       # lo que has disparado a la máquina
        "tablero_propio": propio,  # tus barcos y lo que te han disparado
        "columnas": range(10),
        "jugando": jugando,
        "partida_id": partida.pk if partida else "",
        "ultima_jugada": request.session.pop("ultima_jugada", []),  # para animarla una sola vez
        "barcos_maquina": barcos_maquina,
        "barcos_jugador": barcos_jugador,
        "dificultades": Partida.Dificultad.choices,
        "flota_jugador": flota_jugador,
        "flota_maquina": flota_maquina,
    }
    return render(request, "HDLF/tablero.html", contexto)


@require_POST
def empezar(request):
    partida = servicios.crear_partida(request.POST.get("dificultad", "normal"))
    request.session["partida_id"] = partida.pk
    messages.info(request, "Partida nueva, ¡suerte!")
    return redirect("inicio")


@require_POST
def disparar(request):
    partida = partida_de_sesion(request)
    if partida is None or partida.estado != Partida.Estado.EN_CURSO:
        return redirect("inicio")

    fila = request.POST.get("fila", "")
    columna = request.POST.get("columna", "")
    if not (coordenada_valida(fila) and coordenada_valida(columna)):
        messages.error(request, "Coordenadas incorrectas: solo números del 0 al 9")
        return redirect("inicio")

    i, j = int(fila), int(columna)
    resumen = servicios.registrar_disparo(partida, i, j)
    resultado = resumen["resultado"]
    if resultado == "repetido":
        messages.warning(request, "Ya has disparado a esa casilla, prueba otra")
        return redirect("inicio")
        # Lo que ha pasado en esta jugada, en orden, para que el JS lo anime al cargar
    jugada = [{"tablero": "maquina", "fila": i, "columna": j, "resultado": resultado}]
    for tiro in resumen["maquina"]:
        jugada.append({"tablero": "propio", "fila": tiro["fila"], "columna": tiro["columna"], "resultado": tiro["resultado"]})
    request.session["ultima_jugada"] = jugada
    if resultado == "hundido":
        messages.success(request, f"¡Hundido! ({resumen['barco']}) en {i},{j}")
    elif resultado == "tocado":
        messages.success(request, f"¡Tocado en {i},{j}!")
    else:
        messages.info(request, f"Agua en {i},{j}")

    if resumen["trampa"]:
        messages.warning(request, "¡La máquina afina la puntería!")
    for tiro in resumen["maquina"]:
        texto = f"Máquina dispara a {tiro['fila']},{tiro['columna']}: "
        if tiro["resultado"] == "hundido":
            messages.error(request, texto + f"¡hundido! ({tiro['barco']})")
        elif tiro["resultado"] == "tocado":
            messages.error(request, texto + "tocado")
        else:
            messages.info(request, texto + "agua")

    if partida.estado == Partida.Estado.GANADA:
        messages.success(request, "¡Has hundido toda la flota enemiga! Has ganado.")
    elif partida.estado == Partida.Estado.PERDIDA:
        messages.error(request, "La máquina ha hundido toda tu flota. Has perdido.")
    return redirect("inicio")

@require_POST
def rendirse(request):
    partida = partida_de_sesion(request)
    if partida is not None and partida.estado == Partida.Estado.EN_CURSO:
        servicios.rendirse(partida)
        messages.error(request, "Te has rendido. ¡Vuelve a intentarlo!")
    return redirect("inicio")

@require_POST  #Boton limpiar canpo de batalla, limpia ambos tableros y reinicia el juego.
def limpiar(request):
    partida = partida_de_sesion(request)
    if partida is not None:
        servicios.rendirse(partida)  # si estaba en curso, cuenta como abandonada
    request.session.pop("partida_id", None)  # la página vuelve a estar como nueva
    messages.info(request, "Campo de batalla limpio. ¡Listo para una nueva partida!")
    return redirect("inicio")