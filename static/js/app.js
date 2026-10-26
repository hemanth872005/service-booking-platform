document.addEventListener("DOMContentLoaded", () => {
  const search = document.getElementById("serviceSearch");
  if (search) {
    search.addEventListener("input", () => {
      const term = search.value.trim().toLowerCase();
      document.querySelectorAll(".service-card").forEach(card => {
        card.hidden = !card.dataset.search.includes(term);
      });
    });
  }
  document.querySelectorAll("[data-confirm]").forEach(button => {
    button.addEventListener("click", event => {
      if (!window.confirm(button.dataset.confirm)) event.preventDefault();
    });
  });
  const slotStatus = document.getElementById("slotStatus");
  if (slotStatus && window.serviceSlotsApi) {
    fetch(window.serviceSlotsApi, {headers: {"X-Requested-With": "XMLHttpRequest"}})
      .then(response => {
        if (!response.ok) throw new Error("Could not load slots");
        return response.json();
      })
      .then(data => {
        slotStatus.textContent = `${data.slots.length} available slot(s) currently reported by the server.`;
      })
      .catch(() => { slotStatus.textContent = "Availability is shown below; refresh the page if it looks outdated."; });
  }
});
