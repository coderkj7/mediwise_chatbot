CREATE TABLE appointments (
    appointment_id SERIAL PRIMARY KEY,
    doctor_id INTEGER NOT NULL,
    patient_id  INTEGER NOT NULL,
    appointment_start_ts timestamp NOT NULL,
    created_ts timestamp NOT NULL
);


INSERT INTO appointments ( doctor_id, patient_id,appointment_start_ts, created_ts ) 
VALUES 
( '1', '1','2024-10-25 14:30:00', '2024-10-17 10:30:00' ),
( '1', '2','2024-10-25 14:0:00', '2024-10-17 10:30:00' ),
( '2', '3','2024-10-25 14:30:00', '2024-10-17 10:30:00' ),
( '3', '4','2024-10-25 14:30:00', '2024-10-17 10:30:00' );