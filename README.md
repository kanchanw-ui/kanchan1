# Invoice QA Agent

An AI-powered application that automatically compares invoices against purchase orders to detect mismatches, duplicates, and anomalies. Built with Streamlit, LangChain, and GPT.

## Features

- 📄 **Multi-Format Support**: Accepts Excel (.xlsx, .xls) and PDF files for both invoices and purchase orders
- 🤖 **AI-Powered Analysis**: Uses GPT-4 via LangChain to intelligently compare documents
- 🔍 **Comprehensive Detection**:
  - Rate mismatches (price discrepancies)
  - Duplicate entries
  - Unusual patterns and anomalies
- 📊 **Interactive Visualizations**: Graphical dashboards with charts and metrics
- 📥 **Multiple Output Formats**: Download results as Excel or PDF reports
- ⚡ **Rule-Based Fallback**: Works even without API key using rule-based comparison

## Technologies

- **Streamlit**: Web application framework
- **LangChain**: AI orchestration framework
- **OpenAI GPT-4**: AI model for intelligent comparison
- **Pandas**: Data manipulation and analysis
- **pdfplumber**: PDF text and table extraction
- **openpyxl**: Excel file generation
- **ReportLab**: PDF report generation
- **Plotly**: Interactive visualizations

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd kanchan1
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. **Start the application**:
```bash
streamlit run app.py
```

2. **Configure OpenAI API Key** (optional but recommended):
   - Enter your OpenAI API key in the sidebar
   - Without API key, the system will use rule-based comparison

3. **Upload Files**:
   - Upload an Invoice file (Excel or PDF)
   - Upload a Purchase Order file (Excel or PDF)

4. **Analyze**:
   - Click "Analyze & Compare" button
   - Wait for the AI to process and compare the documents

5. **Review Results**:
   - View summary metrics
   - Explore interactive visualizations
   - Check detailed reports in tabs (Mismatches, Duplicates, Anomalies)

6. **Download Reports**:
   - Download Excel report with multiple sheets
   - Download PDF report with formatted results

## File Format Requirements

### Excel Files
Should contain columns such as:
- `Item` or `Item Number` or `SKU`
- `Description`
- `Quantity` or `Qty`
- `Unit Price` or `Price` or `Rate`
- `Total` (optional)

The system automatically standardizes column names.

### PDF Files
Should be text-based PDFs (not scanned images) containing:
- Item information
- Quantities
- Prices
- Other relevant invoice/PO data

## Project Structure

```
kanchan1/
├── app.py                 # Main Streamlit application
├── file_parser.py         # PDF and Excel file parsing
├── ai_agent.py           # AI comparison agent using LangChain
├── output_generator.py    # Excel and PDF report generation
├── visualization.py      # Interactive chart generation
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## How It Works

1. **File Parsing**: Extracts structured data from uploaded Excel or PDF files
2. **Data Standardization**: Normalizes column names and formats
3. **AI Comparison**: Uses GPT-4 to intelligently compare invoice and PO data
4. **Rule-Based Validation**: Additional rule-based checks for accuracy
5. **Result Generation**: Creates comprehensive reports with visualizations
6. **Output Export**: Generates downloadable Excel and PDF files

## Acceptance Criteria ✅

- ✅ Upload 1 sample invoice and 1 sample PO
- ✅ System compares values and highlights mismatches
- ✅ Clear flagging of duplicates or anomalies
- ✅ Supports Excel and PDF input formats
- ✅ Output available in Excel and PDF formats
- ✅ Graphical visualization for easy understanding

## Configuration

### Environment Variables

You can set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or enter it directly in the application sidebar.

## Troubleshooting

- **PDF parsing issues**: Ensure PDFs are text-based, not scanned images
- **Column matching**: The system tries to auto-detect columns, but ensure your files have clear headers
- **API errors**: Check your OpenAI API key and account balance
- **Empty results**: Verify that your files contain the expected data format

## License

This project is open source and available for use.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
