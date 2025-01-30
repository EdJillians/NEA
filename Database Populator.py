import psycopg2 as psycopg  # imports the psycopg2 module to connect to the database
import csv # imports the csv module to read the csv files
import pandas as pd 
from psycopg2 import sql

NEA_FOLDER_PATH = 'c:/Users/edwar/OneDrive/!Computer_Science/NEA/'

def main():
    # create_database()
    with psycopg.connect("dbname=University user=postgres password=P9@ndalfos") as conn: # connect to the database
        drop_tables(conn)
        create_tables(conn)
        university_csv = clean_csv(f'{NEA_FOLDER_PATH}dataset/INSTITUTION.csv', 'university')
        course_csv = clean_csv(f'{NEA_FOLDER_PATH}dataset/KISCOURSE.csv', 'course')
        location_csv = clean_csv(f'{NEA_FOLDER_PATH}dataset/LOCATION.csv', 'location')
        load_csv(conn, university_csv, 'university')
        load_csv(conn, course_csv, 'course')
        load_csv(conn, location_csv, 'location')
        populate_requirement(conn)
        alter_university_types(conn)

    pass

def create_database():
    """
    Creates a PostgreSQL database named 'University'.
    Requires a PostgreSQL server to be running and accessible.
    """
    connection = None
    cursor = None
    try:
        # Connect to the default PostgreSQL database
        connection = psycopg.connect(
            dbname="postgres",  # Default database
            user="postgres",  # Replace with your username
            password="P9@ndalfos",  # Replace with your password
            host="localhost",  # Replace with your host (e.g., localhost or an IP address)
            port="5432"  # Default PostgreSQL port
        )
        connection.autocommit = True  # Allow database creation outside of a transaction

        # Create a cursor object
        cursor = connection.cursor()

        # Create the University database
        cursor.execute(
            sql.SQL("CREATE DATABASE {};").format(
                sql.Identifier("University")
            )
        )

        print("Database 'University' created successfully.")

    except psycopg.Error as e:
        print(f"Error creating database: {e}")

    finally:
        # Clean up by closing the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()




def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE "requirement"(
            "requirement_id" BIGSERIAL NOT NULL,
            "course_id" VARCHAR(255) NOT NULL,
            "grade" VARCHAR(255) NOT NULL,
            "a_level_subject" VARCHAR(255) NOT NULL
        );
        ALTER TABLE
            "requirement" ADD PRIMARY KEY("requirement_id");

        CREATE TABLE "university"(
            "university_id" VARCHAR(255) NOT NULL,
            "university_name" VARCHAR(255) NOT NULL,
            "university_url" VARCHAR(255),
            "university_type" VARCHAR(255) NOT NULL
        );
        ALTER TABLE
            "university" ADD PRIMARY KEY("university_id");

        CREATE TABLE "location"(
            "location_id" VARCHAR(255) NOT NULL,
            "university_id" VARCHAR(255) NOT NULL,
            "location_name" VARCHAR(255) NOT NULL,
            "longitude" FLOAT(53),
            "latitude" FLOAT(53)
        );
        ALTER TABLE
            "location" ADD PRIMARY KEY("location_id");
                                      
        

        CREATE TABLE "course"(
            "course_id" VARCHAR(255) NOT NULL,
            "course_name" VARCHAR(255) NOT NULL,
            "course_url" VARCHAR(255) NOT NULL,
            "course_length" FLOAT,
            "study_abroad" BOOLEAN NOT NULL,
            "university_id" VARCHAR(255) NOT NULL,
            "tariff_001" FLOAT,
            "tariff_048" FLOAT,
            "tariff_064" FLOAT,
            "tariff_080" FLOAT,
            "tariff_096" FLOAT,
            "tariff_112" FLOAT,
            "tariff_128" FLOAT,
            "tariff_144" FLOAT,
            "tariff_160" FLOAT,
            "tariff_176" FLOAT,
            "tariff_192" FLOAT,
            "tariff_208" FLOAT,
            "tariff_224" FLOAT,
            "tariff_240" FLOAT
        );
        ALTER TABLE
            "course" ADD PRIMARY KEY("course_id");

        ALTER TABLE
            "course" ADD CONSTRAINT "course_university_id_foreign" FOREIGN KEY("university_id") REFERENCES "university"("university_id");

        ALTER TABLE
            "requirement" ADD CONSTRAINT "requirement_course_id_foreign" FOREIGN KEY("course_id") REFERENCES "course"("course_id");
        """)
        conn.commit()


def load_csv(conn, file_path, table_name):
    with conn.cursor() as cur:
        with open(file_path, 'r') as f:
            reader = csv.reader(f) # read the csv file
            headers = next(reader) # get the headers of the csv file
            columns = ', '.join(headers) # join the headers together to form the columns of the table
            placeholders = ', '.join(['%s'] * len(headers)) # create the placeholders for the values to be inserted
            for row in reader: # iterate through the rows of the csv file
                try:
                    row = [None if value == '' else value for value in row]
                    cur.execute(
                        f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})",
                        row
                    )
                    conn.commit()
                except Exception as e:
                    #print(f"Error inserting row {row}: {type(e).__name__} - {e}")
                    conn.rollback()

def clean_csv(file_path, table_name): # this function cleans the csv files and returns the cleaned csv files
    if table_name == 'university':
        file1 = f'{NEA_FOLDER_PATH}dataset/INSTITUTION.csv'
        #file2 = f'{NEA_FOLDER_PATH}dataset/LOCATION.csv'
        df1 = pd.read_csv(file1)
        #df2 = pd.read_csv(file2)
        df1['TYPE'] = 'campus' # this sets all universities to campus type as there is no data for this
        #merged_df = pd.merge(df1, df2, on='UKPRN', how='left')
        columns_to_keep1 = [
            'UKPRN', 'LEGAL_NAME', 'PROVURL', 'TYPE'
        ]
        cleaned_df = df1[columns_to_keep1]
        cleaned_df = cleaned_df.dropna(subset=['UKPRN'])
        cleaned_df = cleaned_df.drop_duplicates(subset=['UKPRN'], keep='first')
        cleaned_df = cleaned_df.rename(columns={
            'UKPRN': 'university_id',
            'LEGAL_NAME': 'university_name',
            'PROVURL': 'university_url',
            'TYPE': 'university_type',
        })
        output_file = f'{NEA_FOLDER_PATH}cleaned_UNIVERSITY.csv'
        cleaned_df.to_csv(output_file, index=False)
        return output_file
    

    elif table_name == 'location':
        file5 = f'{NEA_FOLDER_PATH}dataset/LOCATION.csv'
        df5 = pd.read_csv(file5)
        columns_to_keep2 = ['UKPRN','LOCNAME', 'LONGITUDE', 'LATITUDE']
        cleaned_df = df5[columns_to_keep2]
        cleaned_df = cleaned_df.dropna(subset=['UKPRN'])
        cleaned_df["location_id"]=cleaned_df.apply(lambda row: f"{row['UKPRN']}_{row['LOCNAME']}", axis=1)
        cleaned_df = cleaned_df.rename(columns={
            'UKPRN': 'university_id',
            'LOCNAME': 'location_name',
            'LONGITUDE': 'longitude',
            'LATITUDE': 'latitude',
        })
        output_file = f'{NEA_FOLDER_PATH}cleaned_LOCATION.csv'
        cleaned_df.to_csv(output_file, index=False)
        return output_file



    elif table_name == 'course':
        file3 = f'{NEA_FOLDER_PATH}dataset/KISCOURSE.csv'
        file4 = f'{NEA_FOLDER_PATH}dataset/TARIFF.csv'
        df3 = pd.read_csv(file3)
        df4 = pd.read_csv(file4)
        merged_df = pd.merge(df3, df4, on=['KISCOURSEID', 'UKPRN'], how='inner')
        columns_to_keep = [
            'KISCOURSEID', 'TITLE', 'CRSEURL', 'NUMSTAGE', 'YEARABROAD', 'UKPRN',
            'T001', 'T048', 'T064', 'T080', 'T096', 'T112', 'T128', 'T144', 'T160', 'T176', 'T192', 'T208', 'T224', 'T240'
        ]
        cleaned_df = merged_df[columns_to_keep]
        cleaned_df['YEARABROAD'] = cleaned_df['YEARABROAD'].replace({2: 1}).fillna(0)
        cleaned_df = cleaned_df.dropna(subset=['KISCOURSEID'])
        cleaned_df['KISCOURSEID'] = cleaned_df.apply(lambda row: f"{row['KISCOURSEID']}_{row['UKPRN']}", axis=1)
        cleaned_df['KISCOURSEID'] = cleaned_df.apply(lambda row: f"{row['KISCOURSEID']}_{row['UKPRN']}_{row['NUMSTAGE']}_{str(row['YEARABROAD'])[0]}", axis=1)
        cleaned_df = cleaned_df.rename(columns={
            'KISCOURSEID': 'course_id',
            'TITLE': 'course_name',
            'CRSEURL': 'course_url',
            'NUMSTAGE': 'course_length',
            'YEARABROAD': 'study_abroad',
            'UKPRN': 'university_id',
            'T001': 'tariff_001',
            'T048': 'tariff_048',
            'T064': 'tariff_064',
            'T080': 'tariff_080',
            'T096': 'tariff_096',
            'T112': 'tariff_112',
            'T128': 'tariff_128',
            'T144': 'tariff_144',
            'T160': 'tariff_160',
            'T176': 'tariff_176',
            'T192': 'tariff_192',
            'T208': 'tariff_208',
            'T224': 'tariff_224',
            'T240': 'tariff_240'
        })
        cleaned_df['study_abroad'] = cleaned_df['study_abroad'].astype(bool)
        output_file = f'{NEA_FOLDER_PATH}cleaned_COURSE.csv'
        cleaned_df.to_csv(output_file, index=False)
        return output_file


def drop_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
        DROP TABLE IF EXISTS "requirement" CASCADE;
        DROP TABLE IF EXISTS "university" CASCADE;
        DROP TABLE IF EXISTS "course" CASCADE;
        DROP TABLE IF EXISTS "location" CASCADE;
        """)
        conn.commit()

def populate_requirement(conn):
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO requirement (course_id, grade, a_level_subject) VALUES ('2571192_10007798_10007798_4.0_1', 'A', 'Mathematics');
        """)
        # grades=['A*','A', 'B', 'C', 'D',]
        # counter=0
        # while True:
        #     cur.execute("""
        #                 INSERT INTO requirement (SELECT course_id FROM course WHERE course_name = 'Mathematics' LIMIT 1, grades[counter], 'Mathematics')
        #                 """)
        #     counter+=1
        conn.commit()


def alter_university_types(conn):
    with conn.cursor() as cur:
        cur.execute("""
        UPDATE "university"
        SET university_type = 'collegic'
        WHERE university_name IN ('University of Cambridge', 'University of Oxford', 'University of Durham');
        """)
        cur.execute("""
        UPDATE University
        SET university_type = 'city'
        WHERE university_name IN ('University of Bristol', 'The University of Leeds','University College London')
        """)
        cur.execute("""
        UPDATE University
        SET university_type = 'distance'
        WHERE university_name IN ('The Open University','Arden University Limited')
        """)       


        conn.commit()


if __name__ == "__main__":
    main()
