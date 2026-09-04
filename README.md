# 🗣️ Natural Language to SQL Query Generator

An intelligent chatbot that converts natural language questions into SQL queries and retrieves data from MySQL databases. This project leverages Large Language Models (LLMs) to enable non-technical users to interact with databases seamlessly.

## 🎯 Project Overview

This application bridges the gap between database systems and users without SQL expertise. By utilizing Google's Gemini LLM and LangChain framework, the system interprets natural language questions, generates accurate SQL queries, and returns formatted results.

**Key Use Cases:**
- Business analysts querying sales data without SQL knowledge
- Healthcare professionals accessing patient records
- Retail managers analyzing inventory and customer data
- Financial teams retrieving transaction information

## ✨ Features

- **Natural Language Processing**: Converts user questions into accurate SQL statements
- **Multi-table Database Support**: Handles complex queries across multiple related tables
- **Intelligent Query Generation**: Uses Google Gemini 2.0 Flash for high-accuracy SQL generation
- **Two Implementation Approaches**:
  - Direct LLM-based query generation
  - Agentic approach with SQL toolkit and validation
- **Quality Evaluation**: Integrated RAGAS (Retrieval Augmented Generation Assessment) for response quality metrics
- **Real-world Dataset**: Includes comprehensive regional sales data with 6 tables

## 🛠️ Technical Stack

- **Language**: Python 3.x
- **LLM Framework**: LangChain
- **AI Model**: Google Gemini 2.0 Flash
- **Database**: MySQL
- **Key Libraries**:
  - `langchain` - LLM orchestration
  - `langchain-google-genai` - Google Gemini integration
  - `pymysql` - Database connectivity
  - `ragas` - Evaluation framework
  - `langgraph` - Agent-based workflow
  - `pandas` - Data manipulation

## 📊 Database Schema

The project works with a comprehensive regional sales database containing:

1. **sales_order** - Order transactions with customer, product, and pricing details
2. **customers** - Customer information and indices
3. **products** - Product catalog
4. **regions** - Geographic data including demographics and location
5. **state_regions** - State-to-region mappings
6. **2017_budgets** - Product budget allocations

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- MySQL Server 5.7+
- Google API Key (for Gemini access)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Text-to-SQL-Chatbot.git
cd Text-to-SQL-Chatbot
```

2. **Install dependencies**
```bash
pip install langchain langchain-google-genai langchain-community pymysql sqlalchemy ragas langgraph
```

3. **Set up MySQL database**
```bash
# Create database
mysql -u root -p
CREATE DATABASE text_to_sql;
USE text_to_sql;
```

4. **Load the data**
```bash
# Import CSV files from Data_CSV folder into your MySQL database
# You can use MySQL Workbench or command-line tools
```

5. **Configure database connection**
   
   Update the connection parameters in the notebooks:
   ```python
   host = 'localhost'
   port = '3306'
   username = 'your_username'
   password = 'your_password'
   database_schema = 'text_to_sql'
   ```

6. **Set up API key**
   
   Add your Google Gemini API key:
   ```python
   os.environ["GOOGLE_API_KEY"] = "your_api_key_here"
   ```

## 💻 Usage

### Basic Query Generation

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.utilities import SQLDatabase

# Initialize database connection
db = SQLDatabase.from_uri("mysql+pymysql://user:pass@localhost:3306/text_to_sql")

# Initialize LLM
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key='YOUR_API_KEY')

# Ask questions in natural language
question = "What is the total sales for Product 1?"
# The system generates and executes the SQL query automatically
```

### Agentic Approach (Advanced)

The agentic implementation includes four specialized tools:
- **QuerySQLDatabaseTool** - Execute SQL queries
- **InfoSQLDatabaseTool** - Get table schemas
- **ListSQLDatabaseTool** - List available tables
- **QuerySQLCheckerTool** - Validate queries before execution

See `Agentic Approach.ipynb` for full implementation.

## 📓 Notebooks

1. **`Gemini Chatbot.ipynb`**
   - Basic implementation using prompt templates
   - Direct SQL generation from natural language

2. **`Gemini Chatbot (including RAGAS).ipynb`**
   - Enhanced version with quality evaluation
   - RAGAS metrics for response assessment
   - Helpfulness and context precision scoring

3. **`Agentic Approach.ipynb`**
   - Agent-based implementation with SQL toolkit
   - Multi-step reasoning with tool validation

4. **`gemini.ipynb`**
   - Experimental implementation and testing

## 📈 Evaluation Metrics

The project includes RAGAS evaluation framework measuring:

- **Context Precision**: Relevance of retrieved database schema
- **Faithfulness**: Accuracy of generated SQL queries
- **Helpfulness Score**: Overall usefulness of responses (1-5 scale)
- **Maliciousness Check**: Safety validation

Example results: Context Precision: 1.0, Helpfulness: 3.8/5

## 🔍 Example Queries

```
Q: "What is the total Line Total for Geiss Company?"
SQL: SELECT SUM(`Line Total`) FROM sales_order WHERE `Customer Name Index` = 
     (SELECT `Customer Index` FROM customers WHERE `Customer Names` = 'Geiss Company')

Q: "How many products are there in the database?"
SQL: SELECT COUNT(*) FROM products

Q: "What was the budget of Product 12?"
SQL: SELECT `2017 Budgets` FROM `2017_budgets` WHERE `Product Name` = 'Product 12'
```

## 🎓 Learning Outcomes

This project demonstrates:
- Integration of LLMs with traditional databases
- Prompt engineering for accurate query generation
- Agent-based architectures for complex workflows
- Evaluation frameworks for AI system quality
- Production-ready database interaction patterns

## 🔮 Future Enhancements

- [ ] Web interface using Streamlit or Flask
- [ ] Support for additional database systems (PostgreSQL, SQLite)
- [ ] Query result visualization with charts
- [ ] Query history and caching
- [ ] Multi-language support
- [ ] Voice input integration
- [ ] Enhanced error handling and query suggestions

## ⚠️ Important Notes

- Replace placeholder API keys before running
- Ensure MySQL server is running before executing notebooks
- The system requires proper database schema to generate accurate queries
- Review generated SQL queries in production environments before execution

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📬 Contact

For questions or feedback about this project, please open an issue in the repository.

---

**Built with ❤️ using LangChain and Google Gemini**
