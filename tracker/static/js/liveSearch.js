// liveSearch.js (FINAL UNIFIED VERSION)

function enableLiveSearch(tableBodyId, searchInputId) {
    const tableBody = document.getElementById(tableBodyId);
    const searchInput = document.getElementById(searchInputId);
    const columnFilters = document.querySelectorAll(".column-filter");

    // Guard clause: If table body isn't found, stop running
    if (!tableBody) return;

    // Cache all rows once on load
    const tableRows = tableBody.querySelectorAll("tr");

    // 1. Listen for changes in the Universal Search Bar
    if (searchInput) {
        searchInput.addEventListener("keyup", performSearch);
        searchInput.addEventListener("search", performSearch);
    }

    // 2. Listen for changes in ALL Column Filters
    if (columnFilters.length > 0) {
        columnFilters.forEach(filter => {
            filter.addEventListener("keyup", performSearch);
            filter.addEventListener("search", performSearch);
        });
    }

    // 3. The Master Search Function (Runs every time any input changes)
    function performSearch() {
        const globalTerm = searchInput ? searchInput.value.toLowerCase().trim() : "";

        tableRows.forEach(row => {
            let isVisible = true;

            // --- STEP A: Check Universal Search (First pass) ---
            if (globalTerm && !row.innerText.toLowerCase().includes(globalTerm)) {
                isVisible = false;
            }

            // --- STEP B: Check Column Filters (Second pass, only if not yet hidden) ---
            if (isVisible && columnFilters.length > 0) {
                columnFilters.forEach(filter => {
                    // Stop checking columns if the row has already failed a test
                    if (!isVisible) return;

                    const colIndex = parseInt(filter.dataset.col); // Use parseInt()
                    const filterValue = filter.value.toLowerCase().trim();
                    const cell = row.querySelectorAll("td")[colIndex];

                    // Check if this specific column filter has a value AND the cell exists
                    if (filterValue && cell) {
                        if (!cell.innerText.toLowerCase().includes(filterValue)) {
                            isVisible = false; // Failed this column filter
                        }
                    }
                });
            }

            // --- STEP C: Apply Visibility ---
            // If isVisible is true (passed all checks), display the row.
            row.style.display = isVisible ? "" : "none";
        });
    }
}