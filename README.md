# AI Demo Generator

The AI Demo Generator is a Streamlit-based tool that helps you quickly generate and iterate on code based on your use case descriptions. It leverages OpenAI to create detailed descriptions and corresponding code, allowing for easy editing and management of demos.

## Features

- **Use Case Description**: Describe your desired functionality in natural language.
- **AI-powered Code Generation**: Automatically generate detailed descriptions and corresponding code.
- **Code Execution**: Run the generated code and see results immediately.
- **Interactive Editing**: Make changes to the generated code through natural language requests.
- **Demo Management**: Save, view, load, and delete demos for future reference.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/kmavrodis/demo-generator-with-openai.git
   cd ai-demo-generator
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables in a `.env` file:
   ```
   AZURE_WHISPER_KEY=your_azure_whisper_key
   AZURE_WHISPER_DEPLOYMENT=your_azure_whisper_deployment
   AZURE_WHISPER_ENDPOINT=your_azure_whisper_endpoint
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_DEPLOYMENT_NAME=your_openai_deployment_name
   OPENAI_ENDPOINT=your_openai_endpoint
   DOCUMENT_INTELLIGENCE_ENDPOINT=your_document_intelligence_endpoint
   DOCUMENT_INTELLIGENCE_KEY=your_document_intelligence_key
   ```

## Usage

Run the Streamlit app:
```
streamlit run app.py
```

Follow the instructions in the app to:
1. Describe your use case
2. Generate a demo
3. Run the generated code
4. Edit the code as needed
5. Manage your demos

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
