const showSpinner = () => 
    document.getElementById("spinner").classList.add("spinner-visible");

const hideSpinner = () => 
    document.getElementById("spinner").classList.remove("spinner-visible");





let courseLengthWeight = 50;
document.getElementById('course-length-weight-value').textContent = "" + courseLengthWeight;

const updateCourseLengthWeight = (value) => {
    courseLengthWeight = value;
    document.getElementById('course-length-weight-value').textContent = "" + value;
}

let distanceWeight = 50;
document.getElementById('distance-weight-value').textContent = "" + distanceWeight;

const updateDistanceWeight = (value) => {
    distanceWeight = value;
    document.getElementById('distance-weight-value').textContent = "" + value;
}

let tariffWeight = 50;
document.getElementById('tariff-weight-value').textContent = "" + tariffWeight;

const updateTariffWeight = (value) => {
    tariffWeight = value;
    document.getElementById('tariff-weight-value').textContent = "" + value;
}

let universityTypeWeight = 50;
document.getElementById('university-type-weight-value').textContent = "" + universityTypeWeight;

const updateUniversityTypeWeight = (value) => {
    universityTypeWeight = value;
    document.getElementById('university-type-weight-value').textContent = "" + value;
}

let yearAbroadWeight = 50;
document.getElementById('year-abroad-weight-value').textContent = "" + yearAbroadWeight;

const updateYearAbroadWeight = (value) => {
    yearAbroadWeight = value;
    document.getElementById('year-abroad-weight-value').textContent = "" + value;
}






document.addEventListener('DOMContentLoaded', () => {
    // Populate grade dropdowns dynamically
    const grades = ["","A*", "A", "B", "C", "D", "E"];
    for (let i = 1; i <= 4; i++) {
        const dropdown = document.getElementById(`grade-dropdown${i}`);
        grades.forEach(grade => {
            const option = document.createElement('option');
            option.value = grade;
            option.textContent = grade;
            dropdown.appendChild(option);
        });
    }
        // Populate subject dropdowns dynamically
        const subjects = [
            "","Biology", "Chemistry", "Physics", "Environmental Science", "Geology", "Psychology", 
            "Mathematics", "Further Mathematics", "Statistics", "History", "Geography", 
            "Religious Studies", "Philosophy", "Politics", "Sociology", "Law", 
            "Classical Civilisation", "English Language", "English Literature", "French", 
            "Spanish", "German", "Italian", "Russian", "Chinese", "Japanese", "Arabic", 
            "Latin", "Ancient Greek", "Welsh (First Language)", "Welsh (Second Language)", 
            "Art and Design", "Fine Art", "Graphic Communication", "Photography", "Textiles", 
            "Drama and Theatre Studies", "Music", "Film Studies", "Media Studies", 
            "Economics", "Business Studies", "Physical Education (PE)", "Computer Science", 
            "Design and Technology (Product Design)", "Electronics"
        ];
        
        for (let i = 1; i <= 4; i++) {
            const dropdown = document.getElementById(`subject-dropdown${i}`);
            subjects.forEach(subject => {
                const option = document.createElement('option');
                option.value = subject;
                option.textContent = subject;
                dropdown.appendChild(option);
            });
        }





    // Search button event listener
    document.getElementById('search-button').addEventListener('click', async () => {
        const resourceUrl = 'http://127.0.0.1:5000/courses/search';

        let response, json;
        try {
            //alert("Fetching data...");
            showSpinner();

            response = await fetch(resourceUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    search_term: document.getElementById('search-input').value,
                    year_abroad: document.getElementById('year-abroad-checkbox').checked,
                    course_length: parseFloat(document.getElementById('course-length-input').value),
                    course_length_weight: courseLengthWeight,
                    university_type: document.getElementById('university-type-dropdown').value,
                    postcode: document.getElementById('postcode-input').value,
                    preferred_distance:document.getElementById('distance-dropdown').value,
                    distance_weight: distanceWeight,
                    tariff_weight: tariffWeight,
                    university_type_weight: universityTypeWeight,
                    year_abroad_weight: yearAbroadWeight,
                    

                    subject: [
                        document.getElementById('subject-dropdown1').value,
                        document.getElementById('subject-dropdown2').value,
                        document.getElementById('subject-dropdown3').value,
                        document.getElementById('subject-dropdown4').value
                    ],
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
                hideSpinner();
                return;
            }

            json = await response.json();
        } catch (error) {
            alert("An error occurred: " + error.message);
            hideSpinner();
            return;
        }

        hideSpinner();

        const results = document.getElementById('results');
        results.innerHTML = '';

        for (let i = 0; i < json.length; i++) {
            const course = json[i];
            results.innerHTML += `<div class="result-box">
                <div class="name"><span class="label">Name: </span><span>${course.course_name}</span></div>
                <div class="university"><span class="label">University: </span><span>${course.university_name}</span></div>
                <div class="course-length"><span class="label">Course Length: </span><span>${course.course_length}</span></div>
                <div class="year-abroad"><span class="label">Year Abroad: </span><span>${course.study_abroad}</span></div>
                <div class="url"><span class="label">URL: </span><a href="${course.course_url}">${course.course_url}</a></div>
                <div class="distance"><span class="label">Distance: </span><span>${course.distance}</span></div>
                <div class="score"><span class="label">Score: </span><span>${course.score}</span></div>
            </div>`;
        }
    });
});
