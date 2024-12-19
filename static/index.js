document.getElementById('search-button').addEventListener('click', async () => {
    const resourceUrl = 'http://127.0.0.1:5000/courses/search';

    let response, json;
    try {
        response = await fetch(resourceUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                search_term: document.getElementById('search-input').value,
                year_abroad: document.getElementById('year-abroad-checkbox').checked,
                course_length: parseFloat(document.getElementById('course-length-input').value),
                university_type: document.getElementById('university-type-dropdown').value,
                grades: [
                    document.getElementById('grade-dropdown1').value,
                    document.getElementById('grade-dropdown2').value,
                    document.getElementById('grade-dropdown3').value,
                    document.getElementById('grade-dropdown4').value
                ]
            })
        });

        if (!response.ok) {
            alert("An error occurred while fetching the data");
            return;
        }

        json = await response.json();
    } catch (error) {
        alert("An error occurred: " + error.message);
        return;
    }

    const results = document.getElementById('results');
    results.innerHTML = '';

    for (let i = 0; i < json.length; i++) {
        const course = json[i];
        results.innerHTML += `<div class="result-box">
            <div class="name"><span class="label">Name: </span><span>${course.course_name}</span></div>
            <div class="university"><span class="label">University: </span><span>${course.university_id}</span></div>
            <div class="course-length"><span class="label">Course Length: </span><span>${course.course_length}</span></div>
            <div class="year-abroad"><span class="label">Year Abroad: </span><span>${course.study_abroad}</span></div>
        </div>`;
    }
});
