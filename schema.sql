-- GreenDiagnose Database Schema
-- Final design: species-specific classification, no runtime admin/auth tables
-- MySQL 8.0+

CREATE DATABASE IF NOT EXISTS greendiagnose;
USE greendiagnose;

-- ============================================================
-- 1. Reference data: the 10 covered species
-- ============================================================
CREATE TABLE plant_species (
    id INT AUTO_INCREMENT PRIMARY KEY,
    common_name VARCHAR(100) NOT NULL,
    scientific_name VARCHAR(150),
    dataset_source VARCHAR(150) COMMENT 'e.g. Mendeley, Kaggle, Roboflow - for methodology documentation',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- 2. Diseases — tied directly to a species (not a shared category)
-- ============================================================
CREATE TABLE disease (
    id INT AUTO_INCREMENT PRIMARY KEY,
    species_id INT NOT NULL,
    name VARCHAR(150) NOT NULL COMMENT 'e.g. "Fungal Leaf Spot", specific to this species',
    description TEXT,
    severity_level ENUM('low', 'moderate', 'high') DEFAULT 'moderate',
    FOREIGN KEY (species_id) REFERENCES plant_species(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 3. Symptoms / questionnaire questions — tied to species
--    (a question can be relevant to one or more diseases within that species)
-- ============================================================
CREATE TABLE symptom (
    id INT AUTO_INCREMENT PRIMARY KEY,
    species_id INT NOT NULL,
    question_text VARCHAR(255) NOT NULL,
    answer_type ENUM('yes_no', 'yes_no_unsure', 'multiple_choice') DEFAULT 'yes_no_unsure',
    display_order INT DEFAULT 0,
    FOREIGN KEY (species_id) REFERENCES plant_species(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 4. The actual rule engine: weighted links between symptoms and diseases
--    certainty_weight: how strongly a "yes" to this symptom indicates this disease (0.0-1.0)
-- ============================================================
CREATE TABLE disease_symptom_rule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    disease_id INT NOT NULL,
    symptom_id INT NOT NULL,
    certainty_weight DECIMAL(3,2) NOT NULL COMMENT 'e.g. 0.85',
    FOREIGN KEY (disease_id) REFERENCES disease(id) ON DELETE CASCADE,
    FOREIGN KEY (symptom_id) REFERENCES symptom(id) ON DELETE CASCADE,
    UNIQUE KEY unique_rule (disease_id, symptom_id)
) ENGINE=InnoDB;

-- ============================================================
-- 5. Treatment / care recommendations per disease
-- ============================================================
CREATE TABLE treatment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    disease_id INT NOT NULL,
    recommendation_text TEXT NOT NULL,
    FOREIGN KEY (disease_id) REFERENCES disease(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 6. One row per user diagnosis session (accountless — no user_id anywhere)
-- ============================================================
CREATE TABLE diagnosis_session (
    id INT AUTO_INCREMENT PRIMARY KEY,
    species_id INT NOT NULL,
    image_path VARCHAR(255) NOT NULL COMMENT 'retained photo, pending horticulturist validation before any training use',
    predicted_disease_id INT COMMENT 'CNN''s top prediction, filled after classification',
    predicted_confidence DECIMAL(5,4) COMMENT 'e.g. 0.9134',
    consent_for_training BOOLEAN DEFAULT FALSE COMMENT 'explicit separate consent, per RA 10173 requirement',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (species_id) REFERENCES plant_species(id),
    FOREIGN KEY (predicted_disease_id) REFERENCES disease(id)
) ENGINE=InnoDB;

-- ============================================================
-- 7. Questionnaire answers logged per session
-- ============================================================
CREATE TABLE session_answer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    symptom_id INT NOT NULL,
    answer_value VARCHAR(20) NOT NULL COMMENT 'yes / no / unsure',
    FOREIGN KEY (session_id) REFERENCES diagnosis_session(id) ON DELETE CASCADE,
    FOREIGN KEY (symptom_id) REFERENCES symptom(id)
) ENGINE=InnoDB;

-- ============================================================
-- 8. Final ranked diagnosis results per session (top result + alternatives)
-- ============================================================
CREATE TABLE session_result (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    disease_id INT NOT NULL,
    confidence_score DECIMAL(5,4) NOT NULL,
    result_rank INT NOT NULL COMMENT '1 = top diagnosis, 2 = first alternative, etc.',
    FOREIGN KEY (session_id) REFERENCES diagnosis_session(id) ON DELETE CASCADE,
    FOREIGN KEY (disease_id) REFERENCES disease(id)
) ENGINE=InnoDB;

-- ============================================================
-- Seed the 10 species (fill in scientific names / dataset source as confirmed)
-- ============================================================
INSERT INTO plant_species (common_name, scientific_name, dataset_source) VALUES
('Hibiscus', 'Hibiscus rosa-sinensis', 'Mendeley Data'),
('Aloe Vera', 'Aloe vera', 'Kaggle - Indoor Plant Disease Detection Dataset'),
('Cactus', NULL, 'Kaggle - Indoor Plant Disease Detection Dataset'),
('Money Plant', 'Epipremnum aureum', 'Kaggle - Indoor Plant Disease Detection Dataset'),
('Snake Plant', 'Dracaena trifasciata', 'Kaggle - Indoor Plant Disease Detection Dataset'),
('Spider Plant', 'Chlorophytum comosum', 'Kaggle - Indoor Plant Disease Detection Dataset'),
('Rose', 'Rosa spp.', 'Mendeley Data'),
('Marigold', 'Tagetes spp.', 'Mendeley Data'),
('Orchid', NULL, 'Roboflow'),
('Sunflower', 'Helianthus annuus', 'Kaggle');

-- NOTE: disease, symptom, disease_symptom_rule, and treatment tables
-- are intentionally left empty here — populate them from your team's
-- rule-drafting work (Step 4 of the kickoff plan), validated by your
-- collaborating horticulturist, before the knowledge base is considered complete.
