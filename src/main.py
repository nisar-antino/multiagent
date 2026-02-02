"""
Main CLI interface for the Multi-Agent GST system.
"""
import sys
import json
from pathlib import Path
from colorama import Fore, Style, init
from langchain_core.messages import HumanMessage
from src.graph import graph
from src.utils.logger import setup_logger
from src.database.connection import db

# Initialize colorama for Windows
init(autoreset=True)

# Setup logger
logger = setup_logger('main')


def print_banner():
    """Print welcome banner."""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        {Fore.YELLOW}Multi-Agent GST & Invoice Orchestration System{Fore.CYAN}       ║
║                                                              ║
║  {Fore.GREEN}AI-Powered GST Compliance Analysis{Fore.CYAN}                        ║
║  {Fore.WHITE}Combining Structured Data with Regulatory Knowledge{Fore.CYAN}       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def print_section_header(title: str):
    """Print a section header."""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.YELLOW}{title.center(70)}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def print_answer(answer: str):
    """Print the main answer."""
    print(f"{Fore.GREEN}{answer}{Style.RESET_ALL}")


def print_json_output(data: dict):
    """Print JSON output in a formatted way."""
    json_str = json.dumps(data, indent=2, default=str)
    print(f"{Fore.CYAN}{json_str}{Style.RESET_ALL}")


def run_query(user_query: str) -> dict:
    """
    Run a query through the multi-agent system.
    
    Args:
        user_query: User's question
        
    Returns:
        Dictionary with results
    """
    # Initialize state
    initial_state = {
        'messages': [HumanMessage(content=user_query)],
        'query': user_query,
        'query_type': '',
        'sql_query': '',
        'sql_result': '',
        'rag_context': '',
        'final_answer': '',
        'compliance_flags': {}
    }
    
    # Run through graph
    logger.info(f"Processing query: {user_query}")
    result = graph.invoke(initial_state)
    
    return result


def interactive_mode():
    """Run the CLI in interactive mode."""
    print_banner()
    
    # Check database connection
    print(f"{Fore.YELLOW}Checking database connection...{Style.RESET_ALL}")
    if db.health_check():
        print(f"{Fore.GREEN}✓ Database connected successfully{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.RED}✗ Database connection failed! Please check Docker containers.{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}Run: docker-compose up -d{Style.RESET_ALL}\n")
        sys.exit(1)
    
    # Check vector store
    from src.agents.rag_agent import rag_agent
    doc_count = rag_agent.collection.count() if rag_agent.collection else 0
    if doc_count > 0:
        print(f"{Fore.GREEN}✓ Vector store loaded with {doc_count} document chunks{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.YELLOW}⚠ Vector store is empty. Add GST rule PDFs to data/gst_rules/ and restart.{Style.RESET_ALL}\n")
    
    print(f"{Fore.CYAN}{'─'*70}")
    print(f"{Fore.WHITE}Type your questions about GST invoices and compliance.")
    print(f"{Fore.WHITE}Type 'quit' or 'exit' to end the session.")
    print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}\n")
    
    # Main loop
    while True:
        try:
            # Get user input
            user_input = input(f"{Fore.YELLOW}Query:{Style.RESET_ALL} ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n{Fore.GREEN}Thank you for using the GST Assistant! Goodbye.{Style.RESET_ALL}\n")
                break
            
            if not user_input:
                continue
            
            # Process query
            print(f"\n{Fore.CYAN}Processing...{Style.RESET_ALL}\n")
            
            result = run_query(user_input)
            
            # Display results
            print_section_header("ANSWER")
            print_answer(result['final_answer'])
            
            # Show SQL query if executed
            if result.get('sql_query'):
                print(f"\n{Fore.CYAN}SQL Query Executed:{Style.RESET_ALL}")
                print(f"{Fore.WHITE}{result['sql_query']}{Style.RESET_ALL}")
            
            # Show structured output
            print_section_header("STRUCTURED OUTPUT (JSON)")
            structured_output = {
                'query': user_input,
                'query_type': result.get('query_type', ''),
                'answer': result['final_answer'],
                'compliance_flags': result.get('compliance_flags', {}),
                'sql_executed': result.get('sql_query', ''),
                'has_rag_context': bool(result.get('rag_context', ''))
            }
            print_json_output(structured_output)
            
            print(f"\n{Fore.CYAN}{'─'*70}{Style.RESET_ALL}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Interrupted by user. Exiting...{Style.RESET_ALL}\n")
            break
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}\n")


def main():
    """Main entry point."""
    try:
        # Import config to validate environment
        from src import config
        
        # Run interactive mode
        interactive_mode()
        
    except ValueError as e:
        # Configuration error (e.g., missing API key)
        print(f"{Fore.RED}{str(e)}{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
