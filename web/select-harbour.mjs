import "./harbour.mjs";
const select = document.querySelector("#harbour");
function update() {
  document.querySelector("#halifax-area").hidden = select.value !== "halifax";
  document.querySelector("#vancouver-area").hidden =
    select.value !== "vancouver";
}
select.addEventListener("change", update);
update();
