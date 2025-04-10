# RAG System

Welcome to the **RAG System**! This project implements a **Retrieval-Augmented Generation (RAG)** architecture, combining the power of information retrieval and generative AI to deliver accurate and context-aware responses.

## Features

- **Document Retrieval**: Efficiently fetch relevant documents from a knowledge base.
- **Generative AI**: Generate human-like responses using state-of-the-art language models.
- **Seamless Integration**: Combine retrieval and generation for enhanced performance.
- **Customizable Pipelines**: Tailor the system to your specific use case.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/AmirHPartovi/RAG_system.git
   cd RAG_system
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file and configure API keys or other settings as needed.

## Usage

1. **Index Your Data**:
   Prepare your knowledge base and index it using the provided scripts:(import you're pdf in ./data to create your own knowledge base)

   ```bash
   python3 pdf_RAG_refactor.py
   ```

2. **Run the RAG System**:
   start With streamlit:

   ```bash
   streamlit run pdf_RAG_streamlit.py
   ```

   Or Start the system to handle queries in code:

   ```bash
   python3 pdf_RAG_refactor.py"
   ```

3. **Customize**:
   Modify the configuration file to adjust retrieval and generation parameters.

## Example

```bash
python pdf_RAG.py --query "how to find communities in social media graph?"
```

**Output**:

> Retrieval-Augmented Generation (RAG) is a hybrid approach that combines information retrieval with generative AI to produce accurate and contextually relevant responses.

## Project Structure

```
RAG_system/
├── data/               # Knowledge base and indexed data
├── models/             # Pre-trained models and fine-tuning scripts
├── scripts/            # Utility scripts for indexing and querying
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Inspired by advancements in retrieval-augmented generation.
- Built with ❤️ by the RAG System team.

## Contact

For questions or support, please reach out to [a.partovi99@gmail.com](mailto:a.partovi99@gmail.com).
