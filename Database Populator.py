import psycopg2 as psycopg
import csv
import pandas as pd

NEA_FOLDER_PATH = 'c:/Users/edwar/OneDrive/!Computer_Science/NEA/'

def main():
    # drop_tables()
    # create_tables()
    # university_csv= clean_csv(f'{NEA_FOLDER_PATH}dataset/INSTITUTION.csv', 'university')
    # course_csv=clean_csv(f'{NEA_FOLDER_PATH}dataset/KISCOURSE.csv', 'course')
    # load_csv(university_csv, 'university')
    # load_csv(course_csv, 'course')
    populate_requirement()
    

def create_tables():
    with psycopg.connect("dbname=University user=postgres password=P9@ndalfos") as conn:
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
                "university_type" VARCHAR(255) NOT NULL,
                "longitude" FLOAT(53),
                "latitude" FLOAT(53)
            );
            ALTER TABLE
                "university" ADD PRIMARY KEY("university_id");

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

def load_csv(file_path, table_name):
    with psycopg.connect("dbname=University user=postgres password=P9@ndalfos") as conn:
        with conn.cursor() as cur:
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                headers = next(reader)
                columns = ', '.join(headers)
                placeholders = ', '.join(['%s'] * len(headers))
                for row in reader:
                    try:
                        row = [None if value == '' else value for value in row]
                        cur.execute(
                            f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})",
                            row
                        )
                        conn.commit()
                    except Exception as e:
                        print(f"Error inserting row {row}: {type(e).__name__} - {e}")
                        conn.rollback()

def clean_csv(file_path, table_name):
    if table_name == 'university':
        file1 = f'{NEA_FOLDER_PATH}dataset/INSTITUTION.csv'
        file2 = f'{NEA_FOLDER_PATH}dataset/LOCATION.csv'
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
        df1['TYPE'] = 'campus'
        merged_df = pd.merge(df1, df2, on='UKPRN', how='left')
        columns_to_keep1 = [
            'UKPRN', 'LEGAL_NAME', 'PROVURL', 'TYPE', 'LATITUDE', 'LONGITUDE'
        ]
        cleaned_df = merged_df[columns_to_keep1]
        cleaned_df = cleaned_df.dropna(subset=['UKPRN'])
        cleaned_df = cleaned_df.drop_duplicates(subset=['UKPRN'], keep='first')
        cleaned_df = cleaned_df.rename(columns={
            'UKPRN': 'university_id',
            'LEGAL_NAME': 'university_name',
            'PROVURL': 'university_url',
            'TYPE': 'university_type',
            'LATITUDE': 'latitude',
            'LONGITUDE': 'longitude'
        })
        output_file = f'{NEA_FOLDER_PATH}cleaned_UNIVERSITY.csv'
        cleaned_df.to_csv(output_file, index=False)
        return output_file

    elif table_name == 'course':
        file3 = f'{NEA_FOLDER_PATH}dataset/KISCOURSE.csv'
        file4 = f'{NEA_FOLDER_PATH}dataset/TARIFF.csv'
        df3 = pd.read_csv(file3)
        df4 = pd.read_csv(file4)
        merged_df = pd.merge(df3, df4, on='KISCOURSEID')
        columns_to_keep = [
            'KISCOURSEID', 'TITLE', 'CRSEURL', 'NUMSTAGE', 'YEARABROAD', 'UKPRN_x',
            'T001', 'T048', 'T064', 'T080', 'T096', 'T112', 'T128', 'T144', 'T160', 'T176', 'T192', 'T208', 'T224', 'T240'
        ]
        cleaned_df = merged_df[columns_to_keep]
        cleaned_df['YEARABROAD'] = cleaned_df['YEARABROAD'].replace({2: 1}).fillna(0)
        cleaned_df = cleaned_df.dropna(subset=['KISCOURSEID'])
        cleaned_df = cleaned_df.drop_duplicates(subset=['KISCOURSEID'], keep='first')
        cleaned_df = cleaned_df.rename(columns={'UKPRN_x': 'UKPRN'})
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

def drop_tables():
    with psycopg.connect("dbname=University user=postgres password=P9@ndalfos") as conn:
        with conn.cursor() as cur:
            cur.execute("""
            DROP TABLE IF EXISTS "requirement" CASCADE;
            DROP TABLE IF EXISTS "university" CASCADE;
            DROP TABLE IF EXISTS "course" CASCADE;
            """)
            conn.commit()

def populate_requirement():
    with psycopg.connect("dbname=University user=postgres password=P9@ndalfos") as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        INSERT INTO requirement (course_id, grade, a_level_subject) VALUES ('UUUMA-L110~USMA-AFB30', 'A*', 'Mathematics');
            """)
            conn.commit()


if __name__ == "__main__":
    main()