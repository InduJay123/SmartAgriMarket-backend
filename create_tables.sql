-- Create crops table
CREATE TABLE IF NOT EXISTS crops (
    crop_id INT AUTO_INCREMENT PRIMARY KEY,
    crop_name VARCHAR(100) NOT NULL,
    description TEXT,
    image VARCHAR(255),
    category VARCHAR(100),
    INDEX idx_crop_name (crop_name)
);

-- Create marketplace table
CREATE TABLE IF NOT EXISTS marketplace (
    market_id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    crop_id INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    predicted_date DATE NOT NULL,
    quantity INT NOT NULL,
    farming_method VARCHAR(255),
    region VARCHAR(255),
    district VARCHAR(255),
    image LONGTEXT,
    status VARCHAR(20) DEFAULT 'Available',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_farmer_id (farmer_id),
    INDEX idx_crop_id (crop_id),
    INDEX idx_status (status),
    CONSTRAINT fk_marketplace_crop FOREIGN KEY (crop_id) REFERENCES crops(crop_id) ON DELETE CASCADE
);
