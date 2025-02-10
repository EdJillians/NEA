const LOCAL_STORAGE_KEY = 'universityCourseSearch';

const showSpinner = () => 
    document.getElementById("spinner").classList.add("spinner-visible");

const hideSpinner = () => 
    document.getElementById("spinner").classList.remove("spinner-visible");

// Load form data from local storage or use default values
const loadForm = () => {
    const storedForm = localStorage.getItem(LOCAL_STORAGE_KEY);
    return storedForm ? JSON.parse(storedForm) : {
        course: '',
        year_abroad: false,
        course_length: '3',
        course_length_weight: 50,
        university_type: 'campus',
        postcode: '',
        preferred_distance: '',
        distance_weight: 50,
        tariff_weight: 50,
        university_type_weight: 50,
        year_abroad_weight: 50,
        subject: ['', '', '', ''],
        grades: ['', '', '', '']
    };
};

// Save form data to local storage
const saveFormToLocalStorage = () => {
    const form = {
        course: document.getElementById('search-input').value,
        year_abroad: document.getElementById('year-abroad-checkbox').checked,
        course_length: document.getElementById('course-length-input').value,
        course_length_weight: document.getElementById('course-length-weight-slider').value,
        university_type: document.getElementById('university-type-dropdown').value,
        postcode: document.getElementById('postcode-input').value,
        preferred_distance: document.getElementById('distance-dropdown').value,
        distance_weight: document.getElementById('distance-weight-slider').value,
        tariff_weight: document.getElementById('tariff-weight-slider').value,
        university_type_weight: document.getElementById('university-type-weight-slider').value,
        year_abroad_weight: document.getElementById('year-abroad-weight-slider').value,
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
    };
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(form));
};

// Populate form with saved values
document.addEventListener('DOMContentLoaded', () => {
    const form = loadForm();

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




    document.getElementById('search-input').value = form.course;
    document.getElementById('year-abroad-checkbox').checked = form.year_abroad;
    document.getElementById('course-length-input').value = form.course_length || '';
    document.getElementById('university-type-dropdown').value = form.university_type;
    if (form.postcode){
        document.getElementById('postcode-input').value = form.postcode;
    }
    
    document.getElementById('distance-dropdown').value = form.preferred_distance;

    if(form.subject && form.subject.length == 4) {
        document.getElementById('subject-dropdown1').value = form.subject[0];
        document.getElementById('subject-dropdown2').value = form.subject[1];
        document.getElementById('subject-dropdown3').value = form.subject[2];
        document.getElementById('subject-dropdown4').value = form.subject[3];
    }
    
    if (form.grades && form.grades.length == 4) {
        document.getElementById('grade-dropdown1').value = form.grades[0];
        document.getElementById('grade-dropdown2').value = form.grades[1];
        document.getElementById('grade-dropdown3').value = form.grades[2];
        document.getElementById('grade-dropdown4').value = form.grades[3];
    }

    document.getElementById('course-length-weight-slider').value = form.course_length_weight;
    document.getElementById('distance-weight-slider').value = form.distance_weight;
    document.getElementById('tariff-weight-slider').value = form.tariff_weight;
    document.getElementById('university-type-weight-slider').value = form.university_type_weight;
    document.getElementById('year-abroad-weight-slider').value = form.year_abroad_weight;
});

// Save form when any input changes
document.querySelectorAll('input, select').forEach(element => {
    element.addEventListener('change', saveFormToLocalStorage);
});

// Search button event listener
document.getElementById('search-button').addEventListener('click', async () => {
    saveFormToLocalStorage();
    const form = loadForm();

    const resourceUrl = 'http://127.0.0.1:5000/courses/search';

    let response, json;
    try {
        showSpinner();

        response = await fetch(resourceUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(form)
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

    json.forEach(course => {
        const resultBox = document.createElement('div');
        resultBox.className = 'result-box';
        resultBox.innerHTML = `
            <div class="name"><span class="label">Name: </span><span>${course.course_name}</span></div>
            <div class="university"><span class="label">University: </span><span>${course.university_name}</span></div>
            <div class="course-length"><span class="label">Course Length: </span><span>${course.course_length}</span></div>
            <div class="year-abroad"><span class="label">Year Abroad: </span><span>${course.study_abroad}</span></div>
            <div class="url"><span class="label">URL: </span><a href="${course.course_url}">${course.course_url}</a></div>
            <div class="distance"><span class="label">Distance: </span><span>${course.distance}</span></div>
            <div class="score"><span class="label">Score: </span><span>${course.score}</span></div>
            <button class="dismiss-btn">Dismiss</button>
        `;

        results.appendChild(resultBox);

        resultBox.querySelector('.dismiss-btn').addEventListener('click', () => {
            resultBox.remove();
        });
    });
});
