/**
 * Shows the spinner element by adding the "spinner-visible" class.
 * @function
 */
const showSpinner = () => // Show spinner
    document.getElementById("spinner").classList.add("spinner-visible");

/**
 * Hides the spinner element by removing the "spinner-visible" class.
 * @function
 */
const hideSpinner = () =>  // Hide spinner
    document.getElementById("spinner").classList.remove("spinner-visible");

/**
 * Loads form data from local storage or returns default values if no data is found.
 * @function
 * @returns {Object} The form data object.
 */
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

/**
 * Updates the tariff weight slider value when the user moves it.
 * @function
 */
const updateTariffWeight = () => {
    const tariffWeight = document.getElementById('tariff-weight-slider').value; 
    document.getElementById('tariff-weight-value').textContent = tariffWeight;
}

/**
 * Updates the course length weight slider value when the user moves it.
 * @function
 */
const updateCourseLengthWeight = () => {
    const courseLengthWeight = document.getElementById('course-length-weight-slider').value;
    document.getElementById('course-length-weight-value').textContent = courseLengthWeight;
}

/**
 * Updates the distance weight slider value when the user moves it.
 * @function
 */
const updateDistanceWeight = () => {
    const distanceWeight = document.getElementById('distance-weight-slider').value;
    document.getElementById('distance-weight-value').textContent = distanceWeight;
}

/**
 * Updates the university type weight slider value when the user moves it.
 * @function
 */
const updateUniversityTypeWeight = () => {
    const universityTypeWeight = document.getElementById('university-type-weight-slider').value;
    document.getElementById('university-type-weight-value').textContent = universityTypeWeight;
}

/**
 * Updates the year abroad weight slider value when the user moves it.
 * @function
 */
const updateYearAbroadWeight = () => {
    const yearAbroadWeight = document.getElementById('year-abroad-weight-slider').value;
    document.getElementById('year-abroad-weight-value').textContent = yearAbroadWeight;
}

/**
 * Extracts the alternative courses from the course object and returns them as an HTML string.
 * @function
 * @param {Object} course - The course object containing alternative courses.
 * @returns {string} The HTML string for alternative courses.
 */
const getAlternativeCourses = (course) => {
    if (!course.tucked_courses || course.tucked_courses.length == 0) {
        return '';
    }
    return `
        <div class="label"><img class="alternative-courses-arrow" src="/static/assets/arrow.svg"/>Alternative Courses at ${course.university_name}:</div>
        <ul class="alternative-courses-list hidden">
            ${course.tucked_courses.map(c => `<li><a href="${c.course_url}">${c.course_name}</a> (${c.course_length} years)</li>`).join('')}
        </ul>
    `;
}

/**
 * Generates the HTML content for displaying course requirements.
 * @function
 * @param {Object} course - The course object containing requirements.
 * @returns {string} The HTML string for course requirements.
 */
const getRequirements = (course) => {
    if (!course.requirements || course.requirements.length == 0) {
        return '';
    }

    return `
        <div class="label"><img class="requirements-arrow" src="/static/assets/arrow.svg"/>Requirements:</div>
        <ul class="requirements-list hidden">
            ${course.requirements.map(req => `<li>${req.subject}: ${req.grade}</li>`).join('')}
        </ul>  
    `;
}

/**
 * Toggles the visibility of the alternative courses list when the user clicks on the alternative courses button.
 * @function
 * @param {HTMLElement} element - The HTML element containing the alternative courses list.
 * @returns {void}
 */
const toggleAlternativeCourses = (element) => {
    const alternativeCourses = element.querySelector('.alternative-courses-list');
    alternativeCourses.classList.toggle('hidden');
}

/**
 * Toggles the visibility of the requirements list when the user clicks on the requirements button.
 * @function
 * @param {HTMLElement} element - The HTML element containing the requirements list.
 * @returns {void}
 */
const toggleRequirements = (element) => {
    const requirements = element.querySelector('.requirements-list');
    requirements.classList.toggle('hidden');
}

/**
 * Validates the user input and returns an array of error messages.
 * @function
 * @param {Object} form - The form data object.
 * @returns {Array} An array of error messages.
 */
const getValidationErrors = (form) => {
    const errors = [];
    const postcodeRegex = /^[A-Z]{1,2}[0-9][0-9A-Z]?\s?[0-9][A-Z]{2}$/i;

    if (!form.search_term) {
        errors.push('Please enter a course name to search for.');
    }
    if (!form.course_length || (isNaN(form.course_length) || form.course_length < 1 || form.course_length > 8)) {
        errors.push('Course length must be a number of years between 1 and 8.');
    }
    if (!postcodeRegex.test(form.postcode)) {
        errors.push('Please enter a valid UK postcode.');
    }
    if (form.subject.filter(subject => subject).length < 3) {
        errors.push('Please select at least 3 subjects.');
    }
    if (form.grades.filter(grade => grade).length < 3) {
        errors.push('Please enter at least 3 A-level grades.');
    }

    for (let i = 0; i < form.subject.length; i++) {
        if ((form.subject[i] && !form.grades[i]) || (!form.subject[i] && form.grades[i])) {
            errors.push('Each subject must have a corresponding grade and vice versa.');
            break;
        }
    }

    if (form.course_length_weight == 0 && form.distance_weight == 0 && form.tariff_weight == 0 && form.university_type_weight == 0 && form.year_abroad_weight == 0) {
        errors.push('Please enter at least one weight value greater than 0.');
    }

    return errors;
}

/**
 * Adds a course to the list of favourite courses in local storage.
 * @function
 * @param {Object} course - The course object to add to favourites.
 */
const addFavouriteCourse = (course) => {
    let favouriteCourses = localStorage.getItem(FAVOURITE_COURSES_STORAGE_KEY);
    console.log(favouriteCourses);
    if (favouriteCourses) {
        favouriteCourses = JSON.parse(favouriteCourses);
    } else {
        favouriteCourses = [];
    }
    favouriteCourses.push(course);
    localStorage.setItem(FAVOURITE_COURSES_STORAGE_KEY, JSON.stringify(favouriteCourses));
}

/**
 * Removes a course from the list of favourite courses in local storage.
 * @function
 * @param {number} id - The ID of the course to remove.
 * @returns {void}
 */

const removeFavouriteCourse = (id) => {
    let favouriteCourses = localStorage.getItem(FAVOURITE_COURSES_STORAGE_KEY);
    if (!favouriteCourses) {
        return;
    }
    favouriteCourses = JSON.parse(favouriteCourses);
    favouriteCourses = favouriteCourses.filter(course => course.course_id !== id);
    localStorage.setItem(FAVOURITE_COURSES_STORAGE_KEY, JSON.stringify(favouriteCourses));
}


/**
 * Checks if a course is in the list of favourite courses.
 * @function
 * @param {number} id - The ID of the course to check.
 * @returns {boolean} True if the course is in the list, false otherwise.
 */
const isFavouriteCourse = (id) => {
    let favouriteCourses = localStorage.getItem(FAVOURITE_COURSES_STORAGE_KEY);
    if (!favouriteCourses) {
        return false;
    }
    favouriteCourses = JSON.parse(favouriteCourses);
    return favouriteCourses.some(course => course.course_id === id);
}

/**
 * Returns the list of favourite courses from local storage.
 * @function
 * @returns {Array} The list of favourite courses.
 * @returns {Array} An empty array if no favourite courses are found.
*/
const getFavouriteCourses = () => {
    let favouriteCourses = localStorage.getItem(FAVOURITE_COURSES_STORAGE_KEY);
    if (!favouriteCourses) {
        return [];
    }
    return JSON.parse(favouriteCourses);
}


/**
 * Clears the list of favourite courses from local storage.
 * @function
 * @returns {void} 
 */
const clearFavouriteCourses = () => {
    localStorage.removeItem(FAVOURITE_COURSES_STORAGE_KEY);
}






/**
 * Creates the results display by adding result boxes to the results element.
 * @function
 * @param {Array} courses - The array of course objects to display.
 * @param {HTMLElement} element - The HTML element to add the result boxes to.
 * @returns {void}
 */
const createResultsDisplay = (courses, element) => {
    
    element.innerHTML = '';

    courses.forEach(course => {
        const resultBox = document.createElement('div');
        resultBox.className = 'result-box';
        resultBox.innerHTML = `
            <div class="name"><span class="label"></span><a href="${course.course_url}" style="font-size: 30px; font-weight: bold;">${course.course_name}</a></div>
            
            <div class="university"><span class="label"></span><span style="font-size: 20px;">${course.university_name}</span></div>
            <div class="course-length"><span class="label">Course Length: </span><span>${course.course_length} years</span></div>
            <div class="year-abroad"><span class="label">Year Abroad: </span><span>${course.study_abroad}</span></div>
            <div class="distance"><span class="label">Distance: </span><span>${course.distance} km</span></div>
            <div class="score"><span class="label">Score: </span><span>${course.score}</span></div>
            
            <div class="alternative-courses">${getAlternativeCourses(course)}</div>

            <div class="requirements">${getRequirements(course)}</div>

            ${course.warnings && course.warnings.length > 0 ? `<div class="warnings"><span class="label">Warning: </span><span>${course.warnings}</span></div>` : ''}

            <button class="dismiss-btn">Dismiss</button>

            <img class="favourite-btn" src="/static/assets/favourite.svg" alt="Favourite" />
            <img class="unfavourite-btn" src="/static/assets/favourite-filled.svg" alt="Unfavourite" />
        `;

        element.appendChild(resultBox);

        if (isFavouriteCourse(course.course_id)) {
            resultBox.classList.add('favourite');
        }

        resultBox.querySelector('.dismiss-btn').addEventListener('click', () => {
            resultBox.remove(); // Remove result box when dismiss button is clicked
        });

        resultBox.querySelector('.favourite-btn').addEventListener('click', () => {
            addFavouriteCourse(course);
            resultBox.classList.add('favourite');
        });

        resultBox.querySelector('.unfavourite-btn').addEventListener('click', () => {
            removeFavouriteCourse(course.course_id);
            resultBox.classList.remove('favourite');
        });
        
    });

    document.querySelectorAll('.alternative-courses').forEach(element => {
        element.addEventListener('click', () => toggleAlternativeCourses(element));

    });
    document.querySelectorAll('.requirements').forEach(element => {
        element.addEventListener('click', () => toggleRequirements(element));
    });
}

/**
 * Initializes the home page by loading the list of favourite courses from local storage and displaying them.
 * @function
 * @returns {void}
 */
const initHomePage = () => {
    document.addEventListener('DOMContentLoaded', () => {
        const favouriteCourses = getFavouriteCourses();
        const results = document.getElementById('results');
        if (favouriteCourses.length > 0) {
            createResultsDisplay(favouriteCourses, results);
        }
    });
}

/**
 * Initializes the search page by loading the form data from local storage and adding event listeners to the form elements.
 * @function
 * @returns {void}
 */
const initSearchPage = () => {
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
                '', 'Accounting', 'Ancient Greek', 'Ancient History', 'Arabic', 'Art and Design', 'Biology',
                 'Business Studies', 'Chemistry', 'Chinese', 'Classical Civilisation', 'Computer Science',
                  'Dance', 'Design and Technology (Product Design)', 'Drama and Theatre Studies', 'Economics',
                   'Electronics', 'English Language', 'English Literature', 'Environmental Science', 'Film Studies',
                    'Fine Art', 'French', 'Further Mathematics', 'Geography', 'Geology', 'German', 'Graphic Communication',
                     'History', 'Italian', 'Japanese', 'Latin', 'Law', 'Mathematics', 'Media Studies', 'Music', 'Philosophy',
                      'Photography', 'Physical Education (PE)', 'Physics', 'Politics', 'Psychology', 'Religious Studies', 'Russian',
                       'Sociology', 'Spanish', 'Statistics', 'Textiles', 'Welsh (First Language)', 'Welsh (Second Language)'
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
            results.innerHTML = `<div class="validation-errors">${validationErrors.join(" ")}</div>`;
            return;
        }

        let response, courses;
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

            courses = await response.json();
        } catch (error) {
            alert("An error occurred: " + error.message);
            hideSpinner(); // Hide spinner on error
            return;
        }

        hideSpinner(); // Hide spinner on success
        
        const results = document.getElementById('results');

        createResultsDisplay(courses, results);    
    });

    // Reset button event listener
    document.getElementById('reset-button').addEventListener('click', () => {
        localStorage.removeItem(LOCAL_STORAGE_KEY); // Remove form data from local storage
        location.reload(); // Reload the page
    });
}
