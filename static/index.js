
document.getElementById('search-button').addEventListener('click', async () => {

    const resourceUrl = 'https://api.github.com/users';

    const response = await fetch(resourceUrl);

    if (!response.ok) {
        alert("An error occurred while fetching the data");
        return;
    }

    const json = await response.json();

    const results = document.getElementById('results');
    results.innerHTML = '';

    for (let i = 0; i < json.length; i++) {
        const user = json[i];
        results.innerHTML += `<div class="result-box">
                <div class="name"><span class="label">Name: </span><span>${user.login}</span></div>
                <div class="id"><span class="label">ID: </span><span>${user.id}</span></div>
        </div>`;
    }

});
