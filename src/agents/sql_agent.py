"""
SQL Agent for natural language to SQL conversion and execution.
"""
import logging
from typing import Optional, Dict, Any, List
from ..database.connection import db
from ..utils.llm import llm
from ..utils.security import SQLValidator

logger = logging.getLogger(__name__)


class SQLAgent:
    """Agent for converting natural language queries to SQL and executing them."""
    
    def __init__(self):
        """Initialize SQL agent."""
        self.validator = SQLValidator()
        self.schema_context = self._get_schema_context()
        logger.info("SQL Agent initialized")
    
    def _get_schema_context(self) -> str:
        """Get database schema information for context."""
        schema = """
Database Schema:

1. vendors table:
   - vendor_id (INT, PRIMARY KEY)
   - vendor_name (VARCHAR)
   - gstin (VARCHAR) - GST Identification Number
   - state (VARCHAR)
   - city (VARCHAR)

2. invoices table:
   - invoice_id (INT, PRIMARY KEY)
   - vendor_id (INT, FOREIGN KEY to vendors)
   - invoice_number (VARCHAR)
   - date (DATE)
   - total_amount (DECIMAL)
   - tax_amount (DECIMAL)
   - cgst (DECIMAL) - Central GST
   - sgst (DECIMAL) - State GST
   - igst (DECIMAL) - Integrated GST
   - status (ENUM: 'PAID', 'UNPAID', 'OVERDUE')
   - place_of_supply (VARCHAR)
   - is_reverse_charge (BOOLEAN)

3. invoice_items table:
   - item_id (INT, PRIMARY KEY)
   - invoice_id (INT, FOREIGN KEY to invoices)
   - description (VARCHAR)
   - hsn_code (VARCHAR) - Harmonized System Nomenclature
   - quantity (INT)
   - unit_price (DECIMAL)
   - tax_rate (DECIMAL)

Important Notes:
- Intra-state transactions have CGST and SGST (both are equal, each is half of total tax)
- Inter-state transactions have only IGST (no CGST/SGST)
- tax_amount = cgst + sgst + igst
- Use JOINs to combine data from multiple tables
"""
        return schema
    
    def generate_sql(self, query: str, context: Optional[str] = None) -> str:
        """
        Convert natural language query to SQL.
        
        Args:
            query: Natural language query
            context: Optional RAG context (e.g., GST rules) to inform SQL generation
            
        Returns:
            Generated SQL query
        """
        # Build prompt
        prompt = f"""{self.schema_context}

Task: Convert the following natural language query to a MySQL SELECT query.

Requirements:
- Generate ONLY the SQL query, no explanations
- Use proper JOIN syntax when querying multiple tables
- Format currency values properly
- Use appropriate aggregation functions (SUM, COUNT, AVG, etc.)
- Include ORDER BY and LIMIT clauses when appropriate
- Return valid MySQL syntax

IMPORTANT PATTERNS:

1. **Location-Based Invoice Queries:**
   - When asking about "[State/Location] invoices", use `place_of_supply` NOT `vendor.state`
   - Example: "Karnataka invoices with IGST" means:
     ```sql
     WHERE i.place_of_supply = 'Karnataka' AND i.igst > 0
     ```
   - Only use `vendor.state` if explicitly asking about vendors FROM a location
   - Remember: IGST applies to inter-state transactions (place_of_supply ≠ vendor.state)

2. **Time-Based Aggregation (Monthly/Yearly):**
   - For questions about "monthly" anything, use:
     `GROUP BY YEAR(date), MONTH(date)` or `DATE_FORMAT(date, '%Y-%m')`
   - For totals per month: `SUM(total_amount) as monthly_total`
   
3. **Rule 86B Compliance:**
   - This rule applies to MONTHLY AGGREGATE purchases exceeding ₹50,00,000
   - Query pattern:
     ```sql
     SELECT 
       DATE_FORMAT(date, '%Y-%m') as month,
       SUM(total_amount) as monthly_total,
       COUNT(*) as invoice_count
     FROM invoices
     GROUP BY DATE_FORMAT(date, '%Y-%m')
     HAVING SUM(total_amount) > 5000000
     ```
   - DO NOT check individual invoices > ₹50L, check monthly aggregates!

4. **Compliance Threshold Queries:**
   - When context mentions limits (like ₹50 lakh), apply to aggregates not individuals
   - Include both the threshold check AND supporting invoice details

"""
        
        if context:
            prompt += f"""Additional Context (GST Rules):
{context}

Use this context to inform your SQL query (e.g., if the context mentions specific limits or thresholds, incorporate them).
Pay special attention to whether the rule applies to individual transactions or aggregated amounts.

"""
        
        prompt += f"""Natural Language Query: {query}

SQL Query:"""
        
        try:
            # Generate SQL using LLM
            sql_raw = llm.generate_text(prompt)
            
            # Clean up the response
            sql_query = self._clean_sql(sql_raw)
            
            logger.info(f"Generated SQL: {sql_query}")
            return sql_query
            
        except Exception as e:
            logger.error(f"Failed to generate SQL: {e}")
            raise
    
    def _clean_sql(self, sql: str) -> str:
        """Clean and extract SQL from LLM response."""
        import re
        
        sql = sql.strip()
        
        # Remove markdown code blocks if present
        if sql.startswith("```"):
            lines = sql.split("\n")
            sql = "\n".join(lines[1:-1]) if len(lines) > 2 else sql
        
        # Remove any remaining backticks or 'sql' prefix
        sql = sql.replace("```sql", "").replace("```", "").strip()
        
        # Remove control characters and other non-printable characters
        # Keep only printable ASCII characters, newlines, tabs, and common whitespace
        sql = re.sub(r'[^\x20-\x7E\n\r\t]', '', sql)
        
        # Remove anything after a semicolon (including the semicolon)
        # This prevents issues with extra junk after the query
        sql = sql.split(';')[0].strip()
        
        # Clean up extra whitespace
        sql = ' '.join(sql.split())
        
        # Restore proper formatting for readability (optional, but nice)
        sql = sql.replace(' FROM ', '\nFROM ').replace(' WHERE ', '\nWHERE ').replace(' ORDER BY ', '\nORDER BY ')
        
        return sql.strip()
    
    def execute_sql(self, sql_query: str) -> tuple[bool, List[Dict[str, Any]], Optional[str]]:
        """
        Execute SQL query after validation.
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            Tuple of (success, results, error_message)
        """
        # Validate SQL
        is_valid, error_msg = self.validator.validate_query(sql_query)
        if not is_valid:
            logger.error(f"SQL validation failed: {error_msg}")
            return False, [], f"Security validation failed: {error_msg}"
        
        # Execute query
        try:
            results = db.execute_query(sql_query)
            logger.info(f"Query executed successfully. Returned {len(results)} rows")
            return True, results, None
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return False, [], str(e)
    
    def process_query(self, 
                     natural_language_query: str, 
                     rag_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a natural language query end-to-end.
        
        Args:
            natural_language_query: User's question in natural language
            rag_context: Optional context from RAG agent
            
        Returns:
            Dictionary with sql_query, results, success, and error
        """
        try:
            # Generate SQL
            sql_query = self.generate_sql(natural_language_query, rag_context)
            
            # Execute SQL
            success, results, error = self.execute_sql(sql_query)
            
            return {
                'sql_query': sql_query,
                'results': results,
                'success': success,
                'error': error,
                'row_count': len(results) if success else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to process query: {e}")
            return {
                'sql_query': None,
                'results': [],
                'success': False,
                'error': str(e),
                'row_count': 0
            }
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format SQL results in a human-readable way.
        
        Args:
            results: List of result dictionaries
            
        Returns:
            Formatted string
        """
        if not results:
            return "No results found."
        
        # Build formatted output
        output = f"Found {len(results)} result(s):\n\n"
        
        for i, row in enumerate(results, 1):
            output += f"Result {i}:\n"
            for key, value in row.items():
                # Format currency values
                if isinstance(value, (int, float)) and key in ['total_amount', 'tax_amount', 'cgst', 'sgst', 'igst', 'unit_price']:
                    output += f"  {key}: ₹{value:,.2f}\n"
                else:
                    output += f"  {key}: {value}\n"
            output += "\n"
        
        return output.strip()


# Global SQL agent instance
sql_agent = SQLAgent()
