/**
 * Enables live server-side searching, column filtering, and smart pagination for a data table.
 *
 * @param {string} tableBodyId - The ID of the <tbody> element to update.
 * @param {string} searchInputId - The ID of the global search input field.
 * @param {string} paginationId - The ID of the container for pagination buttons.
 * @param {string} fetchUrl - The URL of the Django view to fetch results from (e.g., '/design/search/').
 */
function enableLiveSearch(tableBodyId, searchInputId, paginationId, fetchUrl) {
    const tableBody = document.getElementById(tableBodyId);
    const searchInput = document.getElementById(searchInputId);
    // Select all inputs with the class 'column-filter'
    const columnFilters = document.querySelectorAll(".column-filter");
    const paginationContainer = document.getElementById(paginationId);

    // State variables
    let currentPage = 1;
    let totalPages = 1;

    if (!tableBody) {
        console.error(`Table body with ID '${tableBodyId}' not found.`);
        return;
    }

    /**
     * Gathers current values from all column filter inputs.
     * @returns {Object<string, string>} Map of column index to filter value.
     */
    function getFilterData() {
        const filters = {};
        columnFilters.forEach(filter => {
            const colIndex = filter.dataset.col;
            // Only add if the value is not empty
            if (filter.value.trim()) {
                filters[colIndex] = filter.value.trim();
            }
        });
        return filters;
    }

    /**
     * Helper function to create a pagination button.
     */
    const createButton = (text, pageNum, className, isDisabled = false) => {
        const btn = document.createElement("button");
        btn.textContent = text;
        btn.className = `btn btn-sm ${className} mx-1`;
        btn.disabled = isDisabled;
        if (!isDisabled) {
            // Attach the click event to fetch the specified page
            btn.addEventListener("click", () => fetchResults(pageNum));
        }
        return btn;
    };


    /**
     * Renders smart pagination controls based on server response data.
     * @param {Object} data - The JSON response data from the server.
     */
    function renderPagination(data) {
        if (!paginationContainer) return;

        paginationContainer.innerHTML = "";

        // Only show pagination if there is more than one page
        if (data.total_pages <= 1) return;

        // 1. Previous Button
        paginationContainer.appendChild(
            createButton(
                "« Prev",
                data.previous_page_number,
                data.has_previous ? "btn-outline-primary" : "btn-secondary",
                !data.has_previous
            )
        );

        // 2. Page Number Buttons (Smart Range from server)
        data.page_numbers.forEach(i => {
            const className = i === data.page ? "btn-primary" : "btn-outline-primary";
            paginationContainer.appendChild(
                createButton(i, i, className)
            );
        });

        // 3. Ellipsis and First Page
        // Check if the range starts after page 1
        if (data.page_numbers[0] > 1) {
            // Add the first page button
            const firstPageBtn = createButton(1, 1, "btn-outline-primary");
            // Insert before the first numbered button (which is at index 1 due to Prev button)
            paginationContainer.insertBefore(firstPageBtn, paginationContainer.childNodes[1]);

            // Add ellipsis if there's more than one page gap (e.g., if range starts at 3)
            if (data.page_numbers[0] > 2) {
                const ellipsis = document.createElement("span");
                ellipsis.textContent = "...";
                ellipsis.className = "mx-1 text-muted";
                paginationContainer.insertBefore(ellipsis, paginationContainer.childNodes[2]);
            }
        }

        // 4. Ellipsis and Last Page
        // Check if the range ends before the last page
        if (data.page_numbers[data.page_numbers.length - 1] < data.total_pages) {

            // Add ellipsis if there's more than one page gap
            if (data.page_numbers[data.page_numbers.length - 1] < data.total_pages - 1) {
                const ellipsis = document.createElement("span");
                ellipsis.textContent = "...";
                ellipsis.className = "mx-1 text-muted";
                paginationContainer.appendChild(ellipsis);
            }

            // Add the last page button
            const lastPageBtn = createButton(data.total_pages, data.total_pages, "btn-outline-primary");
            paginationContainer.appendChild(lastPageBtn);
        }

        // 5. Next Button
        paginationContainer.appendChild(
            createButton(
                "Next »",
                data.next_page_number,
                data.has_next ? "btn-outline-primary" : "btn-secondary",
                !data.has_next
            )
        );
    }

    /**
     * Fetches search results from the server based on current filters and page.
     * @param {number} page - The page number to fetch.
     */
    function fetchResults(page = 1) {
        const globalTerm = searchInput ? searchInput.value.trim() : "";
        const filters = getFilterData();

        const params = new URLSearchParams();
        params.append("page", page);
        if (globalTerm) params.append("q", globalTerm);

        // Add column filters
        Object.keys(filters).forEach(key => {
            // Note: Key here is the column index (e.g., 0, 1, 2)
            params.append(`col_${key}`, filters[key]);
        });

        fetch(`${fetchUrl}?${params.toString()}`)
            .then(res => {
                if (!res.ok) {
                    // Check if the response is OK, if not, throw an error
                    throw new Error(`HTTP error! Status: ${res.status} for URL: ${fetchUrl}`);
                }
                return res.json();
            })
            .then(data => {
                // Check for valid data structure
                if (!data || !Array.isArray(data.rows)) {
                    console.error("Invalid data structure received from server:", data);
                    tableBody.innerHTML = `<tr><td colspan="${columnFilters.length + 1}" class="text-danger">Invalid data received. Please check server logs.</td></tr>`;
                    if (paginationContainer) paginationContainer.innerHTML = "";
                    return;
                }

                // Clear the table body before inserting new rows
                tableBody.innerHTML = "";

                // Populate the table with new rows
                if (data.rows.length === 0) {
                    tableBody.innerHTML = `<tr><td colspan="${columnFilters.length + 1}">No results found for your search criteria.</td></tr>`;
                } else {
                    data.rows.forEach(row => {
                        const tr = document.createElement("tr");
                        // The server returns the row HTML within the 'html' property
                        tr.innerHTML = row.html;
                        tableBody.appendChild(tr);
                    });
                }

                currentPage = data.page;
                totalPages = data.total_pages;
                renderPagination(data);
            })
            .catch(error => {
                console.error("Error fetching or processing results:", error);
                // Display a user-friendly error message
                tableBody.innerHTML = `<tr><td colspan="${columnFilters.length + 1}" class="text-danger">Failed to load data. Please check console for network errors.</td></tr>`;
                if (paginationContainer) paginationContainer.innerHTML = "";
            });
    }

    // --- Event Listeners ---

    // Global search listener
    if (searchInput) {
        // Debounce can be added here, but for simplicity, we use direct input/search events
        searchInput.addEventListener("input", () => fetchResults(1));
        searchInput.addEventListener("search", () => fetchResults(1));
    }

    // Column filter listeners
    columnFilters.forEach(filter => {
        filter.addEventListener("input", () => fetchResults(1));
        filter.addEventListener("search", () => fetchResults(1));
    });

    // Initial fetch to load the first page
    fetchResults();
}