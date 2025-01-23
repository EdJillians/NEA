from flask import Flask, jsonify, request, render_template
from flask_restful import Api, Resource, abort
import psycopg2 as psycopg
from difflib import get_close_matches

from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import time


app = Flask(__name__,static_url_path='/static') # this creates a Flask app
api = Api(app) # this creates a Flask-RESTful API

class Database: # this class is used to interact with the database
    def __init__(self):
        self.connection = psycopg.connect("dbname=University user=postgres password=P9@ndalfos")
        self.cursor = self.connection.cursor()

    def get_course(self, course_id): # redundant
        self.cursor.execute("SELECT * FROM course WHERE course_id = %s", (course_id,))
        result = self.cursor.fetchone()
        if result:
            course_data = result[:6]
            tariffs = dict(zip([desc[0] for desc in self.cursor.description[6:]], result[6:]))
        return Course(*course_data, **tariffs)
        

    def get_university(self, university_id): 
        self.cursor.execute("SELECT * FROM university WHERE university_id = %s", (university_id,))
        result = self.cursor.fetchone()
        if result:
            return University(*result)
        return None

    # def search_courses(self, course_name, course_length=None, limit=5): # shouldnt be used
    #     if course_length:
    #         self.cursor.execute("SELECT * FROM course WHERE course_name LIKE %s AND course_length = %s LIMIT %s", ('%' + course_name + '%', course_length, limit))
    #     else:
    #         self.cursor.execute("SELECT * FROM course WHERE course_name LIKE %s LIMIT %s", ('%' + course_name + '%', limit))
    #     results = self.cursor.fetchall()

    #     courses = []
    #     for result in results:
    #         course_data = result[:6]
    #         tariffs = dict(zip([desc[0] for desc in self.cursor.description[6:]], result[6:]))
    #         courses.append(Course(*course_data, **tariffs))
        
    #     return courses if results else []
    # def __del__(self):
    #     self.connection.close()
    
    
    def select_courses(self, search_term): # selects possible relevant courses from the database
        courses = []
        # Fetch all course names from the database
        self.cursor.execute("SELECT course_name FROM course")
        all_course_names = [row[0] for row in self.cursor.fetchall()] # this list comprehension extracts the course names from the fetched rows
        # Find similar course names
        similar_names = get_close_matches(search_term, all_course_names, cutoff=0.6, n=300) # selects up to 300 closest matches from all course names
        # Create searches for these course names

        for name in similar_names: # iterate through the similar course names
            self.cursor.execute(""" 
            SELECT course.*, university.*
            FROM course
            JOIN university ON course.university_id = university.university_id
            WHERE course.course_name = %s
            """, (name,)) # this query selects the course and university data for the course with the current name
            results = self.cursor.fetchall()
            course_description = self.cursor.description
            self.cursor.execute("""
            SELECT grade, a_level_subject 
            FROM requirement
            WHERE requirement.course_id = %s
            """, (results[0][0],)) # this query selects the requirements for the course with the current name
            requirement_results = self.cursor.fetchall()
            requirements = [{"grade": req[0], "a_level_subject": req[1]} for req in requirement_results]
            for result in results:
                #print(result)
                course_data = result[:6]  # course_data is a tuple of the first 6 elements of the retrieved row
                #print(course_data)
                tariffs = dict(zip([desc[0] for desc in course_description[6:20]], result[6:20]))  # this converts the tariffs columns into a dictionary
                #print(course_description)
                #print(tariffs)
                university_data = result[20:26]  # university_data is the next 6 elements of the retrieved row
                #print(university_data)
                university = University(*university_data)  # instantiate a University object
                courses.append(Course(*course_data, uni=university, requirements=requirements, **tariffs))  # instantiate a Course object with the course_data tuple, the university object, the requirements, and the tariffs dictionary
        return courses



class Course:
    def __init__(self, course_id, course_name, course_url, course_length, study_abroad, university_id, uni ,requirements,**tariffs):
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

    def convert_to_json(self): # this method converts the object into a dictionary that can be converted to JSON
        return {
            "course_id": self.course_id,
            "course_name": self.__course_name,
            "course_length": self.__course_length,
            "study_abroad": self.__study_abroad,
            "university_id": self.__university_id,
            "course_url": self.__course_url,
            **self.__tariffs,
            "score": self.__score,
            "distance": self.__distance,
            "university_name": self.__university.get_university_name(),
            "university_type": self.__university.get_university_type()
        }





    def calculate_score(self, data):
        # Normalize scores
        distance_score = self.__calculate_distance_score(data)
        tariff_score = self.__calculate_tariff_score(data) 
        university_type_score = self.__calculate_university_type_score(data) 
        year_abroad_score = self.__calculate_year_abroad_score(data) 
        course_length_score = self.__calculate_course_length_score(data) 

        # Dynamic weights based on user preferences
        distance_weight = data.get('distance_weight', 50)
        tariff_weight = data.get('tariff_weight', 100)
        university_type_weight = data.get('university_type_weight', 50)
        year_abroad_weight = data.get('year_abroad_weight', 50)
        course_length_weight = data.get('course_length_weight', 50)

        # Calculate final score
        final_score = (
            distance_score * distance_weight +
            tariff_score * tariff_weight +
            university_type_score * university_type_weight +
            year_abroad_score * year_abroad_weight +
            course_length_score * course_length_weight
        )# / (distance_weight + tariff_weight + university_type_weight + year_abroad_weight + course_length_weight)

        self.__score = final_score
        return final_score

    def __calculate_distance_score(self, data):
        if data.get('postcode'):
            self.__calculate_distance(data)
            if self.__distance == "Invalid postcode":
                distance_score = 0
            else:
                preferred_distance = data.get('preferred_distance')
                #print(preferred_distance)
                if preferred_distance == "More than 500" and self.__distance > 500:
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
            elif tariff_value < 240:
                tariff_score = tariff_value / 100
            else:
                # Handle case where ucas_points is greater than or equal to the highest category value
                tariff_value = sum([self.__tariffs.get('tariff_'+categories[i]) for i in range(-3, 0)]) / 3
                if tariff_value:
                    tariff_score = tariff_value / 100
                else:
                    tariff_score = 0.25
        else:
            tariff_score = 0.05 # score when the user has not entered grades or the course has no tariff values
        return tariff_score

    
    def __calculate_distance(self, data):
        
        location = data.get("coords")

        if not location:
            self.__distance = "Invalid postcode"
            return
        
        university_coords = self.__university.get_university_coordinates()
        user_coords = (location.latitude, location.longitude)

        

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
        self.__score *= multiplier 
    def display_score(self): # this method returns the score of the course
        return self.__score
    def get_university_id(self):
        return self.__university_id
    
    def tuck_course(self,other):
        self.__tucked_courses.append(other)
    

class University:
    def __init__(self, university_id, university_name, university_url, university_type, longitude, latitude):
        self.university_id = university_id
        self.__university_name = university_name
        self.__university_url = university_url
        self.__university_type = university_type
        self.__longitude = longitude
        self.__latitude = latitude

    def convert_to_json(self):
        return {
            "university_id": self.university_id,
            "university_name": self.__university_name,
            "university_url": self.__university_url,
            "university_type": self.__university_type,
            "longitude": self.__longitude,
            "latitude": self.__latitude
        }
    def get_university_type(self):
        return self.__university_type
    def get_university_coordinates(self):
        return (self.__latitude, self.__longitude)
    def get_university_name(self):
        return self.__university_name

class CourseResource(Resource):
    def get(self, course_id):
        db = Database()
        course = db.get_course(course_id)
        if course:
            return jsonify(course.convert_to_json())
        abort(404, message="Course not found")


class UniversityResource(Resource):
    def get(self, university_id):
        db = Database()
        university = db.get_university(university_id)
        if university:
            return jsonify(university.convert_to_json())
        abort(404, message="University not found")

class CourseSearchResource(Resource):
    def __init__(self):
        self.db=Database()



    def get(self):
        course_name = request.args.get('course_name')
        if not course_name:
            abort(400, message="Course name is required")
        
        courses = self.db.search_courses(course_name)
        if courses:
            return jsonify([course.convert_to_json() for course in courses])
        abort(404, message="No courses found")
    
    def post(self):

        data = request.get_json()
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

        sorted_courses = sorted(final_courses, key=lambda x: x.display_score(), reverse=True)


        if sorted_courses:
            return jsonify([course.convert_to_json() for course in sorted_courses[:100]])

        abort(404, message="No courses found")



    def merge_sort(self,unsorted_courses):
        pass



api.add_resource(CourseResource, "/course/<string:course_id>")
api.add_resource(UniversityResource, "/university/<string:university_id>")
api.add_resource(CourseSearchResource, "/courses/search")

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
