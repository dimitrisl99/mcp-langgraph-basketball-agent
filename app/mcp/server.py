from mcp.server.fastmcp import FastMCP #FastMCP --> easy way to create MCP server

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


#Αν τρέχω αυτό το αρχείο απευθείας, τότε κάνε το παρακάτω :
if __name__ == "__main__":
    mcp.run()