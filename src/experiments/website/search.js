
document.getElementById("search-form").addEventListener("submit", function(e) {
    e.preventDefault();
    let searchQuery = document.getElementById("search-input").value;

    fetch(`http://localhost:8000/search?query=${searchQuery}`)
        .then((response) => response.json())
        .then((data) => {
            let container = document.getElementById("main-container");
            data.results.forEach(result => {
                let resultDiv = document.createElement("div");
                resultDiv.textContent = result;
                container.appendChild(resultDiv);
            });
        })
        .catch((error) => {
            console.error("Error: ", error);
        });
});