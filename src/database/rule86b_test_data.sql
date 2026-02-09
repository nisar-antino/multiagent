-- ============================================
-- Rule 86B Test Data
-- ============================================
-- This script adds invoices that trigger Rule 86B violations
-- Rule 86B: If monthly purchases exceed ₹50 lakhs, ITC restricted to 99%
--
-- Strategy: Add multiple invoices in the same month (April 2024)
-- that collectively exceed ₹50,00,000

-- Clear any existing April 2024 invoices first (to avoid duplicates)
DELETE FROM invoice_items WHERE invoice_id IN (
    SELECT invoice_id FROM invoices WHERE DATE_FORMAT(date, '%Y-%m') = '2024-04'
);
DELETE FROM invoices WHERE DATE_FORMAT(date, '%Y-%m') = '2024-04';

-- Add vendor specifically for this test (if not exists)
INSERT INTO vendors (vendor_name, gstin, state, city) VALUES
('High Volume Supplier Ltd', '29HVSL12345F1Z9', 'Karnataka', 'Bangalore')
ON DUPLICATE KEY UPDATE vendor_id=LAST_INSERT_ID(vendor_id);

SET @test_vendor_id = LAST_INSERT_ID();

-- ============================================
-- SCENARIO: April 2024 - Exceeding ₹50 Lakh Monthly Limit
-- ============================================
-- Add 6 invoices in April 2024 totaling ~₹60 lakhs

INSERT INTO invoices (vendor_id, invoice_number, date, total_amount, tax_amount, cgst, sgst, igst, status, place_of_supply, is_reverse_charge) VALUES
-- Invoice 1: ₹12,00,000 (April 2, 2024)
(@test_vendor_id, 'INV-RULE86B-001', '2024-04-02', 1200000.00, 216000.00, 108000.00, 108000.00, 0.00, 'PAID', 'Karnataka', 0),
-- Invoice 2: ₹15,00,000 (April 8, 2024)
(@test_vendor_id, 'INV-RULE86B-002', '2024-04-08', 1500000.00, 270000.00, 135000.00, 135000.00, 0.00, 'PAID', 'Karnataka', 0),
-- Invoice 3: ₹8,50,000 (April 12, 2024)
(@test_vendor_id, 'INV-RULE86B-003', '2024-04-12', 850000.00, 153000.00, 76500.00, 76500.00, 0.00, 'PAID', 'Karnataka', 0),
-- Invoice 4: ₹11,00,000 (April 18, 2024)
(@test_vendor_id, 'INV-RULE86B-004', '2024-04-18', 1100000.00, 198000.00, 99000.00, 99000.00, 0.00, 'PAID', 'Karnataka', 0),
-- Invoice 5: ₹9,25,000 (April 22, 2024)
(@test_vendor_id, 'INV-RULE86B-005', '2024-04-22', 925000.00, 166500.00, 83250.00, 83250.00, 0.00, 'UNPAID', 'Karnataka', 0),
-- Invoice 6: ₹6,75,000 (April 28, 2024)
(@test_vendor_id, 'INV-RULE86B-006', '2024-04-28', 675000.00, 121500.00, 60750.00, 60750.00, 0.00, 'PAID', 'Karnataka', 0);

-- Total for April 2024: ₹63,50,000 (exceeds ₹50 lakh limit by ₹13,50,000)

-- ============================================
-- Add invoice items for these invoices
-- ============================================
SET @inv1 = (SELECT invoice_id FROM invoices WHERE invoice_number = 'INV-RULE86B-001');
SET @inv2 = (SELECT invoice_id FROM invoices WHERE invoice_number = 'INV-RULE86B-002');
SET @inv3 = (SELECT invoice_id FROM invoices WHERE invoice_number = 'INV-RULE86B-003');
SET @inv4 = (SELECT invoice_id FROM invoices WHERE invoice_number = 'INV-RULE86B-004');
SET @inv5 = (SELECT invoice_id FROM invoices WHERE invoice_number = 'INV-RULE86B-005');
SET @inv6 = (SELECT invoice_id FROM invoices WHERE invoice_number = 'INV-RULE86B-006');

INSERT INTO invoice_items (invoice_id, description, hsn_code, quantity, unit_price, tax_rate) VALUES
-- Items for INV-RULE86B-001
(@inv1, 'Industrial Manufacturing Equipment', '84561000', 3, 333333.33, 18.00),
(@inv1, 'Precision Tooling Set', '82071300', 10, 33333.33, 18.00),

-- Items for INV-RULE86B-002
(@inv2, 'CNC Milling Machine', '84562900', 2, 625000.00, 18.00),
(@inv2, 'Measuring Instruments Digital', '90318000', 5, 50000.00, 18.00),

-- Items for INV-RULE86B-003
(@inv3, 'Welding Robot System', '84798900', 1, 708333.33, 18.00),
(@inv3, 'Safety Equipment Industrial', '39269099', 50, 2833.33, 18.00),

-- Items for INV-RULE86B-004
(@inv4, 'Hydraulic Press 200 Ton', '84629900', 2, 458333.33, 18.00),
(@inv4, 'Conveyor Belt System', '84283900', 1, 183333.33, 18.00),

-- Items for INV-RULE86B-005
(@inv5, 'Laser Cutting Machine', '84562100', 1, 770833.33, 18.00),
(@inv5, 'Dust Extraction System', '84212100', 1, 154166.67, 18.00),

-- Items for INV-RULE86B-006
(@inv6, 'Quality Control Equipment', '90318000', 4, 140625.00, 18.00),
(@inv6, 'Material Handling Forklifts', '84272090', 2, 140625.00, 18.00);

-- ============================================
-- Verification Query
-- ============================================
-- Uncomment to verify the data was inserted correctly:
/*
SELECT 
    DATE_FORMAT(date, '%Y-%m') as month,
    COUNT(*) as invoice_count,
    SUM(total_amount) as monthly_total_amount,
    SUM(tax_amount) as monthly_tax_amount,
    CASE 
        WHEN SUM(total_amount) > 5000000 THEN 'EXCEEDS Rule 86B Limit'
        ELSE 'Within Limit'
    END as rule_86b_status
FROM invoices
WHERE DATE_FORMAT(date, '%Y-%m') = '2024-04'
GROUP BY DATE_FORMAT(date, '%Y-%m');
*/
