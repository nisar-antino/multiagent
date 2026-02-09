"""
LangGraph state machine for orchestrating agents.
"""
import operator
from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
import logging
from .agents.rag_agent import rag_agent
from .agents.sql_agent import sql_agent
from .utils.llm import llm

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the multi-agent system."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str
    query_type: str  # "data", "regulatory", or "hybrid"
    sql_query: str
    sql_result: str
    rag_context: str
    final_answer: str
    compliance_flags: dict


def classifier_node(state: AgentState) -> AgentState:
    """
    Classify the user query to determine routing.
    
    Routes:
    - "data": Pure data query -> SQL agent only
    - "regulatory": Pure regulatory query -> RAG agent only
    - "hybrid": Requires both RAG (for rules) then SQL (for data)
    """
    query = state['query']
    
    prompt = f"""Analyze this user query and classify it into one of three categories:

1. "data" - Purely factual/data questions about invoices, vendors, amounts, etc.
   Examples: "Show me all invoices from Karnataka", "What is the total tax collected?"

2. "regulatory" - Purely regulatory/legal questions about GST rules.
   Examples: "What is Rule 86B?", "Explain input tax credit limits"

3. "hybrid" - Questions that require understanding GST rules AND querying data.
   Examples: "Show invoices violating Rule 86B", "Find transactions exceeding ITC limits"

User Query: {query}

Respond with ONLY one word: data, regulatory, or hybrid"""
    
    try:
        response = llm.generate_text(prompt).strip().lower()
        
        # Clean response
        if "data" in response:
            query_type = "data"
        elif "regulatory" in response:
            query_type = "regulatory"
        elif "hybrid" in response:
            query_type = "hybrid"
        else:
            # Default to hybrid if unclear
            query_type = "hybrid"
        
        logger.info(f"Query classified as: {query_type}")
        
        state['query_type'] = query_type
        state['messages'].append(AIMessage(content=f"Classified as {query_type} query"))
        
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        state['query_type'] = "hybrid"  # Safe default
    
    return state


def rag_node(state: AgentState) -> AgentState:
    """Retrieve relevant GST rules context."""
    query = state['query']
    
    logger.info("Retrieving GST rules context...")
    context = rag_agent.retrieve_context(query, k=5)
    
    state['rag_context'] = context
    state['messages'].append(AIMessage(content=f"Retrieved {len(context)} chars of context"))
    
    logger.info(f"RAG context retrieved: {len(context)} characters")
    return state


def sql_node(state: AgentState) -> AgentState:
    """Generate and execute SQL query."""
    query = state['query']
    rag_context = state.get('rag_context', '')
    
    logger.info("Processing SQL query...")
    
    # Use RAG context if available (for hybrid queries)
    result = sql_agent.process_query(query, rag_context if rag_context else None)
    
    state['sql_query'] = result.get('sql_query', '')
    
    if result['success']:
        # Format results
        formatted = sql_agent.format_results(result['results'])
        state['sql_result'] = formatted
        state['messages'].append(AIMessage(content=f"Query executed: {result['row_count']} rows"))
    else:
        state['sql_result'] = f"Error: {result['error']}"
        state['messages'].append(AIMessage(content=f"Query failed: {result['error']}"))
    
    logger.info(f"SQL execution complete. Success: {result['success']}")
    return state


def synthesizer_node(state: AgentState) -> AgentState:
    """
    Synthesize final answer from all available context.
    """
    query = state['query']
    query_type = state['query_type']
    rag_context = state.get('rag_context', '')
    sql_result = state.get('sql_result', '')
    sql_query = state.get('sql_query', '')
    
    # Build synthesis prompt
    prompt = f"""You are a GST compliance assistant. Provide a clear, direct, and actionable answer to the user's question.

User Question: {query}

"""
    
    if rag_context:
        prompt += f"""Relevant GST Rules:
{rag_context}

"""
    
    if sql_result:
        prompt += f"""Database Query Results:
{sql_result}

SQL Query Used: {sql_query}

"""
    
    prompt += """Generate a clear, direct answer following these guidelines:

1. **Start with a direct answer:** Begin with "Yes" or "No" to the user's question
2. **List violations clearly:** If violations exist, list them with:
   - Month/Period
   - Amount
   - Threshold exceeded
3. **Keep it concise:** Avoid lengthy explanations unless critical
4. **Be actionable:** Focus on what the data shows, not what's missing
5. **Cite rules briefly:** Reference regulations but don't over-explain

For Rule 86B queries specifically:
- If monthly totals exceed ₹50 lakhs, state "Yes, violations detected"
- List each month with amount and excess
- Briefly mention ITC restriction (99% limit, 1% cash payment)
- Skip technical caveats about missing data

Answer:"""
    
    try:
        answer = llm.generate_text(prompt)
        
        # Ensure answer is a string (handle cases where LLM might return a list or other type)
        if isinstance(answer, list):
            answer = ' '.join(str(item) for item in answer)
        elif not isinstance(answer, str):
            answer = str(answer)
        
        state['final_answer'] = answer
        
        # Extract compliance flags
        compliance_flags = {
            'has_violations': 'violation' in answer.lower() or 'exceed' in answer.lower(),
            'regulatory_cited': bool(rag_context),
            'data_analyzed': bool(sql_result)
        }
        state['compliance_flags'] = compliance_flags
        
        state['messages'].append(AIMessage(content="Final answer synthesized"))
        logger.info("Answer synthesized successfully")
        
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        state['final_answer'] = f"Error synthesizing answer: {e}"
        state['compliance_flags'] = {}
    
    return state


def route_after_classifier(state: AgentState) -> Literal["rag_node", "sql_node"]:
    """Determine next node after classification."""
    query_type = state.get('query_type', 'hybrid')
    
    if query_type == "data":
        return "sql_node"
    else:  # regulatory or hybrid
        return "rag_node"


def route_after_rag(state: AgentState) -> Literal["sql_node", "synthesizer_node"]:
    """Determine next node after RAG."""
    query_type = state.get('query_type', 'hybrid')
    
    if query_type == "regulatory":
        # Pure regulatory query, go straight to synthesis
        return "synthesizer_node"
    else:  # hybrid
        # Need to query SQL with RAG context
        return "sql_node"


def create_graph() -> StateGraph:
    """
    Create the LangGraph state machine.
    
    Flow:
    1. Classifier determines query type
    2. Routes based on type:
       - data: -> SQL -> Synthesizer
       - regulatory: -> RAG -> Synthesizer
       - hybrid: -> RAG -> SQL -> Synthesizer
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("classifier_node", classifier_node)
    workflow.add_node("rag_node", rag_node)
    workflow.add_node("sql_node", sql_node)
    workflow.add_node("synthesizer_node", synthesizer_node)
    
    # Set entry point
    workflow.set_entry_point("classifier_node")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "classifier_node",
        route_after_classifier,
        {
            "rag_node": "rag_node",
            "sql_node": "sql_node"
        }
    )
    
    workflow.add_conditional_edges(
        "rag_node",
        route_after_rag,
        {
            "sql_node": "sql_node",
            "synthesizer_node": "synthesizer_node"
        }
    )
    
    # SQL always goes to synthesizer
    workflow.add_edge("sql_node", "synthesizer_node")
    
    # Synthesizer is the end
    workflow.add_edge("synthesizer_node", END)
    
    return workflow.compile()


# Create global graph instance
graph = create_graph()
logger.info("LangGraph workflow created")
