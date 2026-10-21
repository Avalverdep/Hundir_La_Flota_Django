const modal = document.getElementById("modal-disparo");
const btnDisparar = document.getElementById("btn-disparar");
const btnCancelar = document.getElementById("btn-cancelar");


if (modal && btnDisparar) {
  btnDisparar.addEventListener("click", () => modal.showModal());
  btnCancelar.addEventListener("click", () => modal.close());
}


const datos = document.getElementById("datos-tablero");
if (datos) {
  console.table(JSON.parse(datos.textContent));
}