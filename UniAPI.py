from flask import Flask, jsonify, request, render_template # this is used to create the web app
from flask_restful import Api, Resource, abort # this is used to create the API

import psycopg2 as psycopg # this is used to interact with the database

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from geopy.distance import geodesic # this is used to calculate the distance between two coordinates
from geopy.geocoders import Nominatim # this is used to convert postcodes to coordinates
import time # used for testing


app = Flask(__name__,static_url_path='/static') # this creates a Flask app
api = Api(app) # this creates a Flask-RESTful API

class Database: # this class is used to interact with the database
    def __init__(self):
        self.connection = psycopg.connect("dbname=University user=postgres password=P9@ndalfos")
        self.cursor = self.connection.cursor()

    def get_course(self, course_id): # redundant but was used for the CourseResource class
        self.cursor.execute("SELECT * FROM course WHERE course_id = %s", (course_id,))
        result = self.cursor.fetchone()
        if result:
            course_data = result[:6]
            tariffs = dict(zip([desc[0] for desc in self.cursor.description[6:]], result[6:]))
        return Course(*course_data, **tariffs)
        

    def get_university(self, university_id): # redundant but was used for the UniversityResource class
        self.cursor.execute("SELECT * FROM university WHERE university_id = %s", (university_id,))
        result = self.cursor.fetchone()
        if result:
            return University(*result)
        return None
    

    def select_courses(self, search_term):
        """Finds courses matching the search term and retrieves relevant details."""
        
        # Retrieve all course names from the database
        self.cursor.execute("SELECT course_name FROM course")
        all_course_names = [row[0] for row in self.cursor.fetchall()]
        
        # Initialize TF-IDF Vectorizer
        vectorizer = TfidfVectorizer()
        # Create TF-IDF matrix for courses and the search query
        tfidf_matrix = vectorizer.fit_transform(all_course_names + [search_term])
        # Compute cosine similarity between search query and all course titles
        similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
        # Rank courses based on similarity score
        sorted_indices = similarities.argsort()[0][::-1]
        
        # Filter out courses with low similarity scores
        similar_names = [all_course_names[index] for index in sorted_indices if similarities[0][index] > 0.1]
        similarity_scores = [similarities[0][index] for index in sorted_indices if similarities[0][index] > 0.1]

        # Fetch matching course details
        placeholders = ", ".join(["%s"] * len(similar_names))
        query = f"""
            SELECT c.course_id, c.course_name, c.course_url, c.course_length, c.study_abroad, c.university_id, u.university_name, u.university_type
            FROM course c
            JOIN university u ON c.university_id = u.university_id
            WHERE c.course_name IN ({placeholders})
        """

        if not similar_names:
            return []
        self.cursor.execute(query, tuple(similar_names))
        results = self.cursor.fetchall()

        courses = []
        for row, similarity_score in zip(results, similarity_scores):
            course_id, course_name, course_url, course_length, study_abroad, university_id, university_name, university_type = row

            # Retrieve course tariffs
            self.cursor.execute("SELECT * FROM course WHERE course_id = %s", (course_id,))
            course_row = self.cursor.fetchone()
            tariffs = dict(zip([desc[0] for desc in self.cursor.description[6:]], course_row[6:]))

            # Retrieve course requirements
            self.cursor.execute("SELECT a_level_subject, grade FROM requirement WHERE course_id = %s", (course_id,))
            requirements = [{"subject": req[0], "grade": req[1]} for req in self.cursor.fetchall()]
            # Retrieve university locations
            self.cursor.execute("SELECT latitude, longitude, location_name FROM location WHERE university_id = %s", (university_id,))
            locations = [{"latitude": loc[0], "longitude": loc[1],"name": loc[2]} for loc in self.cursor.fetchall()]
            if not locations:
                locations = [{"latitude": 0, "longitude": 0, "name": ""}]  # Default value if no locations exist

            # Create University and Course objects
            university = University(university_id, university_name, "", university_type)
            university.set_locations(locations) # this sets the locations for the university
            course = Course(course_id, course_name, course_url, course_length, study_abroad, university_id, university, requirements, similarity_score, **tariffs)

            courses.append(course)

        return courses

class Course:
    def __init__(self, course_id, course_name, course_url, course_length, study_abroad, university_id, uni ,requirements, similarity_score,**tariffs):
        self.course_id = course_id #course_id is kept as a public attribute because it is used to identify the course
        self.__course_name = course_name
        self.__course_length = course_length
        self.__study_abroad = study_abroad
        self.__university_id = university_id
        self.__course_url = course_url
        self.__tariffs = tariffs # this is a dictionary containing the tariff values for the course
        self.__score = 100 # initial score will be 100
        self.__tucked_courses=[]
        self.__distance=0 # this is the distance from the user's location to the university
        self.__university=uni # this is the university object that the course belongs to
        self.__requirements = requirements # this is a list of dictionaries containing the requirements for the course
        self.__warnings = [] # this is a list of potential discrepancies between the user's grades and the course's requirements
        self.__similarity_score = similarity_score # this is the similarity score between the course name and the user's search term

    def convert_to_json(self): # this method converts the object into a dictionary that can be converted to JSON
        return {
            "course_id": self.course_id,
            "course_name": self.__course_name,
            "course_length": self.__course_length,
            "study_abroad": self.__study_abroad,
            "university_id": self.__university_id,
            "course_url": self.__course_url,
            **self.__tariffs,
            "score": round(self.__score, 2),
            "distance": self.__distance,
            "university_name": self.__university.get_university_name(), # this is the name of the university that the course belongs to
            "university_type": self.__university.get_university_type(), # this is the type of the university that the course belongs to
            "requirements": self.__requirements,
            "tucked_courses": [course.convert_to_json() for course in self.__tucked_courses], # this is a list of the courses that have been tucked into this course
            "warnings": self.__warnings 
        }

    def check_requirements(self, data): # this method checks if the user's grades meet the course's requirements

        #self.__warnings.append("This is a test warning") # this is a test warning
        possible_grades =['A*','A','B','C','D','E']
        user_grades = data.get('grades')
        user_subjects = data.get('subject')
        if not user_grades or not user_subjects and self.__requirements:
            self.__warnings.append("This course has requirements but you have not entered your grades")
            return self.__warnings



        for req in self.__requirements:
            if req['subject'] not in user_subjects:
                self.__warnings.append(f"This course requires {req['subject']}")
                continue
            if req['subject'] in user_subjects:
                grade_index = possible_grades.index(req['grade'])
                user_grade = user_grades[user_subjects.index(req['subject'])]
                user_grade_index = possible_grades.index(user_grade)

                if user_grade_index > grade_index:
                    self.__warnings.append(f"This course requires {req['grade']} in {req['subject']} but you have {user_grade}")

        
        return self.__warnings





    def calculate_score(self, data):
        # calculate scores
        distance_score = self.__calculate_distance_score(data)
        tariff_score = self.__calculate_tariff_score(data)
        university_type_score = self.__calculate_university_type_score(data)
        year_abroad_score = self.__calculate_year_abroad_score(data)
        course_length_score = self.__calculate_course_length_score(data)
        similarity_score = self.__similarity_score # use the stored similarity score

        # Dynamic weights based on user preferences
        distance_weight = float(data.get('distance_weight', 50))
        tariff_weight = float(data.get('tariff_weight', 100))
        university_type_weight = float(data.get('university_type_weight', 50))
        year_abroad_weight = float(data.get('year_abroad_weight', 50))
        course_length_weight = float(data.get('course_length_weight', 50))
        similarity_weight = 1 # you can adjust this weight as needed

        # Calculate final score
        total_weight = distance_weight + tariff_weight + university_type_weight + year_abroad_weight + course_length_weight + similarity_weight
        if total_weight == 0:
            final_score = 0
        else:
            final_score = 100 * (
                distance_score * distance_weight +
                tariff_score * tariff_weight +
                university_type_score * university_type_weight +
                year_abroad_score * year_abroad_weight +
                course_length_score * course_length_weight +
                similarity_score * similarity_weight
            ) / total_weight

        self.__score = final_score
        return final_score

    def __calculate_distance_score(self, data):
        #print(self.__distance)
        if data.get('postcode') and data.get('preferred_distance'): # check if the user has entered a postcode and a preferred distance
            self.__calculate_distance(data)
            if self.__distance == 0:
                distance_score = 0
            else:
                preferred_distance = data.get('preferred_distance') # retrieve the user's preferred distance from the data
                #print(preferred_distance)
                if preferred_distance == "more than 500" and self.__distance > 500:
                    distance_score = 1
                elif preferred_distance == "400-500" and 400 <= self.__distance <= 500:
                    distance_score = 1
                elif preferred_distance == "300-400" and 300 <= self.__distance <= 400:
                    distance_score = 1
                elif preferred_distance == "200-300" and 200 <= self.__distance <= 300:
                    distance_score = 1
                elif preferred_distance == "100-200" and 100 <= self.__distance <= 200:
                    distance_score = 1
                elif preferred_distance == "Less than 100" and self.__distance < 100:
                    distance_score = 1
                elif preferred_distance=="none":
                    distance_score = 0
                else:
                    distance_score = 0.5
        else:
            distance_score = 0 
        return distance_score


    def __calculate_tariff_score(self, data):
        if data.get('grades') and any(self.__tariffs.values()):  #check if the user has entered grades and if the course has tariff values
            ucas_points = self.__convert_UCAS_points(data['grades'])
            categories= ["001","048","064","080","096","112","128","144","160","176","192","208","224","240"]# this list contains the categories of UCAS points
            tariff_value = None
            for i in range(len(categories) - 1): # iterate through the categories to find the correct category for the user's UCAS points
                if ucas_points < int(categories[i+1]):
                    start_index = max(i-1, 0)
                    end_index = min(i+2, len(categories))
                    tariff_values = [self.__tariffs.get('tariff_'+str(categories[j])) for j in range(start_index, end_index)] # this list contains the tariff values of the categories surrounding the user's UCAS points
                    tariff_value = sum(tariff_values) / len(tariff_values) # this calculates the average tariff value of the surrounding categories
                    break # break out of the loop once the correct category is found
            if tariff_value is None:
                tariff_score = 0.5

            elif tariff_value > 224:
                # Handle case where ucas_points is in the highest category
                tariff_value = sum([self.__tariffs.get('tariff_'+categories[i]) for i in range(-3, 0)]) / 3
                if tariff_value:
                    tariff_score = tariff_value / 100
                else:
                    tariff_score = 0.25
            else:
                tariff_score = tariff_value / 100
        else:
            tariff_score = 0.05 # score when the user has not entered grades or the course has no tariff values
        return tariff_score

    
    def __calculate_distance(self, data):
        
        user_location = data.get("coords") #retrieve the user's location from the data

        if not user_location:
            self.__distance = 0
            return
        university_coords = self.__university.get_university_coordinates()
        #print(university_coords)
        user_coords = (user_location.latitude, user_location.longitude)

        self.__distance = geodesic(user_coords, university_coords).km
        self.__distance = round(self.__distance, 2)


    def __calculate_year_abroad_score(self, data):
        if data['year_abroad'] != self.__study_abroad and data['year_abroad']==False: # score if the user doesnt want to study abroad but the course offers it
            year_abroad_score = 0.5
        elif data['year_abroad'] == self.__study_abroad and data['year_abroad']==True: # score if the user wants to study abroad and the course offers it
            year_abroad_score = 1
        elif data['year_abroad'] == self.__study_abroad and data['year_abroad']==False: # score if the user doesnt want to study abroad and the course doesnt offer it
            year_abroad_score = 1
        else:
            year_abroad_score = 0.25 # score when user wants to study abroad but course does not offer it
        return year_abroad_score
    
    def __calculate_course_length_score(self, data):
        if data['course_length'] != self.__course_length: # score if the user's preferred course length is different from the course's length
            course_length_score = 0.75
        else:
            course_length_score = 1
        return course_length_score
    
    def __calculate_university_type_score(self, data):
        if data.get('university_type') != self.__university.get_university_type(): # score if the user's preferred university type is different from the course's university type
            university_type_score = 0.5
        else:
            university_type_score = 1
        return university_type_score
            
    def __convert_UCAS_points(self, grades):
        total_points = 0
        scoring_dictionary = {"A*": 56, "A": 48, "B": 40, "C": 32, "D": 24, "E": 16,"":0} # this dictionary maps a-level grades to their UCAS points
        for grade in grades:
            total_points += scoring_dictionary[grade]
        return total_points

    
    def __alter_score(self, multiplier): # this method alters the score of the course by multiplying it by a given value
        self.__score *= multiplier # i dont use this anymore
    def display_score(self): # this method returns the score of the course
        return self.__score
    def get_university_id(self):
        return self.__university_id
    
    def tuck_course(self,other): # this method tucks another course into the course
        self.__tucked_courses.append(other)
    



class University:
    def __init__(self, university_id, university_name, university_url, university_type): # this is the constructor for the University class
        self.university_id = university_id
        self.__university_name = university_name
        self.__university_url = university_url
        self.__university_type = university_type
        self.__locations =[] # this is a list of dictionaries containing the locations of the university

    def convert_to_json(self): # this method converts the object into a dictionary that can be converted to JSON
        return {
            "university_id": self.university_id,
            "university_name": self.__university_name,
            "university_url": self.__university_url,
            "university_type": self.__university_type,
        }
    
    def set_locations(self, locations): # this method sets the locations for the university
        self.__locations = locations


    def get_university_type(self):
        return self.__university_type
    
    def get_university_coordinates(self):
        for location in self.__locations:
            if "main" in location["name"].lower() or self.__university_name.split()[-1].lower() in location["name"].lower():
                return (location["latitude"], location["longitude"])

        return (self.__locations[0]["latitude"], self.__locations[0]["longitude"])

    def get_university_name(self):
        return self.__university_name

class CourseResource(Resource): # this is the class that is used to get course details it is not currently used
    def get(self, course_id):
        db = Database()
        course = db.get_course(course_id)
        if course:
            return jsonify(course.convert_to_json())
        abort(404, message="Course not found")


class UniversityResource(Resource): # this is the class that is used to get university details it is not currently used
    def get(self, university_id):
        db = Database()
        university = db.get_university(university_id)
        if university:
            return jsonify(university.convert_to_json())
        abort(404, message="University not found")

class CourseSearchResource(Resource): # this is the class that is used to search for courses
    def __init__(self):
        self.db=Database()


    def get(self): # this is the get method that is not currently used
        course_name = request.args.get('course_name')
        if not course_name:
            abort(400, message="Course name is required")
        
        courses = self.db.search_courses(course_name)
        if courses:
            return jsonify([course.convert_to_json() for course in courses])
        abort(404, message="No courses found")
    
    def post(self): # this is the method that is called when a POST request is made to the endpoint it is the main method that is called when the user searches for courses

        data = request.get_json()
        print(data)
        if not data or 'search_term' not in data:
            abort(400, message="No search term provided")
        
        courses = self.db.select_courses(data['search_term']) 


        unique_courses = {course.course_id: course for course in courses}.values()

        postcode = data['postcode']
        geolocator=Nominatim(user_agent="uniapi")
        data["coords"]= geolocator.geocode(postcode, timeout=10)

        university_courses = {}
        for course in unique_courses:
            course.calculate_score(data)
            course.check_requirements(data)
            university_id = course.get_university_id()# this is for tucking courses
            if university_id not in university_courses:
                university_courses[university_id] = []
            university_courses[university_id].append(course)



        final_courses = []
        for courses in university_courses.values():
            highest_scoring_course = max(courses, key=lambda x: x.display_score())
            for course in courses:
                if course != highest_scoring_course:
                    highest_scoring_course.tuck_course(course)
            final_courses.append(highest_scoring_course)

        #t=time.time()
        #sorted_courses2 = sorted(final_courses, key=lambda x: x.display_score(), reverse=True)
        #print(time.time()-t)
        #t=time.time()
        sorted_courses = self.merge_sort(final_courses)[::-1] # the merge sort is about 5x slower than the built-in sort
        #print(time.time()-t)
        


        if sorted_courses:
            return jsonify([course.convert_to_json() for course in sorted_courses[:100]])

        abort(404, message="No courses found")



    def merge_sort(self, unsorted_courses):
        if len(unsorted_courses) <= 1:
            return unsorted_courses
        else:
            mid = len(unsorted_courses) // 2
            left = unsorted_courses[:mid]
            right = unsorted_courses[mid:]

            left = self.merge_sort(left) #calls itself recursively to sort the left side
            right = self.merge_sort(right) #calls itself recursively to sort the right side

            return self.merge(left, right) #merges the left and right sides

    
    def merge(self, left, right): # this method merges the left and right sides of the list
        result = []
        left_index = 0
        right_index = 0

        while left_index < len(left) and right_index < len(right):
            if left[left_index].display_score() < right[right_index].display_score():# this retrieves the score of the course and compares it
                result.append(left[left_index])
                left_index += 1
            else:
                result.append(right[right_index])
                right_index += 1

        result += left[left_index:]
        result += right[right_index:]

        return result # returns the merged list




api.add_resource(CourseResource, "/course/<string:course_id>")
api.add_resource(UniversityResource, "/university/<string:university_id>")


api.add_resource(CourseSearchResource, "/courses/search")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)
