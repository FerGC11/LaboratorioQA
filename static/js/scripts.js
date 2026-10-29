"use strict";

// Keep the catalog select as the submitted value and progressively add text search.
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("select[data-family-search], select[data-catalog-search]").forEach((select, index) => {
    const input = document.createElement("input");
    const list = document.createElement("datalist");
    const choices = Array.from(select.options).filter(option => option.value);
    list.id = `family-options-${index}`;
    const normalize = value => value.trim().toLocaleLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    function updateSuggestions(value = "") {
      const query = normalize(value);
      const matches = query
        ? choices.filter(option => normalize(option.text).includes(query))
        : choices;
      list.replaceChildren();
      matches.forEach(option => {
        const suggestion = document.createElement("option");
        suggestion.value = option.text;
        list.append(suggestion);
      });
    }
    updateSuggestions();
    input.type = "text";
    input.id = `${select.id}-search-${index}`;
    input.setAttribute("list", list.id);
    input.autocomplete = "off";
    input.placeholder = `Escribe para buscar ${select.dataset.catalogSearch || "familia"}`;
    input.required = select.required;
    select.required = false;
    const label = select.parentElement.querySelector("label");
    if (label) label.htmlFor = input.id;
    function syncText() {
      input.value = select.value ? select.selectedOptions[0].text : "";
      input.setCustomValidity("");
      updateSuggestions();
    }
    input.addEventListener("input", () => {
      updateSuggestions(input.value);
      const match = choices.find(option => normalize(option.text) === normalize(input.value));
      select.value = match ? match.value : "";
      input.setCustomValidity(input.value && !match ? "Selecciona una opcion del catalogo." : "");
    });
    select.form.addEventListener("submit", event => {
      if (!input.reportValidity()) event.preventDefault();
    });
    select.form.addEventListener("reset", () => setTimeout(syncText, 0));
    select.hidden = true;
    select.before(input, list);
    syncText();
  });
});
