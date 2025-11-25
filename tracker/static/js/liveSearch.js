// liveSearch.js
function enableLiveSearch(inputId, tableId) {
    const searchInput = document.getElementById(inputId);
    const tableRows = document.querySelectorAll(`#${tableId} tr`);

    if (!searchInput || !tableRows.length) return;

    searchInput.addEventListener("keyup", function () {
        let filter = this.value.toLowerCase();
        tableRows.forEach(row => {
            row.style.display = row.innerText.toLowerCase().includes(filter) ? "" : "none";
        });
    });
}
