const LOCAL_STORAGE_KEY = 'universityCourseSearch'; // Key for local storage

const showSpinner = () => // Show spinner
    document.getElementById("spinner").classList.add("spinner-visible");

const hideSpinner = () =>  // Hide spinner
    document.getElementById("spinner").classList.remove("spinner-visible");

// Load form data from local storage or return default values
const loadForm = () => {
    const storedForm = localStorage.getItem(LOCAL_STORAGE_KEY);
    return storedForm ? JSON.parse(storedForm) : {
        search_term: '',
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
/**
 * Saves the form data to local storage.
 * The form data includes search term, year abroad preference, course length, 
 * course length weight, university type, postcode, preferred distance, 
 * distance weight, tariff weight, university type weight, year abroad weight, 
 * subjects, and grades.
 * 
 * @function
 */
const saveFormToLocalStorage = () => { 
    const form = {
        search_term: document.getElementById('search-input').value,
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
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(form)); // Save form data to local storage
};

// Update weight values when sliders are moved 

const updateTariffWeight = () => {
    const tariffWeight = document.getElementById('tariff-weight-slider').value; 
    document.getElementById('tariff-weight-value').textContent = tariffWeight;
}
const updateCourseLengthWeight = () => {
    const courseLengthWeight = document.getElementById('course-length-weight-slider').value;
    document.getElementById('course-length-weight-value').textContent = courseLengthWeight;
}

const updateDistanceWeight = () => {
    const distanceWeight = document.getElementById('distance-weight-slider').value;
    document.getElementById('distance-weight-value').textContent = distanceWeight;
}

const updateUniversityTypeWeight = () => {
    const universityTypeWeight = document.getElementById('university-type-weight-slider').value;
    document.getElementById('university-type-weight-value').textContent = universityTypeWeight;
}

const updateYearAbroadWeight = () => {
    const yearAbroadWeight = document.getElementById('year-abroad-weight-slider').value;
    document.getElementById('year-abroad-weight-value').textContent = yearAbroadWeight;
}

const getAlternativeCourses = (course) => {
    if (!course.tucked_courses || course.tucked_courses.length == 0) {
        return '';
    }

    // return `Other Courses: ${course.tucked_courses.map(c => JSON.stringify(c)).join(', ')}`;

    return `
        <div class="label"><img class="alternative-courses-arrow" src="/static/assets/arrow.svg"/>Alternative Courses at ${course.university_name}:</div>
        <ul class="alternative-courses-list hidden">
            ${course.tucked_courses.map(c => `<li><a href="${c.course_url}">${c.course_name}</a> (${c.course_length} years)</li>`).join('')}
        </ul>
    `;
}

const toggleAlternativeCourses = (element) => {
    const alternativeCourses = element.querySelector('.alternative-courses-list');
    alternativeCourses.classList.toggle('hidden');
}

const getValidationErrors = (form) => {
    const errors = [];
    if (!form.search_term) {
        errors.push('Please enter a course name to search for.');
    }
    if (!form.course_length || (isNaN(form.course_length) || form.course_length < 1 || form.course_length > 8)) {
        errors.push('Course length must be a number of years between 1 and 8.');
    }
    if (form.postcode.length > 0 && form.postcode.length != 7) {
        errors.push('Postcode must be 7 characters long.');
    }
    if (form.subject.filter(subject => subject).length < 3) {
        errors.push('Please select at least 3 subjects.');
    }
    if (form.grades.filter(grade => grade).length < 3) {
        errors.push('Please enter at least 3 A-level grades.');
    }


    return errors;
}


// Populate form with saved values
document.addEventListener('DOMContentLoaded', () => {
    const form = loadForm();

    // Populate grade dropdowns dynamically
    const grades = ["","A*", "A", "B", "C", "D", "E"]; // Grades array
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
            "","Biology", "Chemistry", "Physics", "Environmental Science", "Geology", "Psychology", // Subjects array
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
    
    document.getElementById('search-input').value = form.search_term || '';
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

    
    document.getElementById('course-length-weight-slider').value = form.course_length_weight || 50;
    document.getElementById('course-length-weight-value').textContent = form.course_length_weight || 50;

    document.getElementById('distance-weight-slider').value = form.distance_weight || 50;
    document.getElementById('distance-weight-value').textContent = form.distance_weight || 50;

    document.getElementById('tariff-weight-slider').value = form.tariff_weight || 50;
    document.getElementById('tariff-weight-value').textContent = form.tariff_weight || 50;

    document.getElementById('university-type-weight-slider').value = form.university_type_weight || 50;
    document.getElementById('university-type-weight-value').textContent = form.university_type_weight || 50; // default value is 50 for the sliders

    document.getElementById('year-abroad-weight-slider').value = form.year_abroad_weight|| 50;
    document.getElementById('year-abroad-weight-value').textContent = form.year_abroad_weight || 50;
});

// Save form when any input changes
document.querySelectorAll('input, select').forEach(element => {
    element.addEventListener('change', saveFormToLocalStorage);
});


// Search button event listener
document.getElementById('search-button').addEventListener('click', async () => {
    saveFormToLocalStorage();
    const form = loadForm();

    const resourceUrl = 'http://127.0.0.1:5000/courses/search'; // URL for the API  

    // Validate the user input:
    const validationErrors = getValidationErrors(form);
    if (validationErrors.length > 0) {
        const results = document.getElementById('results');
        results.innerHTML = `<div class="validation-errors">${validationErrors.join(". ")}</div>`;
        return;
    }

    let response, json;
    try {
        showSpinner(); // Show spinner

        response = await fetch(resourceUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(form)
        });
        console.log(response);
        if (!response.ok) {
            alert("An error occurred while fetching the data");
            hideSpinner(); // Hide spinner on error
            return;
        }

        json = await response.json();
    } catch (error) {
        alert("An error occurred: " + error.message);
        hideSpinner(); // Hide spinner on error
        return;
    }

    hideSpinner(); // Hide spinner on success
    const results = document.getElementById('results');
    results.innerHTML = '';

    json.forEach(course => { // Display results in the results box
        const resultBox = document.createElement('div');
        resultBox.className = 'result-box';
        resultBox.innerHTML = `
            <div class="name"><span class="label">Name: </span><span>${course.course_name}</span></div>
            <div class="university"><span class="label">University: </span><span>${course.university_name}</span></div>
            <div class="course-length"><span class="label">Course Length: </span><span>${course.course_length} years</span></div>
            <div class="year-abroad"><span class="label">Year Abroad: </span><span>${course.study_abroad}</span></div>
            <div class="url"><span class="label">URL: </span><a href="${course.course_url}">${course.course_url}</a></div>
            <div class="distance"><span class="label">Distance: </span><span>${course.distance}</span></div>
            <div class="score"><span class="label">Score: </span><span>${course.score}</span></div>
            <div class="alternative-courses">${getAlternativeCourses(course)}</span></div>

            <button class="dismiss-btn">Dismiss</button>
        `;

        results.appendChild(resultBox);

        resultBox.querySelector('.dismiss-btn').addEventListener('click', () => {
            resultBox.remove(); // Remove result box when dismiss button is clicked
        });

        
    });

    document.querySelectorAll('.alternative-courses').forEach(element => {
        element.addEventListener('click', () => toggleAlternativeCourses(element));
    });
    
});

// Reset button event listener
document.getElementById('reset-button').addEventListener('click', () => {
    localStorage.removeItem(LOCAL_STORAGE_KEY); // Remove form data from local storage
    location.reload(); // Reload the page
});
