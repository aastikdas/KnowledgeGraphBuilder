document.addEventListener("DOMContentLoaded", () => {
    const analyzeBtn = document.getElementById("analyze-btn");
    const sampleBtn = document.getElementById("sample-btn");
    const textInput = document.getElementById("text-input");
    const loading = document.getElementById("loading");
    const errorMsg = document.getElementById("error-message");
    const resultsContainer = document.getElementById("results-container");

    const sampleText = "Google acquired YouTube in 2006 for $1.65 billion. Sundar Pichai is the CEO of Google. Google is headquartered in Mountain View, California. Larry Page and Sergey Brin founded Google while at Stanford University.";

    // Load Sample Feature
    sampleBtn.addEventListener("click", () => {
        textInput.value = sampleText;
    });

    analyzeBtn.addEventListener("click", async () => {
        const text = textInput.value.trim();
        if (!text) {
            showError("Please enter some text to analyze.");
            return;
        }

        // Reset UI State
        hideError();
        resultsContainer.classList.add("hidden");
        loading.classList.remove("hidden");
        analyzeBtn.disabled = true;

        try {
            const response = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Failed to process text.");
            }

            populateResults(data);

        } catch (err) {
            showError(err.message);
        } finally {
            loading.classList.add("hidden");
            analyzeBtn.disabled = false;
        }
    });

    function populateResults(data) {
        // 1. Update Graph Stats
        document.getElementById("stat-entities").innerText = data.stats.total_entities;
        document.getElementById("stat-relations").innerText = data.stats.total_relationships;
        document.getElementById("stat-types").innerText = data.stats.unique_types;
        document.getElementById("stat-density").innerText = data.stats.density;

        // 2. Set Iframe Source
        document.getElementById("graph-iframe").src = data.graph_html_url;

        // 3. Set Download Links
        document.getElementById("btn-download-png").href = data.png_url;
        document.getElementById("btn-download-csv").href = data.csv_url;

        // 4. Populate Entities Table
        const entitiesTbody = document.querySelector("#entities-table tbody");
        entitiesTbody.innerHTML = "";
        data.entities.forEach(ent => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td style="color: white; font-weight: 500;">${ent.name}</td>
                <td><span style="background: rgba(123, 97, 255, 0.15); color: #9681ff; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem;">${ent.type}</span></td>
            `;
            entitiesTbody.appendChild(tr);
        });

        // 5. Populate Relationships Table
        const relTbody = document.querySelector("#relationships-table tbody");
        relTbody.innerHTML = "";
        data.relationships.forEach(rel => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${rel.source}</td>
                <td style="color: #50fa7b; font-weight: 600; font-size: 0.8rem; text-transform: uppercase;">${rel.relation}</td>
                <td>${rel.target}</td>
            `;
            relTbody.appendChild(tr);
        });

        // Show results container
        resultsContainer.classList.remove("hidden");
        
        // Note: For history to update dynamically without reload, you could append 
        // a new DOM element to the #history-list, but it will sync on next full load anyway.
    }

    function showError(message) {
        errorMsg.innerText = message;
        errorMsg.classList.remove("hidden");
    }

    function hideError() {
        errorMsg.classList.add("hidden");
    }
});