from flask import Flask, jsonify, request, render_template
from flask_restful import Api, Resource, abort
import psycopg2 as psycopg
from difflib import get_close_matches
import random




app = Flask(__name__,static_url_path='/static')
api = Api(app)

class Database:
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
        
        



    def get_university(self, university_id): # redundant
        self.cursor.execute("SELECT * FROM university WHERE university_id = %s", (university_id,))
        result = self.cursor.fetchone()
        if result:
            return University(*result)
        return None

    def search_courses(self, course_name, course_length=None, limit=5): # shouldnt be used
        if course_length:
            self.cursor.execute("SELECT * FROM course WHERE course_name LIKE %s AND course_length = %s LIMIT %s", ('%' + course_name + '%', course_length, limit))
        else:
            self.cursor.execute("SELECT * FROM course WHERE course_name LIKE %s LIMIT %s", ('%' + course_name + '%', limit))
        results = self.cursor.fetchall()

        courses = []
        for result in results:
            course_data = result[:6]
            tariffs = dict(zip([desc[0] for desc in self.cursor.description[6:]], result[6:]))
            courses.append(Course(*course_data, **tariffs))
        
        return courses if results else []
    def __del__(self):
        self.connection.close()
    
    
    def select_courses(self, search_term): # selects possible relevant courses from the database
        courses = []
        # Fetch all course names from the database
        self.cursor.execute("SELECT course_name FROM course")
        all_course_names = [row[0] for row in self.cursor.fetchall()]
        # Find similar course names
        similar_names = get_close_matches(search_term, all_course_names, cutoff=0.7, n=100) # selects the top 100 closest matches from all course names
        # Create searches for these course names
        for name in similar_names:
            self.cursor.execute("SELECT * FROM course WHERE course_name = %s", (name,))
            results = self.cursor.fetchall()
            for result in results:
                course_data = result[:6] # course_data is a tuple of the first 6 elements of the retrieved row
                tariffs = dict(zip([desc[0] for desc in self.cursor.description[6:]], result[6:])) # this converts the tariffs columns into a dictionary
                courses.append(Course(*course_data, **tariffs)) # this instantiates a Course object with the course_data tuple and the tariffs dictionary
        return courses



class Course:
    def __init__(self, course_id, course_name, course_url, course_length, study_abroad, university_id, **tariffs):
        self.course_id = course_id
        self.__course_name = course_name
        self.__course_length = course_length
        self.__study_abroad = study_abroad
        self.__university_id = university_id
        self.__course_url = course_url
        self.__tariffs = tariffs
        self.__score = 100 # initial score will be 100

    def convert_to_json(self):
        return {
            "course_id": self.course_id,
            "course_name": self.__course_name,
            "course_length": self.__course_length,
            "study_abroad": self.__study_abroad,
            "university_id": self.__university_id,
            "course_url": self.__course_url,
            **self.__tariffs,
            "score": self.__score
        }

    def calculate_score(self, data):
        #print(data)
        if data['year_abroad'] != self.__study_abroad:
            self.__alter_score(0.5)

        if data['course_length'] != self.__course_length:
            self.__alter_score(0.5)
        if data.get('grades') and any(self.__tariffs.values()):  
            ucas_points = self.__convert_UCAS_points(data['grades'])
            #print(ucas_points)
            categories= ["001","048","064","080","096","112","128","144","160","176","192","208","224","240"]
            tariff_value = None
            for i in range(len(categories) - 1):
                if ucas_points < int(categories[i+1]):
                    #print(categories[i])
                    start_index = max(i-1, 0)
                    end_index = min(i+2, len(categories))
                    tariff_values = [self.__tariffs.get('tariff_'+str(categories[j])) for j in range(start_index, end_index)]
                    #print(tariff_values, self.__tariffs)
                    tariff_value = sum(tariff_values) / len(tariff_values)
                    break
            if tariff_value!=None:
                self.__alter_score(tariff_value / 25) #The 25 can be adjusted to change the weighting of the tariff in the overall score
            else:
                # Handle case where ucas_points is greater than or equal to the highest category value
                tariff_value = sum([self.__tariffs.get('tariff_'+categories[i]) for i in range(-3, 0)]) / 3
                if tariff_value:
                    self.__alter_score(tariff_value / 25)
            
        
            
    def __convert_UCAS_points(self, grades):
        total_points = 0
        scoring_dictionary = {"A*": 56, "A": 48, "B": 40, "C": 32, "D": 24, "E": 16}
        for grade in grades:
            total_points += scoring_dictionary[grade]
        return total_points

    
    def __alter_score(self, multiplier):
        self.__score *= multiplier
    def display_score(self):
        return self.__score
    

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
    def get(self):
        course_name = request.args.get('course_name')
        if not course_name:
            abort(400, message="Course name is required")
        db = Database()
        courses = db.search_courses(course_name)
        if courses:
            return jsonify([course.convert_to_json() for course in courses])
        abort(404, message="No courses found")
    
    def post(self):
        data = request.get_json()
        if not data or 'search_term' not in data:
            abort(400, message="No search term provided")
        db = Database()
        courses = db.select_courses(data['search_term'])

        unique_courses = {course.course_id: course for course in courses}.values()

        for course in unique_courses:
            course.calculate_score(data)
        #    print(course.score)
    
        sorted_courses = sorted(unique_courses, key=lambda x: x.display_score(), reverse=True) # I could write a merge sort for this
        
        if sorted_courses:
            return jsonify([course.convert_to_json() for course in sorted_courses[:50]])
        abort(404, message="No courses found")



api.add_resource(CourseResource, "/course/<string:course_id>")
api.add_resource(UniversityResource, "/university/<string:university_id>")
api.add_resource(CourseSearchResource, "/courses/search")

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
