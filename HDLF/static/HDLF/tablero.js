// Modales: cualquier botón con data-abrir-modal="id" abre ese <dialog>,
// y cualquier botón con data-cerrar-modal cierra el <dialog> en el que está.
document.querySelectorAll("[data-abrir-modal]").forEach((boton) => {
  boton.addEventListener("click", () => {
    document.getElementById(boton.dataset.abrirModal).showModal();
  });
});
document.querySelectorAll("[data-cerrar-modal]").forEach((boton) => {
  boton.addEventListener("click", () => boton.closest("dialog").close());
});

// Selector de dificultad: avisa de lo que hace el nivel adaptativo
const selectDificultad = document.getElementById("select-dificultad");
const infoDificultad = document.getElementById("info-dificultad");
if (selectDificultad && infoDificultad) {
  selectDificultad.addEventListener("change", () => {
    infoDificultad.hidden = selectDificultad.value !== "adaptativa";
  });
}

// Imágenes de los barcos: si el PNG existe se muestra y se oculta el dibujo provisional
document.querySelectorAll("img.barco-img").forEach((img) => {
  const mostrar = () => {
    img.hidden = false;
    img.nextElementSibling.hidden = true; // el .barco-dibujo
  };
  if (img.complete && img.naturalWidth > 0) mostrar();
  else img.addEventListener("load", mostrar);
});
// Historial: los mensajes de cada jugada se guardan en el navegador (localStorage),
// una lista por partida, y se pintan en el cuadro de la derecha y en su modal ampliado.
const PREFIJO_HISTORIAL = "hdlf-historial-";
const panelHistorial = document.getElementById("historial");

function leerHistorial(clave) {
  try {
    return JSON.parse(localStorage.getItem(clave)) || [];
  } catch (e) {
    return [];
  }
}

function guardarHistorial(clave, lista) {
  try {
    localStorage.setItem(clave, JSON.stringify(lista));
  } catch (e) {
    // sin almacenamiento: el historial solo vive mientras dura esta página
  }
}

function pintarHistorial(lista) {
  for (const id of ["historial-lista", "historial-lista-ampliada"]) {
    const ul = document.getElementById(id);
    ul.replaceChildren();
    if (lista.length === 0) {
      const vacio = document.createElement("li");
      vacio.textContent = "Aún no has jugado ninguna partida.";
      ul.append(vacio);
    }
    for (const entrada of lista) {
      const li = document.createElement("li");
      li.className = entrada.tipo;
      li.textContent = entrada.texto;
      ul.append(li);
    }
    ul.scrollTop = ul.scrollHeight;
  }
}

if (panelHistorial) {
  const partida = panelHistorial.dataset.partida;
  let historial = [];
  const clave = PREFIJO_HISTORIAL + partida;
  // Esta logica se encarga de eliminar la partida de bbdd, y del historial 
  try {
    Object.keys(localStorage)
      .filter((k) => k.startsWith(PREFIJO_HISTORIAL) && (!partida || k !== clave))
      .forEach((k) => localStorage.removeItem(k));
  } catch (e) {}
  if (partida) {
    historial = leerHistorial(clave);
    // Los mensajes que Django acaba de mostrar son las jugadas nuevas
    document.querySelectorAll(".mensajes li").forEach((li) => {
      historial.push({ texto: li.textContent.trim(), tipo: li.className });
    });
    guardarHistorial(clave, historial);
  }
  pintarHistorial(historial);
}

// Depuración: ambos tableros en F12 -> Console
for (const [id, titulo] of [["datos-tablero", "Disparos a la máquina"], ["datos-tablero-propio", "Tu tablero"]]) {
  const datos = document.getElementById(id);
  if (datos) {
    console.log(titulo);
    console.table(JSON.parse(datos.textContent));
  }
}

// ---------- Limpiar con fuego ----------
// Al confirmar "Limpiar", en vez de enviar el formulario directamente:
// 1) una cortina de fuego barre la pantalla de izquierda a derecha,
// 2) cada elemento se tuesta y suelta cenizas cuando el fuego le alcanza,
// 3) al terminar se envía el formulario y la página limpia aparece con un fundido.
const DURACION_FUEGO = 1400; // ms que tarda la cortina en cruzar la pantalla
const MAX_CENIZAS = 700;
const formLimpiar = document.querySelector("#modal-limpiar form");
const sinAnimaciones = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (formLimpiar && !sinAnimaciones) {
  formLimpiar.addEventListener("submit", (evento) => {
    evento.preventDefault(); // paramos el envío para animar primero
    formLimpiar.closest("dialog").close();
    quemarPantalla(() => {
      try {
        sessionStorage.setItem("hdlf-limpiado", "1"); // para el fundido de la página nueva
      } catch (e) {}
      formLimpiar.submit(); // submit() no vuelve a lanzar el evento: no hay bucle
    });
  });
}

function quemarPantalla(alTerminar) {
  const fuego = document.createElement("div");
  fuego.className = "barrido-fuego";
  fuego.style.animationDuration = DURACION_FUEGO + "ms";
  document.body.append(fuego);

  const ancho = window.innerWidth;
  let cenizas = 0;
  // El frente del fuego recorre 1,6 anchos de pantalla en DURACION_FUEGO:
  // calculamos cuándo llega a una x concreta
  const llegaA = (x) => Math.max(0, (x / (1.6 * ancho)) * DURACION_FUEGO);

  // Casillas, títulos, botones y mensajes: arden cuando el fuego llega a su centro
  const elementos = document.querySelectorAll(
    ".principal h1, .principal h2, .tablero th, .tablero td, .principal > button, .mensajes li, #flota h2, #flota h3, #flota li, #historial h2, #historial li"
  ); 
  elementos.forEach((el) => {
    const caja = el.getBoundingClientRect();
    const visible = caja.bottom > 0 && caja.top < window.innerHeight;
    setTimeout(() => {
      el.classList.add("quemado");
      if (visible) cenizas += soltarCenizas(caja, MAX_CENIZAS - cenizas);
    }, llegaA(caja.left + caja.width / 2));
  });

  // Las tablas (y sus bordes) y el cuadro del historial desaparecen
  // cuando el fuego ha pasado su borde derecho
  document.querySelectorAll(".tablero, #historial, #flota").forEach((el) => {
    setTimeout(() => el.classList.add("quemado"), llegaA(el.getBoundingClientRect().right));
  });
  setTimeout(alTerminar, DURACION_FUEGO + 300);
}

function soltarCenizas(caja, disponibles) {
  const cantidad = Math.max(0, Math.min(Math.round((caja.width * caja.height) / 300), 45, disponibles));
  for (let i = 0; i < cantidad; i++) {
    const ceniza = document.createElement("span");
    ceniza.className = Math.random() < 0.3 ? "ceniza brasa" : "ceniza";
    ceniza.style.left = caja.left + Math.random() * caja.width + "px";
    ceniza.style.top = caja.top + Math.random() * caja.height + "px";
    ceniza.style.setProperty("--dx", 20 + Math.random() * 90 + "px");     // el fuego las empuja a la derecha
    ceniza.style.setProperty("--dy", -(30 + Math.random() * 100) + "px"); // y suben
    ceniza.style.animationDelay = Math.random() * 250 + "ms";
    ceniza.addEventListener("animationend", () => ceniza.remove());
    document.body.append(ceniza);
  }
  return cantidad;
}

// Página recién limpiada: aparece con un fundido
try {
  if (sessionStorage.getItem("hdlf-limpiado")) {
    sessionStorage.removeItem("hdlf-limpiado");
    document.body.classList.add("renacer");
  }
} catch (e) {}