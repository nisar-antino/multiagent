-- Multi-Agent GST Database Schema
-- Indian GST Invoicing System

-- ============================================
-- Table 1: Vendors
-- ============================================
CREATE TABLE IF NOT EXISTS vendors (
    vendor_id INT PRIMARY KEY AUTO_INCREMENT,
    vendor_name VARCHAR(255) NOT NULL,
    gstin VARCHAR(15) NOT NULL UNIQUE,
    state VARCHAR(50) NOT NULL,
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Table 2: Invoices
-- ============================================
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id INT PRIMARY KEY AUTO_INCREMENT,
    vendor_id INT NOT NULL,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    date DATE NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    tax_amount DECIMAL(12, 2) NOT NULL,
    cgst DECIMAL(12, 2) DEFAULT 0.00,
    sgst DECIMAL(12, 2) DEFAULT 0.00,
    igst DECIMAL(12, 2) DEFAULT 0.00,
    status ENUM('PAID', 'UNPAID', 'OVERDUE') DEFAULT 'PAID',
    place_of_supply VARCHAR(50) NOT NULL,
    is_reverse_charge BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

-- ============================================
-- Table 3: Invoice Items
-- ============================================
CREATE TABLE IF NOT EXISTS invoice_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_id INT NOT NULL,
    description VARCHAR(255) NOT NULL,
    hsn_code VARCHAR(8) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    tax_rate DECIMAL(5, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
);

-- ============================================
-- Seed Data: Vendors (20 vendors across Indian states)
-- ============================================
INSERT INTO vendors (vendor_name, gstin, state, city) VALUES
('Tech Solutions Pvt Ltd', '29ABCDE1234F1Z5', 'Karnataka', 'Bangalore'),
('Mumbai Electronics', '27FGHIJ5678K2L6', 'Maharashtra', 'Mumbai'),
('Delhi Hardware Store', '07MNOPQ9012R3S7', 'Delhi', 'New Delhi'),
('Chennai Textiles', '33TUVWX3456Y4A8', 'Tamil Nadu', 'Chennai'),
('Hyderabad Traders', '36ZABCD7890E5B9', 'Telangana', 'Hyderabad'),
(' Kolkata Merchants', '19FGHIJ1234K6C0', 'West Bengal', 'Kolkata'),
('Pune Software Services', '27LMNOP5678Q7D1', 'Maharashtra', 'Pune'),
('Jaipur Handicrafts', '08RSTUV9012W8E2', 'Rajasthan', 'Jaipur'),
('Ahmedabad Chemicals', '24WXYZAB3456C9F', 'Gujarat', 'Ahmedabad'),
('Lucknow Enterprises', '09CDEFGH7890D0G', 'Uttar Pradesh', 'Lucknow'),
('Kochi Spices Export', '32IJKLMN1234E1H', 'Kerala', 'Kochi'),
('Chandigarh IT Hub', '04OPQRST5678F2I', 'Chandigarh', 'Chandigarh'),
('Guwahati Tea Company', '18UVWXYZ9012G3J', 'Assam', 'Guwahati'),
('Indore Manufacturing', '23ABCDEF3456H4K', 'Madhya Pradesh', 'Indore'),
('Visakhapatnam Steel', '37GHIJKL7890I5L', 'Andhra Pradesh', 'Visakhapatnam'),
('Bhopal Pharma Ltd', '23MNOPQR1234J6M', 'Madhya Pradesh', 'Bhopal'),
('Surat Diamonds', '24STUVWX5678K7N', 'Gujarat', 'Surat'),
('Coimbatore Motors', '33YZABCD9012L8O', 'Tamil Nadu', 'Coimbatore'),
('Nagpur Logistics', '27EFGHIJ3456M9P', 'Maharashtra', 'Nagpur'),
('Patna Agro Products', '10KLMNOP7890N0Q', 'Bihar', 'Patna');

-- ============================================
-- Seed Data: Invoices (100 invoices with diverse scenarios)
-- ============================================

-- INTRA-STATE TRANSACTIONS (CGST + SGST) - Karnataka
INSERT INTO invoices (vendor_id, invoice_number, date, total_amount, tax_amount, cgst, sgst, igst, status, place_of_supply, is_reverse_charge) VALUES
(1, 'INV-KA-001', '2024-01-15', 50000.00, 9000.00, 4500.00, 4500.00, 0.00, 'PAID', 'Karnataka', 0),
(1, 'INV-KA-002', '2024-01-20', 75000.00, 13500.00, 6750.00, 6750.00, 0.00, 'PAID', 'Karnataka', 0),
(1, 'INV-KA-003', '2024-02-05', 120000.00, 21600.00, 10800.00, 10800.00, 0.00, 'UNPAID', 'Karnataka', 0),
(1, 'INV-KA-004', '2024-02-12', 85000.00, 15300.00, 7650.00, 7650.00, 0.00, 'PAID', 'Karnataka', 0),
(1, 'INV-KA-005', '2024-03-01', 95000.00, 17100.00, 8550.00, 8550.00, 0.00, 'PAID', 'Karnataka', 1),

-- INTER-STATE TRANSACTIONS (IGST) - Maharashtra to Other States
(2, 'INV-MH-001', '2024-01-10', 80000.00, 14400.00, 0.00, 0.00, 14400.00, 'PAID', 'Karnataka', 0),
(2, 'INV-MH-002', '2024-01-25', 110000.00, 19800.00, 0.00, 0.00, 19800.00, 'PAID', 'Delhi', 0),
(2, 'INV-MH-003', '2024-02-08', 65000.00, 11700.00, 0.00, 0.00, 11700.00, 'OVERDUE', 'Tamil Nadu', 0),
(2, 'INV-MH-004', '2024-02-15', 150000.00, 27000.00, 0.00, 0.00, 27000.00, 'PAID', 'Gujarat', 0),
(2, 'INV-MH-005', '2024-03-05', 92000.00, 16560.00, 0.00, 0.00, 16560.00, 'UNPAID', 'Telangana', 0),

-- INTRA-STATE - Maharashtra
(2, 'INV-MH-006', '2024-03-10', 45000.00, 8100.00, 4050.00, 4050.00, 0.00, 'PAID', 'Maharashtra', 0),
(7, 'INV-PN-001', '2024-01-18', 130000.00, 23400.00, 11700.00, 11700.00, 0.00, 'PAID', 'Maharashtra', 0),
(7, 'INV-PN-002', '2024-02-22', 78000.00, 14040.00, 7020.00, 7020.00, 0.00, 'PAID', 'Maharashtra', 0),
(19, 'INV-NG-001', '2024-03-12', 56000.00, 10080.00, 5040.00, 5040.00, 0.00, 'UNPAID', 'Maharashtra', 0),

-- INTRA-STATE - Delhi
(3, 'INV-DL-001', '2024-01-12', 68000.00, 12240.00, 6120.00, 6120.00, 0.00, 'PAID', 'Delhi', 0),
(3, 'INV-DL-002', '2024-02-17', 145000.00, 26100.00, 13050.00, 13050.00, 0.00, 'PAID', 'Delhi', 0),
(3, 'INV-DL-003', '2024-03-08', 89000.00, 16020.00, 8010.00, 8010.00, 0.00, 'OVERDUE', 'Delhi', 0),

-- INTRA-STATE - Tamil Nadu
(4, 'INV-TN-001', '2024-01-22', 95000.00, 17100.00, 8550.00, 8550.00, 0.00, 'PAID', 'Tamil Nadu', 0),
(4, 'INV-TN-002', '2024-02-11', 112000.00, 20160.00, 10080.00, 10080.00, 0.00, 'PAID', 'Tamil Nadu', 0),
(18, 'INV-CB-001', '2024-03-15', 73000.00, 13140.00, 6570.00, 6570.00, 0.00, 'UNPAID', 'Tamil Nadu', 0),

-- INTER-STATE - Delhi to Other States
(3, 'INV-DL-004', '2024-01-28', 125000.00, 22500.00, 0.00, 0.00, 22500.00, 'PAID', 'Karnataka', 0),
(3, 'INV-DL-005', '2024-02-20', 88000.00, 15840.00, 0.00, 0.00, 15840.00, 'PAID', 'Maharashtra', 0),

-- INTRA-STATE - Telangana
(5, 'INV-TS-001', '2024-01-16', 103000.00, 18540.00, 9270.00, 9270.00, 0.00, 'PAID', 'Telangana', 0),
(5, 'INV-TS-002', '2024-02-25', 67000.00, 12060.00, 6030.00, 6030.00, 0.00, 'PAID', 'Telangana', 0),
(5, 'INV-TS-003', '2024-03-18', 154000.00, 27720.00, 13860.00, 13860.00, 0.00, 'UNPAID', 'Telangana', 0),

-- INTER-STATE - Tamil Nadu to Other States
(4, 'INV-TN-003', '2024-01-30', 76000.00, 13680.00, 0.00, 0.00, 13680.00, 'PAID', 'Kerala', 0),
(4, 'INV-TN-004', '2024-03-02', 99000.00, 17820.00, 0.00, 0.00, 17820.00, 'PAID', 'Karnataka', 0),
(18, 'INV-CB-002', '2024-02-14', 142000.00, 25560.00, 0.00, 0.00, 25560.00, 'OVERDUE', 'Andhra Pradesh', 0),

-- INTRA-STATE - West Bengal
(6, 'INV-WB-001', '2024-02-01', 59000.00, 10620.00, 5310.00, 5310.00, 0.00, 'PAID', 'West Bengal', 0),
(6, 'INV-WB-002', '2024-03-10', 87000.00, 15660.00, 7830.00, 7830.00, 0.00, 'PAID', 'West Bengal', 0),

-- INTRA-STATE - Gujarat
(9, 'INV-GJ-001', '2024-01-24', 118000.00, 21240.00, 10620.00, 10620.00, 0.00, 'PAID', 'Gujarat', 0),
(9, 'INV-GJ-002', '2024-02-28', 94000.00, 16920.00, 8460.00, 8460.00, 0.00, 'PAID', 'Gujarat', 0),
(17, 'INV-ST-001', '2024-03-20', 205000.00, 36900.00, 18450.00, 18450.00, 0.00, 'UNPAID', 'Gujarat', 0),
(17, 'INV-ST-002', '2024-03-22', 178000.00, 32040.00, 16020.00, 16020.00, 0.00, 'PAID', 'Gujarat', 0),

-- INTER-STATE - Gujarat to Other States
(9, 'INV-GJ-003', '2024-03-05', 135000.00, 24300.00, 0.00, 0.00, 24300.00, 'PAID', 'Rajasthan', 0),
(17, 'INV-ST-003', '2024-02-10', 88000.00, 15840.00, 0.00, 0.00, 15840.00, 'PAID', 'Maharashtra', 0),

-- INTRA-STATE - Rajasthan
(8, 'INV-RJ-001', '2024-01-19', 72000.00, 12960.00, 6480.00, 6480.00, 0.00, 'PAID', 'Rajasthan', 0),
(8, 'INV-RJ-002', '2024-02-26', 105000.00, 18900.00, 9450.00, 9450.00, 0.00, 'PAID', 'Rajasthan', 0),
(8, 'INV-RJ-003', '2024-03-14', 63000.00, 11340.00, 5670.00, 5670.00, 0.00, 'OVERDUE', 'Rajasthan', 0),

-- INTRA-STATE - Uttar Pradesh
(10, 'INV-UP-001', '2024-02-03', 81000.00, 14580.00, 7290.00, 7290.00, 0.00, 'PAID', 'Uttar Pradesh', 0),
(10, 'INV-UP-002', '2024-03-07', 127000.00, 22860.00, 11430.00, 11430.00, 0.00, 'PAID', 'Uttar Pradesh', 0),

-- INTRA-STATE - Kerala
(11, 'INV-KL-001', '2024-01-27', 96000.00, 17280.00, 8640.00, 8640.00, 0.00, 'PAID', 'Kerala', 0),
(11, 'INV-KL-002', '2024-02-19', 114000.00, 20520.00, 10260.00, 10260.00, 0.00, 'PAID', 'Kerala', 0),
(11, 'INV-KL-003', '2024-03-25', 69000.00, 12420.00, 6210.00, 6210.00, 0.00, 'UNPAID', 'Kerala', 0),

-- INTER-STATE - Kerala to Other States
(11, 'INV-KL-004', '2024-02-06', 148000.00, 26640.00, 0.00, 0.00, 26640.00, 'PAID', 'Tamil Nadu', 0),

-- INTRA-STATE - Madhya Pradesh
(14, 'INV-MP-001', '2024-01-21', 79000.00, 14220.00, 7110.00, 7110.00, 0.00, 'PAID', 'Madhya Pradesh', 0),
(14, 'INV-MP-002', '2024-02-24', 108000.00, 19440.00, 9720.00, 9720.00, 0.00, 'PAID', 'Madhya Pradesh', 0),
(16, 'INV-BP-001', '2024-03-11', 92000.00, 16560.00, 8280.00, 8280.00, 0.00, 'UNPAID', 'Madhya Pradesh', 0),

-- INTRA-STATE - Andhra Pradesh
(15, 'INV-AP-001', '2024-02-09', 132000.00, 23760.00, 11880.00, 11880.00, 0.00, 'PAID', 'Andhra Pradesh', 0),
(15, 'INV-AP-002', '2024-03-16', 86000.00, 15480.00, 7740.00, 7740.00, 0.00, 'PAID', 'Andhra Pradesh', 0),

-- INTER-STATE - Andhra Pradesh to Other States
(15, 'INV-AP-003', '2024-01-14', 115000.00, 20700.00, 0.00, 0.00, 20700.00, 'PAID', 'Telangana', 0),

-- INTRA-STATE - Chandigarh
(12, 'INV-CH-001', '2024-02-16', 74000.00, 13320.00, 6660.00, 6660.00, 0.00, 'PAID', 'Chandigarh', 0),
(12, 'INV-CH-002', '2024-03-23', 98000.00, 17640.00, 8820.00, 8820.00, 0.00, 'UNPAID', 'Chandigarh', 0),

-- INTRA-STATE - Assam
(13, 'INV-AS-001', '2024-01-26', 61000.00, 10980.00, 5490.00, 5490.00, 0.00, 'PAID', 'Assam', 0),
(13, 'INV-AS-002', '2024-03-19', 83000.00, 14940.00, 7470.00, 7470.00, 0.00, 'PAID', 'Assam', 0),

-- INTRA-STATE - Bihar
(20, 'INV-BR-001', '2024-02-21', 71000.00, 12780.00, 6390.00, 6390.00, 0.00, 'PAID', 'Bihar', 0),
(20, 'INV-BR-002', '2024-03-24', 104000.00, 18720.00, 9360.00, 9360.00, 0.00, 'OVERDUE', 'Bihar', 0),

-- COMPLIANCE VIOLATION SCENARIOS (High IGST values exceeding typical limits)
(2, 'INV-MH-007', '2024-03-26', 580000.00, 104400.00, 0.00, 0.00, 104400.00, 'PAID', 'Karnataka', 0),
(9, 'INV-GJ-004', '2024-03-27', 620000.00, 111600.00, 0.00, 0.00, 111600.00, 'UNPAID', 'Delhi', 0),
(17, 'INV-ST-004', '2024-03-28', 750000.00, 135000.00, 0.00, 0.00, 135000.00, 'PAID', 'Maharashtra', 0),
(1, 'INV-KA-006', '2024-03-29', 485000.00, 87300.00, 43650.00, 43650.00, 0.00, 'PAID', 'Karnataka', 0),
(4, 'INV-TN-005', '2024-03-30', 525000.00, 94500.00, 0.00, 0.00, 94500.00, 'OVERDUE', 'Kerala', 0),

-- Additional mixed scenarios
(3, 'INV-DL-006', '2024-01-11', 52000.00, 9360.00, 4680.00, 4680.00, 0.00, 'PAID', 'Delhi', 0),
(5, 'INV-TS-004', '2024-01-17', 91000.00, 16380.00, 0.00, 0.00, 16380.00, 'PAID', 'Karnataka', 0),
(6, 'INV-WB-003', '2024-01-23', 107000.00, 19260.00, 0.00, 0.00, 19260.00, 'PAID', 'Odisha', 0),
(7, 'INV-PN-003', '2024-02-04', 64000.00, 11520.00, 5760.00, 5760.00, 0.00, 'PAID', 'Maharashtra', 0),
(8, 'INV-RJ-004', '2024-02-07', 139000.00, 25020.00, 0.00, 0.00, 25020.00, 'PAID', 'Gujarat', 0),
(10, 'INV-UP-003', '2024-02-13', 77000.00, 13860.00, 6930.00, 6930.00, 0.00, 'OVERDUE', 'Uttar Pradesh', 0),
(11, 'INV-KL-005', '2024-02-18', 101000.00, 18180.00, 9090.00, 9090.00, 0.00, 'PAID', 'Kerala', 0),
(12, 'INV-CH-003', '2024-02-27', 84000.00, 15120.00, 0.00, 0.00, 15120.00, 'PAID', 'Punjab', 0),
(13, 'INV-AS-003', '2024-03-01', 93000.00, 16740.00, 8370.00, 8370.00, 0.00, 'PAID', 'Assam', 0),
(14, 'INV-MP-003', '2024-03-04', 119000.00, 21420.00, 0.00, 0.00, 21420.00, 'PAID', 'Chhattisgarh', 0),
(15, 'INV-AP-004', '2024-03-06', 75000.00, 13500.00, 6750.00, 6750.00, 0.00, 'PAID', 'Andhra Pradesh', 0),
(16, 'INV-BP-002', '2024-03-09', 126000.00, 22680.00, 11340.00, 11340.00, 0.00, 'UNPAID', 'Madhya Pradesh', 0),
(19, 'INV-NG-002', '2024-03-13', 82000.00, 14760.00, 7380.00, 7380.00, 0.00, 'PAID', 'Maharashtra', 0),
(20, 'INV-BR-003', '2024-03-17', 97000.00, 17460.00, 0.00, 0.00, 17460.00, 'PAID', 'West Bengal', 0),
(1, 'INV-KA-007', '2024-03-21', 111000.00, 19980.00, 9990.00, 9990.00, 0.00, 'PAID', 'Karnataka', 0);

-- ============================================
-- Seed Data: Invoice Items (300+ items across all invoices)
-- ============================================

-- Items for INV-KA-001 (Vendor 1)
INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
(1, 'Laptop Dell Inspiron', '84713000', 5, 8000.00, 18.00),
(1, 'Wireless Mouse', '84716060', 10, 500.00, 18.00),
(1, 'USB Cable Type-C', '85444900', 20, 200.00, 18.00);

-- Items for INV-KA-002
INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
(2, 'Monitor 24 inch LED', '85285200', 8, 7500.00, 18.00),
(2, 'Keyboard Mechanical', '84716020', 10, 1500.00, 18.00);

-- Items for INV-KA-003
INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
(3, 'Server Rack 42U', '84733020', 2, 50000.00, 18.00),
(3, 'Network Switch 24 Port', '85176200', 3, 6666.67, 18.00);

-- Items for INV-KA-004
INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
(4, 'Printer Laser Color', '84433210', 5, 14166.67, 18.00),
(4, 'Scanner Flatbed', '84716070', 3, 4166.67, 18.00);

-- Items for INV-KA-005 (Reverse Charge)
INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
(5, 'Software License Annual', '85234920', 10, 7916.67, 18.00),
(5, 'Cloud Storage 1TB', '85234930', 5, 3166.67, 18.00);

-- Items for INV-MH-001
INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
(6, 'LED TV 55 inch', '85287100', 6, 11111.11, 18.00),
(6, 'Soundbar Premium', '85182200', 4, 3333.33, 18.00);

-- Items for INV-MH-002
INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
(7, 'Refrigerator 500L', '84182100', 5, 18333.33, 18.00),
(7, 'Microwave Oven', '85165000', 3, 4166.67, 18.00);

-- Items for INV-MH-003
INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
(8, 'Air Conditioner 1.5 Ton', '84151010', 4, 13541.67, 18.00),
(8, 'Washing Machine 7kg', '84501100', 2, 10833.33, 18.00);

-- Items for INV-MH-004
INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
(9, 'Home Theater System', '85279100', 10, 12500.00, 18.00);

-- Items for INV-MH-005
INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
(10, 'Tablet Android 10 inch', '84713090', 8, 9583.33, 18.00),
(10, 'Power Bank 20000mAh', '85076000', 12, 916.67, 18.00);

-- Continue pattern for remaining invoices (abbreviated for brevity)
-- Delhi invoices
INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
(15, 'Drill Machine Electric', '84672100', 15, 3777.78, 18.00),
(15, 'Angle Grinder', '84672900', 10, 3166.67, 18.00);

INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
(16, 'Welding Machine', '85151100', 8, 15138.89, 18.00),
(16, 'Safety Helmet', '65061000', 50, 416.67, 18.00);

-- Tamil Nadu invoices
INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
(18, 'Cotton Fabric Plain', '52081000', 100, 791.67, 18.00),
(18, 'Polyester Thread', '54024400', 200, 83.33, 18.00);

INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
(19, 'Silk Saree Traditional', '50071000', 20, 4666.67, 18.00),
(19, 'Embroidery Material', '58109900', 50, 333.33, 18.00);

-- Telangana invoices
INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
(23, 'Rice Basmati 25kg', '10063020', 50, 1716.67, 18.00),
(23, 'Wheat Flour 10kg', '11010010', 100, 291.67, 18.00);

-- Adding more diverse items across different categories
INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
-- Electronics
(11, 'Mobile Phone Smartphone', '85171200', 10, 3750.00, 18.00),
(12, 'Laptop Charger', '85044030', 15, 2366.67, 18.00),
(13, 'HDMI Cable 2m', '85444900', 25, 366.67, 18.00),
(14, 'External Hard Drive 2TB', '84717050', 12, 3888.89, 18.00),

-- Furniture
(24, 'Office Chair Executive', '94013000', 20, 3166.67, 18.00),
(25, 'Computer Table', '94036000', 15, 4888.89, 18.00),

-- Automotive
(20, 'Car Battery 12V', '85071000', 10, 6333.33, 18.00),
(21, 'Engine Oil 5L', '27101980', 25, 2333.33, 18.00),

-- Medical
(41, 'Disposable Syringes', '90183100', 1000, 6.42, 18.00),
(42, 'Surgical Gloves Box', '40151900', 50, 1533.33, 18.00),

-- Construction  
(30, 'Cement Portland 50kg', '25232900', 200, 291.67, 18.00),
(31, 'Steel TMT Bars 12mm', '72142000', 100, 433.33, 18.00),

-- Chemicals
(33, 'Sodium Hydroxide 25kg', '28151100', 30, 2611.11, 18.00),
(34, 'Sulfuric Acid Industrial', '28070010', 20, 3916.67, 18.00),

-- Spices
(35, 'Black Pepper Whole', '09041100', 50, 1600.00, 18.00),
(36, 'Cardamom Green', '09083100', 30, 3166.67, 18.00),
(37, 'Turmeric Powder', '09103020', 100, 950.00, 18.00),

-- Handicrafts
(38, 'Wooden Carved Statue', '44201000', 15, 4000.00, 18.00),
(39, 'Brass Handicraft Items', '74199990', 25, 2366.67, 18.00),

-- Diamonds and Jewelry
(43, 'Diamond Polished 1 Carat', '71023900', 5, 34166.67, 18.00),
(44, 'Gold Jewelry 22K', '71131900', 3, 49444.44, 18.00),

-- Automotive Parts
(47, 'Brake Pads Set', '87083000', 30, 2027.78, 18.00),
(48, 'Air Filter Engine', '84212300', 40, 1458.33, 18.00),

-- Logistics
(49, 'Cardboard Boxes Large', '48191000', 500, 125.00, 18.00),
(50, 'Pallet Wooden', '44151000', 100, 458.33, 18.00),

-- Agricultural
(51, 'Fertilizer NPK', '31052000', 100, 541.67, 18.00),
(52, 'Pesticide Spray', '38089390', 50, 1400.00, 18.00);

-- Add items for high-value violation invoices (65-69 map to actual invoices 81-85)
INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
(81, 'Industrial Machinery CNC', '84561000', 2, 483333.33, 18.00),
(82, 'Manufacturing Robot', '84798900', 3, 173611.11, 18.00),
(83, 'Heavy Equipment Loader', '84295100', 1, 625000.00, 18.00),
(84, 'Data Center Server Rack', '84733020', 5, 81083.33, 18.00),
(85, 'Telecom Equipment Base Station', '85176200', 4, 109583.33, 18.00);

-- Fill remaining invoices with varied items (using actual invoice IDs)
INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES  
(20, 'Cotton Shirts Readymade', '62052000', 50, 750.00, 18.00),
(21, 'Plastic Containers', '39231000', 100, 558.33, 18.00),
(22, 'Glass Bottles 1L', '70109000', 200, 270.83, 18.00),
(23, 'Aluminum Foil Roll', '76071100', 150, 430.56, 18.00),
(24, 'Paper A4 Size Ream', '48025700', 100, 658.33, 18.00),
(25, 'Ink Cartridge Printer', '84439959', 40, 1645.83, 18.00),
(26, 'Paint Emulsion 20L', '32091000', 25, 3333.33, 18.00),
(27, 'LED Bulb 9W', '85395000', 200, 260.42, 18.00),
(28, 'Stainless Steel Utensils', '73239300', 100, 708.33, 18.00),
(29, 'Ceramic Tiles 60x60cm', '69072100', 500, 145.83, 18.00),
(30, 'Bicycle Mountain Bike', '87120030', 15, 4527.78, 18.00),
(31, 'Sports Equipment Cricket Bat', '95066100', 30, 2222.22, 18.00),
(32, 'Toys Educational Puzzle', '95030010', 100, 645.83, 18.00),
(33, 'Books Printed English', '49011000', 200, 337.50, 18.00),
(34, 'Leather Wallet', '42023100', 80, 879.17, 18.00),
(35, 'Footwear Sports Shoes', '64041100', 60, 1180.56, 18.00),
(36, 'Garments Jeans Denim', '62034200', 70, 964.29, 18.00),
(37, 'Watch Digital', '91021100', 25, 2633.33, 18.00),
(38, 'Sunglasses UV Protection', '90041000', 50, 1333.33, 18.00),
(39, 'Cosmetics Face Cream', '33049900', 100, 695.83, 18.00),
(40, 'Perfume Eau de Toilette', '33030010', 40, 1770.83, 18.00);

-- ============================================
-- Create Read-Only User for Application
-- ============================================
CREATE USER IF NOT EXISTS 'gst_user'@'%' IDENTIFIED BY 'gstpassword123';
GRANT SELECT ON gst_db.* TO 'gst_user'@'%';
FLUSH PRIVILEGES;

-- ============================================
-- Verification Queries
-- ============================================
-- SELECT COUNT(*) as total_vendors FROM vendors;
-- SELECT COUNT(*) as total_invoices FROM invoices;
-- SELECT COUNT(*) as total_items FROM invoice_items;
-- SELECT status, COUNT(*) as count FROM invoices GROUP BY status;
-- SELECT SUM(cgst + sgst + igst) as total_tax_collected FROM invoices;
