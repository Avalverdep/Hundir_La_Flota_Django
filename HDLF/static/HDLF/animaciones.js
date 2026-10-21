// Animaciones de los disparos con GSAP (https://gsap.com).
// La página llega ya con el resultado pintado; aquí "rebobinamos" las casillas
// de la última jugada y las revelamos una a una con su efecto:
//   agua    -> onda + gotas que saltan
//   tocado  -> destello, temblor, brasas y humo
//   hundido -> lo mismo pero más grande, y el tablero entero se sacude
// Además, las casillas tocadas brillan como brasas durante toda la partida.

const reducirMovimiento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (window.gsap && !reducirMovimiento) {
  brasasPermanentes();
  animarUltimaJugada();
}

function animarUltimaJugada() {
  const datos = document.getElementById("datos-ultima-jugada");
  const jugada = datos ? JSON.parse(datos.textContent) : [];
  const pasos = jugada
    .map((tiro) => ({ ...tiro, casilla: buscarCasilla(tiro) }))
    .filter((tiro) => tiro.casilla);
  if (pasos.length === 0) return;

  // Rebobinar: las casillas de esta jugada se ven como agua sin disparar
  pasos.forEach((tiro) => tiro.casilla.classList.add("pendiente"));

  const linea = gsap.timeline({ delay: 0.2 });
  pasos.forEach((tiro, i) => {
    // pausa un poco más larga al pasar de tu disparo a los de la máquina
    const hueco = i > 0 && tiro.tablero !== pasos[i - 1].tablero ? 0.35 : 0.1;
    linea.add(apuntar(tiro.casilla), `+=${hueco}`);
    linea.add(() => impacto(tiro));
    linea.add(() => {}, "+=0.35"); // deja respirar el efecto antes del siguiente
  });
}

function buscarCasilla({ tablero, fila, columna }) {
  return document.querySelector(
    `.tablero[data-tablero="${tablero}"] td[data-fila="${fila}"][data-columna="${columna}"]`
  );
}

// Crea un elemento decorativo centrado en la casilla (coordenadas de página)
function crearEfecto(casilla, clase, tam) {
  const caja = casilla.getBoundingClientRect();
  const el = document.createElement("span");
  el.className = "fx " + clase;
  el.style.width = el.style.height = tam + "px";
  el.style.left = caja.left + window.scrollX + caja.width / 2 - tam / 2 + "px";
  el.style.top = caja.top + window.scrollY + caja.height / 2 - tam / 2 + "px";
  document.body.append(el);
  return el;
}

const azar = (min, max) => gsap.utils.random(min, max); // solo se llama si GSAP ha cargado

// Un aro de mira que cae sobre la casilla
function apuntar(casilla) {
  const mira = crearEfecto(casilla, "fx-mira", 34);
  return gsap
    .timeline({ onComplete: () => mira.remove() })
    .fromTo(mira, { scale: 2.6, opacity: 0, rotation: -90 }, { scale: 1, opacity: 1, rotation: 0, duration: 0.35, ease: "power3.in" })
    .to(mira, { scale: 0.6, opacity: 0, duration: 0.12 });
}

function impacto({ casilla, resultado }) {
  casilla.classList.remove("pendiente");
  if (resultado === "agua") {
    salpicadura(casilla);
  } else {
    explosion(casilla, resultado === "hundido");
  }
}

function salpicadura(casilla) {
  gsap.fromTo(casilla, { scale: 0.6 }, { scale: 1, duration: 0.5, ease: "elastic.out(1, 0.4)" });
  // dos ondas que se expanden
  for (let i = 0; i < 2; i++) {
    const onda = crearEfecto(casilla, "fx-onda", 30);
    gsap.fromTo(onda, { scale: 0.3, opacity: 0.9 }, {
      scale: 2.6, opacity: 0, duration: 0.8, delay: i * 0.15, ease: "power2.out",
      onComplete: () => onda.remove(),
    });
  }
  // gotas que saltan en arco y caen
  for (let i = 0; i < 9; i++) {
    const gota = crearEfecto(casilla, "fx-gota", azar(4, 7));
    const duracion = azar(0.5, 0.75);
    gsap.to(gota, { x: azar(-38, 38), duration: duracion, ease: "none" });
    gsap.to(gota, { y: azar(-55, -25), duration: duracion / 2, ease: "power2.out", yoyo: true, repeat: 1 });
    gsap.to(gota, { opacity: 0, duration: 0.2, delay: duracion - 0.2, onComplete: () => gota.remove() });
  }
}

function explosion(casilla, hundido) {
  const fuerza = hundido ? 1.8 : 1;
  // destello
  const destello = crearEfecto(casilla, "fx-destello", 40 * fuerza);
  gsap.fromTo(destello, { scale: 0.2, opacity: 1 }, {
    scale: 1.8, opacity: 0, duration: 0.45, ease: "power2.out", onComplete: () => destello.remove(),
  });
  // la casilla se enciende y tiembla
  gsap.fromTo(casilla, { scale: 1.5 }, { scale: 1, duration: 0.45, ease: "back.out(3)" });
  gsap.fromTo(casilla, { x: -4 }, { x: 4, duration: 0.05, repeat: 7, yoyo: true, ease: "none", clearProps: "x" });
  // brasas que salen disparadas y caen
  for (let i = 0; i < 14 * fuerza; i++) {
    const brasa = crearEfecto(casilla, "fx-brasa", azar(3, 6));
    const angulo = azar(0, Math.PI * 2);
    const distancia = azar(25, 65) * fuerza;
    gsap.to(brasa, {
      x: Math.cos(angulo) * distancia,
      y: Math.sin(angulo) * distancia + 20, // un poco de gravedad
      opacity: 0, scale: 0.3,
      duration: azar(0.5, 0.9), ease: "power2.out",
      onComplete: () => brasa.remove(),
    });
  }
  // humo que sube y se disipa
  for (let i = 0; i < 4 * fuerza; i++) {
    const humo = crearEfecto(casilla, "fx-humo", azar(14, 22));
    gsap.fromTo(humo, { opacity: 0.7, scale: 0.5 }, {
      x: azar(-15, 15), y: azar(-70, -45) * fuerza, scale: azar(2, 3), opacity: 0,
      duration: azar(1.1, 1.6), delay: 0.1 + i * 0.08, ease: "power1.out",
      onComplete: () => humo.remove(),
    });
  }
  // hundido: el tablero entero se sacude
  if (hundido) {
    const tablero = casilla.closest(".tablero");
    gsap.fromTo(tablero, { x: -8, rotation: -0.6 }, {
      x: 8, rotation: 0.6, duration: 0.06, repeat: 9, yoyo: true, ease: "none", clearProps: "x,rotation",
    });
  }
}

// Las casillas tocadas laten como brasas (cada una a su ritmo)
function brasasPermanentes() {
  gsap.to(".tablero td.tocado", {
    boxShadow: "inset 0 0 10px 3px rgba(255, 190, 40, .95)",
    duration: 0.7,
    repeat: -1,
    yoyo: true,
    ease: "sine.inOut",
    stagger: { each: 0.2, from: "random" },
  });
}