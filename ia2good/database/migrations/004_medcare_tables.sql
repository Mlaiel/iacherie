-- Migration: 004_medcare_tables.sql
-- Create MedCare-AI module tables
-- Date: 2025-01-08

BEGIN;

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Patients table
CREATE TABLE IF NOT EXISTS medcare_patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL,
    birth_date DATE NOT NULL,
    gender VARCHAR(20),
    blood_type VARCHAR(10),
    height_cm INTEGER,
    weight_kg FLOAT,
    allergies TEXT[],
    chronic_conditions TEXT[],
    current_medications JSONB DEFAULT '[]'::jsonb,
    emergency_contact JSONB,
    insurance_info JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Symptom reports table
CREATE TABLE IF NOT EXISTS medcare_symptom_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES medcare_patients(id) ON DELETE CASCADE,
    symptoms JSONB NOT NULL,
    severity INTEGER CHECK (severity BETWEEN 1 AND 10),
    duration_hours INTEGER,
    body_parts TEXT[],
    images TEXT[],
    ai_analysis JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Diagnoses table
CREATE TABLE IF NOT EXISTS medcare_diagnoses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symptom_report_id UUID NOT NULL REFERENCES medcare_symptom_reports(id) ON DELETE CASCADE,
    condition_name VARCHAR(255) NOT NULL,
    confidence FLOAT CHECK (confidence BETWEEN 0 AND 1),
    icd10_code VARCHAR(20),
    urgency VARCHAR(20) CHECK (urgency IN ('emergency', 'urgent', 'routine', 'monitor')),
    recommendations TEXT,
    differential_diagnoses JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Consultations table
CREATE TABLE IF NOT EXISTS medcare_consultations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES medcare_patients(id) ON DELETE CASCADE,
    doctor_id UUID NOT NULL,
    symptom_report_id UUID REFERENCES medcare_symptom_reports(id),
    type VARCHAR(20) CHECK (type IN ('video', 'chat', 'phone', 'in_person')),
    status VARCHAR(20) DEFAULT 'scheduled',
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    duration_minutes INTEGER,
    notes TEXT,
    diagnosis TEXT,
    amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Prescriptions table
CREATE TABLE IF NOT EXISTS medcare_prescriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consultation_id UUID REFERENCES medcare_consultations(id),
    patient_id UUID NOT NULL REFERENCES medcare_patients(id) ON DELETE CASCADE,
    doctor_id UUID NOT NULL,
    medications JSONB NOT NULL,
    instructions TEXT,
    valid_until DATE,
    qr_code TEXT,
    dispensed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Image analysis table
CREATE TABLE IF NOT EXISTS medcare_image_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES medcare_patients(id) ON DELETE CASCADE,
    image_path TEXT NOT NULL,
    image_type VARCHAR(50) NOT NULL,
    ai_analysis JSONB,
    reviewed_by_doctor UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Medical records table (aggregate view)
CREATE TABLE IF NOT EXISTS medcare_medical_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES medcare_patients(id) ON DELETE CASCADE,
    record_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    created_by UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Doctors table (extends users)
CREATE TABLE IF NOT EXISTS medcare_doctors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL,
    specialties TEXT[],
    license_number VARCHAR(100) UNIQUE NOT NULL,
    license_expiry DATE,
    is_verified BOOLEAN DEFAULT false,
    rating FLOAT DEFAULT 0.0,
    total_consultations INTEGER DEFAULT 0,
    available BOOLEAN DEFAULT true,
    hourly_rate DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_medcare_patients_user ON medcare_patients(user_id);
CREATE INDEX IF NOT EXISTS idx_medcare_symptoms_patient ON medcare_symptom_reports(patient_id);
CREATE INDEX IF NOT EXISTS idx_medcare_symptoms_created ON medcare_symptom_reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_medcare_diagnoses_symptom ON medcare_diagnoses(symptom_report_id);
CREATE INDEX IF NOT EXISTS idx_medcare_diagnoses_urgency ON medcare_diagnoses(urgency);
CREATE INDEX IF NOT EXISTS idx_medcare_consultations_patient ON medcare_consultations(patient_id);
CREATE INDEX IF NOT EXISTS idx_medcare_consultations_doctor ON medcare_consultations(doctor_id);
CREATE INDEX IF NOT EXISTS idx_medcare_consultations_status ON medcare_consultations(status);
CREATE INDEX IF NOT EXISTS idx_medcare_consultations_scheduled ON medcare_consultations(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_medcare_prescriptions_consultation ON medcare_prescriptions(consultation_id);
CREATE INDEX IF NOT EXISTS idx_medcare_prescriptions_patient ON medcare_prescriptions(patient_id);
CREATE INDEX IF NOT EXISTS idx_medcare_prescriptions_valid ON medcare_prescriptions(valid_until);
CREATE INDEX IF NOT EXISTS idx_medcare_images_patient ON medcare_image_analyses(patient_id);
CREATE INDEX IF NOT EXISTS idx_medcare_records_patient ON medcare_medical_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_medcare_doctors_user ON medcare_doctors(user_id);
CREATE INDEX IF NOT EXISTS idx_medcare_doctors_available ON medcare_doctors(available);

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_medcare_patients_updated_at BEFORE UPDATE ON medcare_patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_medcare_consultations_updated_at BEFORE UPDATE ON medcare_consultations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_medcare_prescriptions_updated_at BEFORE UPDATE ON medcare_prescriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_medcare_doctors_updated_at BEFORE UPDATE ON medcare_doctors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
