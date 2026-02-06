import sqlparse

query = """SELECT
 i.invoice_id,
 i.invoice_number,
 v.vendor_name,
 i.date,
 FORMAT(i.total_amount, 2) AS total_amount,
 FORMAT(i.igst, 2) AS igst_amount
FROM invoices i
JOIN vendors v
 ON i.vendor_id = v.vendor_id
WHERE
 v.state = 'Karnataka' AND i.igst > 0
ORDER BY
 i.date DESC"""

print(f"Original Query:\n{query}\n")

parsed = sqlparse.parse(query)
print(f"Parsed count: {len(parsed)}")

if parsed:
    stmt = parsed[0]
    print(f"Statement Type: {stmt.get_type()}")
    print(f"Tokens: {[t.value for t in stmt.tokens]}")
