import sys
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP #FastMCP --> easy way to create MCP server

PROJECT_ROOT = Path(__file__).parents[2] #πρόσβαση στο root του project
sys.path.append(str(PROJECT_ROOT))

from app.rag.retriever import search_playbooks #import retriever

from app.rag.answer_generator import generate_basketball_answer

from app.sql.text_to_sql import answer_sql_question #import text-to-sql

# Create the MCP Server
mcp = FastMCP("MCP RAG SQL Chatbot Server") # " " the name of the server


@mcp.tool() #decorator --> next function ->  become MCP tool
def get_company_info(topic: str) -> str: # Παίρνει string και επιστρέφει string π.χ. products
    """
    Simple demo tool.

    Args:
        topic: The topic we want information about.
               Available values: products, customers, faq

    Returns:
        A text answer with basic company information.
    """

    company_data = {
        "products": (
            "Η εταιρεία διαθέτει προϊόντα σφολιάτας, πίτες, "
            "κρουασάν, vegan επιλογές και κατεψυγμένα αρτοσκευάσματα."
        ),
        "customers": (
            "Οι βασικοί πελάτες περιλαμβάνουν supermarkets, "
            "HoReCa συνεργάτες και σημεία λιανικής."
        ),
        "faq": (
            "Οι συχνές ερωτήσεις αφορούν οδηγίες ψησίματος, "
            "αποθήκευση προϊόντων και διαθέσιμους κωδικούς ανά πελάτη."
        ),
    }

    #clean user's input
    clean_topic = topic.lower().strip() #τα κάνει πεζά + βγάζει κενά απο αρχή και τέλος

    #Αν υπάρχει το αντίστοιχο topic μέσα στο dictionary (π.χ. είναι product, customers, faq) επιστρέφουμε
    #αντίστοιχη πληροφορία

    if clean_topic in company_data:
        return company_data[clean_topic]

    #Αν δεν υπάρχει το topic επιστρέφουμε fallback μήνυμα
    return (
        "Δεν βρέθηκε πληροφορία για αυτό το topic. "
        "Δοκίμασε ένα από τα: products, customers, faq."
    )

#κάνουμε αυτή την function διαθέσιμη ως MCP tool
#Πλέον ο MCP agent θα μπορεί να καλέσει search_basketball_playbooks
@mcp.tool()
def search_basketball_playbooks(query: str, top_k: int = 5) -> str:
    """
    Searches basketball playbooks using the RAG retriever.

    Args:
        query: The user's basketball systems question.
        top_k: Number of relevant chunks to retrieve.

    Returns:
        A formatted text response with relevant playbook chunks and sources.
    """

    results = search_playbooks(query=query, top_k=top_k) #καλούμε rag retriever

    if not results:
        return "Δεν βρέθηκαν σχετικά αποτελέσματα στα playbooks."

    response_parts = []

    for index, result in enumerate(results, start=1):
        response_parts.append(
            f"Result {index}\n"
            f"Source: {result['source']}\n"
            f"Page: {result['page']}\n"
            f"Chunk: {result['chunk_index']}\n"
            f"Text:\n{result['text']}\n"
        )

    return "\n---\n".join(response_parts) #επιστρέφουμε το formatted text

#rag tool
@mcp.tool()
def answer_basketball_question(question: str, top_k: int = 5) -> str:
    """
    Answers a basketball systems question using RAG + local Ollama model.

    Args:
        question: The user's basketball question.
        top_k: Number of retrieved chunks to use.

    Returns:
        A grounded answer based on the basketball playbooks.
    """

    result = generate_basketball_answer(
        question=question,
        top_k=top_k,
    )

    return json.dumps(result, ensure_ascii=False)

#text-to-sql tool
@mcp.tool()
def answer_nba_stats_question(question: str) -> str:
    """
    Answers NBA statistics questions using Text-to-SQL over the local SQLite database.

    Args:
        question: The user's NBA statistics question.

    Returns:
        A SQL-backed answer with the generated query and results.
    """

    answer = answer_sql_question(question)

    return answer

#Αν τρέχω αυτό το αρχείο απευθείας, τότε κάνε το παρακάτω :
if __name__ == "__main__":
    mcp.run()