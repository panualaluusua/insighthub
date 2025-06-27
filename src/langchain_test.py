import langchain
from langchain_community.llms import Ollama

def main():
    """
    Tests that LangChain is installed and can be imported.
    """
    print(f"LangChain version: {langchain.__version__}")
    print("LangChain is installed correctly!")
    
    # Optional: Test a specific integration
    try:
        llm = Ollama(model="llama2")
        print("Successfully initialized a community model.")
    except Exception as e:
        print(f"Could not initialize Ollama, but core LangChain is working. Error: {e}")

if __name__ == "__main__":
    main() 