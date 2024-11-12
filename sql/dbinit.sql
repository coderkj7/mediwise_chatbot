CREATE TABLE doctors (
    doctor_id SERIAL PRIMARY KEY,
    doctor_name VARCHAR(50) NOT NULL,
    doctor_specialty VARCHAR(50) NOT NULL,
    availability VARCHAR(50) NOT NULL,
    location VARCHAR(50) NOT NULL,
    accepting_new_patients BOOLEAN NOT NULL
);


CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    patient_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    medical_record_number VARCHAR(50) NOT NULL,
    symptoms VARCHAR(50) NULL,
    doctor_type_requested  VARCHAR(50) NULL,
    chat_summary TEXT,
    consent BOOLEAN DEFAULT False
);
CREATE UNIQUE INDEX idx_patients
ON patients(medical_record_number);



CREATE TABLE appointments (
    appointment_id SERIAL PRIMARY KEY,
    doctor_name VARCHAR(50) NOT NULL,
    patient_medical_record_number  VARCHAR(50) NOT NULL,
    appointment_start_ts timestamp NOT NULL,
    created_ts timestamp NOT NULL
);
CREATE UNIQUE INDEX idx_appointments
ON appointments(doctor_name, patient_medical_record_number);


INSERT INTO doctors (doctor_name, doctor_specialty, availability, location, accepting_new_patients) 
VALUES 
('Dr.EmilyCarter','GeneralPractitioner','Mon-Fri9am-5pm','FamilyMedicineBuilding','True'),
('Dr.MichaelThompson','Pediatrician','Mon-Fri8am-4pm','MainHospital','True'),
('Dr.SarahJohnson','GeneralPractitioner','Tue-Thu10am-6pm','FamilyMedicineBuilding','False'),
('Dr.DavidLee','Cardiologist','Mon-Wed9am-3pm','MainHospital','True'),
('Dr.LisaBrown','GeneralPractitioner','Mon-Fri8am-5pm','FamilyMedicineBuilding','True'),
('Dr.JamesWilson','Dermatologist','Wed-Fri9am-4pm','MainHospital','False'),
('Dr.KarenSmith','GeneralPractitioner','Mon-Thu9am-5pm','FamilyMedicineBuilding','True'),
('Dr.RobertGarcia','OrthopedicSurgeon','Tue-Fri8am-4pm','MainHospital','True'),
('Dr.PatriciaMartinez','Endocrinologist','Mon-Thu10am-5pm','MainHospital','False'),
('Dr.JohnAnderson','GeneralPractitioner','Mon-Fri8am-6pm','FamilyMedicineBuilding','True'),
('Dr.AngelaWhite','Neurologist','Tue-Thu9am-3pm','MainHospital','True'),
('Dr.CharlesHarris','Gastroenterologist','Mon-Wed9am-5pm','MainHospital','False'),
('Dr.JenniferClark','Psychiatrist','Mon-Fri10am-4pm','MainHospital','True'),
('Dr.DanielLewis','Urologist','Tue-Thu8am-5pm','MainHospital','True'),
('Dr.MichelleRobinson','Pulmonologist','Mon-Wed9am-4pm','MainHospital','False'),
('Dr.StevenYoung','Rheumatologist','Mon-Fri8am-5pm','MainHospital','True'),
('Dr.LauraKing','Ophthalmologist','Tue-Fri9am-4pm','MainHospital','True'),
('Dr.BrianWright','Oncologist','Mon-Thu10am-5pm','MainHospital','False'),
('Dr.NancyHill','FamilyMedicine','Mon-Fri9am-5pm','FamilyMedicineBuilding','True');


INSERT INTO patients (patient_name, date_of_birth,medical_record_number, symptoms, doctor_type_requested, chat_summary, consent) 
VALUES 
('JohnSmith','1985-06-15','MRN123456','Headache,nausea','Neurologist', NULL, 'False'),
('EmilyJohnson','1990-03-22','MRN123457','Cough,fever','Pulmonologist', NULL, 'False'),
('MichaelBrown','1978-12-30','MRN123458','Chestpain','Cardiologist', NULL, 'False'),
('JessicaDavis','1982-01-05','MRN123459','Jointpain,swelling','Rheumatologist', NULL, 'False'),
('DavidWilson','1995-07-19','MRN123460','Abdominalpain','Gastroenterologist', NULL, 'False'),
('SarahMiller','1988-09-25','MRN123461','Fatigue,weightloss','Endocrinologist', NULL, 'False'),
('DanielGarcia','1975-11-11','MRN123462','Skinrash,itching','Dermatologist', NULL, 'False'),
('LauraMartinez','1992-05-16','MRN123463','Shortnessofbreath','Pulmonologist', NULL, 'False'),
('JamesRodriguez','1980-04-02','MRN123464','Dizziness,fainting','Cardiologist', NULL, 'False'),
('PatriciaHernandez','1983-08-30','MRN123465','Backpain','Orthopedic', NULL, 'False'),
('RobertLee','1970-02-14','MRN123466','Nausea,vomiting','Gastroenterologist', NULL, 'False'),
('LindaWalker','1991-10-10','MRN123467','Anxiety,insomnia','Psychiatrist', NULL, 'False'),
('CharlesHall','1986-12-01','MRN123468','Visionchanges','Ophthalmologist', NULL, 'False'),
('SusanAllen','1979-07-27','MRN123469','Hearingloss','Audiologist', NULL, 'False'),
('JosephYoung','1994-03-03','MRN123470','Throatpain','ENTSpecialist', NULL, 'False'),
('KarenKing','1987-05-20','MRN123471','Moodswings','Psychiatrist', NULL, 'False'),
('ThomasWright','1981-08-12','MRN123472','Highbloodpressure','Cardiologist', NULL, 'False'),
('NancyScott','1993-04-28','MRN123473','Allergicreaction','Allergist', NULL, 'False'),
('DanielGreen','1984-11-21','MRN123474','Fatigue,headaches','Neurologist', NULL, 'False'),
('BarbaraAdams','1976-09-09','MRN123475','Chesttightness','Cardiologist', NULL, 'False'),
('MatthewNelson','1990-06-07','MRN123476','Jointstiffness','Rheumatologist', NULL, 'False'),
('JessicaCarter','1989-02-18','MRN123477','Persistentcough','Pulmonologist', NULL, 'False'),
('BrianMitchell','1980-01-30','MRN123478','Severeabdominalpain','Gastroenterologist', NULL, 'False'),
('AngelaPerez','1995-10-05','MRN123479','Skinlesions','Dermatologist', NULL, 'False'),
('KevinRoberts','1974-12-12','MRN123480','Frequentheadaches','Neurologist', NULL, 'False'),
('MeganTurner','1988-03-15','MRN123481','Weightgain,fatigue','Endocrinologist', NULL, 'False'),
('EdwardPhillips','1992-08-22','MRN123482','Numbnessinlimbs','Neurologist', NULL, 'False'),
('AshleyCampbell','1981-04-06','MRN123483','Severefatigue','Endocrinologist', NULL, 'False'),
('ChristopherParker','1979-09-29','MRN123484','Chestpain,sweating','Cardiologist', NULL, 'False'),
('MichelleEvans','1993-01-11','MRN123485','Severeanxiety','Psychiatrist', NULL, 'False'),
('JoshuaEdwards','1986-07-14','MRN123486','Difficultybreathing','Pulmonologist', NULL, 'False'),
('SamanthaCollins','1991-11-18','MRN123487','Nausea,dizziness','Gastroenterologist', NULL, 'False'),
('RyanStewart','1984-05-27','MRN123488','Jointpain','Rheumatologist', NULL, 'False'),
('LauraSanchez','1990-10-30','MRN123489','Skinirritation','Dermatologist', NULL, 'False'),
('NicholasMorris','1977-02-20','MRN123490','Severeheadaches','Neurologist', NULL, 'False');
