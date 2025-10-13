-- MedCare-AI Database Schema
-- Telemedicine and AI Diagnostic System

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
    doctor_id UUID,
    symptom_report_id UUID REFERENCES medcare_symptom_reports(id),
    type VARCHAR(20) CHECK (type IN ('video', 'chat', 'phone', 'in_person')),
    status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'no_show')),
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
    consultation_id UUID NOT NULL REFERENCES medcare_consultations(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES medcare_patients(id) ON DELETE CASCADE,
    doctor_id UUID NOT NULL,
    medications JSONB NOT NULL,
    instructions TEXT,
    valid_until DATE NOT NULL,
    qr_code TEXT NOT NULL UNIQUE,
    dispensed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Medical images table
CREATE TABLE IF NOT EXISTS medcare_medical_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES medcare_patients(id) ON DELETE CASCADE,
    symptom_report_id UUID REFERENCES medcare_symptom_reports(id),
    image_type VARCHAR(50) NOT NULL, -- skin, xray, mri, ct_scan, etc.
    image_url TEXT NOT NULL,
    ai_analysis JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Video call sessions table
CREATE TABLE IF NOT EXISTS medcare_video_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consultation_id UUID NOT NULL REFERENCES medcare_consultations(id) ON DELETE CASCADE,
    room_id TEXT NOT NULL UNIQUE,
    provider VARCHAR(50), -- twilio, jitsi, custom
    session_data JSONB,
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    duration_minutes INTEGER
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_medcare_patients_user ON medcare_patients(user_id);
CREATE INDEX IF NOT EXISTS idx_medcare_symptoms_patient ON medcare_symptom_reports(patient_id);
CREATE INDEX IF NOT EXISTS idx_medcare_symptoms_created ON medcare_symptom_reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_medcare_diagnoses_symptom ON medcare_diagnoses(symptom_report_id);
CREATE INDEX IF NOT EXISTS idx_medcare_consultations_patient ON medcare_consultations(patient_id);
CREATE INDEX IF NOT EXISTS idx_medcare_consultations_doctor ON medcare_consultations(doctor_id);
CREATE INDEX IF NOT EXISTS idx_medcare_consultations_status ON medcare_consultations(status);
CREATE INDEX IF NOT EXISTS idx_medcare_consultations_scheduled ON medcare_consultations(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_medcare_prescriptions_patient ON medcare_prescriptions(patient_id);
CREATE INDEX IF NOT EXISTS idx_medcare_prescriptions_qr ON medcare_prescriptions(qr_code);
CREATE INDEX IF NOT EXISTS idx_medcare_images_patient ON medcare_medical_images(patient_id);

-- Triggers for updated_at
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

-- Medical documents table (NEW: dialyse, ordonnances, IRM, X-ray, etc.)
CREATE TABLE IF NOT EXISTS medcare_medical_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES medcare_patients(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL, -- prescription, lab_result, xray, mri, ct_scan, dialysis_report, blood_test, etc.
    original_filename VARCHAR(255),
    file_url TEXT NOT NULL,
    file_size_bytes INTEGER,
    mime_type VARCHAR(100),
    language_detected VARCHAR(10),
    ocr_text TEXT,
    ai_analysis JSONB,
    is_shared_anonymously BOOLEAN DEFAULT false,
    anonymous_share_id UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Community forum posts (NEW: consultation publique anonyme)
CREATE TABLE IF NOT EXISTS medcare_community_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID NOT NULL, -- User ID (patient or doctor)
    author_type VARCHAR(20) CHECK (author_type IN ('patient', 'doctor', 'specialist')),
    post_type VARCHAR(30) CHECK (post_type IN ('case_discussion', 'second_opinion', 'medical_advice', 'document_review')),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    related_document_id UUID REFERENCES medcare_medical_documents(id),
    is_anonymous BOOLEAN DEFAULT true,
    anonymous_display_name VARCHAR(100),
    tags TEXT[],
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'closed', 'archived', 'flagged')),
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Community forum responses
CREATE TABLE IF NOT EXISTS medcare_community_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES medcare_community_posts(id) ON DELETE CASCADE,
    author_id UUID NOT NULL,
    author_type VARCHAR(20) CHECK (author_type IN ('patient', 'doctor', 'specialist', 'pharmacist')),
    content TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    is_anonymous BOOLEAN DEFAULT true,
    anonymous_display_name VARCHAR(100),
    helpful_votes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Medication solidarity requests (NEW: solidarité médicaments)
CREATE TABLE IF NOT EXISTS medcare_medication_solidarity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES medcare_patients(id) ON DELETE CASCADE,
    prescription_id UUID REFERENCES medcare_prescriptions(id),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    medications_needed JSONB NOT NULL, -- [{name, dosage, quantity, estimated_cost}]
    total_estimated_cost DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'EUR',
    urgency VARCHAR(20) CHECK (urgency IN ('critical', 'urgent', 'normal')),
    delivery_address JSONB, -- Encrypted address for delivery
    status VARCHAR(30) DEFAULT 'open' CHECK (status IN ('open', 'partially_funded', 'fully_funded', 'delivered', 'cancelled')),
    amount_raised DECIMAL(10,2) DEFAULT 0,
    is_verified BOOLEAN DEFAULT false,
    verified_by_doctor_id UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Medication solidarity contributions
CREATE TABLE IF NOT EXISTS medcare_medication_contributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solidarity_request_id UUID NOT NULL REFERENCES medcare_medication_solidarity(id) ON DELETE CASCADE,
    contributor_id UUID NOT NULL, -- User ID of volunteer
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    payment_method VARCHAR(50),
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'completed', 'failed', 'refunded')),
    payment_transaction_id TEXT,
    message_to_patient TEXT,
    is_anonymous BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Medication solidarity deliveries
CREATE TABLE IF NOT EXISTS medcare_medication_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solidarity_request_id UUID NOT NULL REFERENCES medcare_medication_solidarity(id) ON DELETE CASCADE,
    volunteer_id UUID, -- Optional: volunteer delivering
    pharmacy_id UUID, -- Pharmacy fulfilling the prescription
    tracking_number TEXT,
    delivery_status VARCHAR(30) DEFAULT 'pending' CHECK (delivery_status IN ('pending', 'purchased', 'in_transit', 'delivered', 'failed')),
    purchased_at TIMESTAMP,
    delivered_at TIMESTAMP,
    delivery_proof_url TEXT, -- Photo/signature proof
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for new tables
CREATE INDEX IF NOT EXISTS idx_medical_documents_patient ON medcare_medical_documents(patient_id);
CREATE INDEX IF NOT EXISTS idx_medical_documents_type ON medcare_medical_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_medical_documents_shared ON medcare_medical_documents(is_shared_anonymously) WHERE is_shared_anonymously = true;
CREATE INDEX IF NOT EXISTS idx_medical_documents_created ON medcare_medical_documents(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_community_posts_author ON medcare_community_posts(author_id);
CREATE INDEX IF NOT EXISTS idx_community_posts_type ON medcare_community_posts(post_type);
CREATE INDEX IF NOT EXISTS idx_community_posts_status ON medcare_community_posts(status);
CREATE INDEX IF NOT EXISTS idx_community_posts_created ON medcare_community_posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_community_posts_tags ON medcare_community_posts USING gin(tags);

CREATE INDEX IF NOT EXISTS idx_community_responses_post ON medcare_community_responses(post_id);
CREATE INDEX IF NOT EXISTS idx_community_responses_author ON medcare_community_responses(author_id);
CREATE INDEX IF NOT EXISTS idx_community_responses_votes ON medcare_community_responses(helpful_votes DESC);

CREATE INDEX IF NOT EXISTS idx_medication_solidarity_patient ON medcare_medication_solidarity(patient_id);
CREATE INDEX IF NOT EXISTS idx_medication_solidarity_status ON medcare_medication_solidarity(status);
CREATE INDEX IF NOT EXISTS idx_medication_solidarity_urgency ON medcare_medication_solidarity(urgency);
CREATE INDEX IF NOT EXISTS idx_medication_solidarity_created ON medcare_medication_solidarity(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_medication_contributions_request ON medcare_medication_contributions(solidarity_request_id);
CREATE INDEX IF NOT EXISTS idx_medication_contributions_contributor ON medcare_medication_contributions(contributor_id);
CREATE INDEX IF NOT EXISTS idx_medication_contributions_status ON medcare_medication_contributions(payment_status);

CREATE INDEX IF NOT EXISTS idx_medication_deliveries_request ON medcare_medication_deliveries(solidarity_request_id);
CREATE INDEX IF NOT EXISTS idx_medication_deliveries_status ON medcare_medication_deliveries(delivery_status);

-- Triggers for updated_at
CREATE TRIGGER update_medical_documents_updated_at BEFORE UPDATE ON medcare_medical_documents
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_community_posts_updated_at BEFORE UPDATE ON medcare_community_posts
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_medication_solidarity_updated_at BEFORE UPDATE ON medcare_medication_solidarity
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

