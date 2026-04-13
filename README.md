# Smart Stock Analysis & Prediction System

A powerful Python-based application for analyzing stock market data, visualizing trends, and predicting future prices using machine learning. Features an interactive desktop dashboard built with Tkinter, supporting Indian markets (NIFTY, SENSEX) and global stocks.

## Features

- 📊 **Real-time Stock Data**: Fetch live stock market data using Yahoo Finance API
- 📈 **Interactive Dashboard**: User-friendly Tkinter GUI for visualization and analysis
- 🤖 **Price Prediction**: Machine learning-based price predictions using Linear Regression and Polynomial Features
- 🌍 **Multi-Market Support**: Analyze Indian markets (NIFTY, SENSEX) and global stocks
- 📉 **Technical Analysis**: Visualize stock trends with advanced charting capabilities
- 💾 **Data Export**: Save and export analysis data to CSV and JSON formats
- 🗄️ **MongoDB Integration**: Optional database support for storing analysis results (optional)

## Prerequisites

- **Python 3.10+**
- pip (Python package manager)
- Internet connection (for API access)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/stock-analyzer.git
cd stock-analyzer
```

### 2. Create a Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) MongoDB Setup

If you want to use the MongoDB feature for storing analysis results:

```bash
pip install pymongo
# Configure your MongoDB connection in the application
```

## Usage

### Running the Application

```bash
python main.py
```

This will launch the interactive Tkinter dashboard where you can:

1. **Enter Stock Ticker**: Input a stock symbol (e.g., NIFTY50, RELIANCE, AAPL)
2. **Select Date Range**: Choose the period for analysis
3. **Visualize Trends**: View price charts and technical indicators
4. **Make Predictions**: Generate price predictions for future dates
5. **Export Data**: Save your analysis results

### Example Stock Symbols

**Indian Markets:**
- NIFTY50.NS - Nifty 50 Index
- SENSEX.BO - BSE Sensex Index
- RELIANCE.NS - Reliance Industries
- TCS.NS - Tata Consultancy Services

**International Markets:**
- AAPL - Apple Inc.
- GOOGL - Google/Alphabet
- MSFT - Microsoft
- AMZN - Amazon

## Dependencies

| Library | Purpose | Version |
|---------|---------|---------|
| pandas | Data manipulation and analysis | ≥1.5.0 |
| numpy | Numerical computing | ≥1.23.0 |
| matplotlib | Data visualization | ≥3.6.0 |
| yfinance | Yahoo Finance API wrapper | ≥0.2.28 |
| scikit-learn | Machine learning algorithms | ≥1.1.0 |
| pymongo | MongoDB integration (optional) | ≥4.3.0 |

## Project Structure

```
stock-analyzer/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── setup.py               # Package setup configuration
├── README.md              # This file
├── .gitignore            # Git ignore rules
└── LICENSE               # Project license
```

## Features in Detail

### Stock Data Analysis
- Real-time price fetching
- Historical data retrieval
- Price change calculations
- Volume analysis

### Predictions
- Linear Regression models
- Polynomial Regression for non-linear patterns
- Future price extrapolation
- Accuracy metrics

### Visualization
- Candlestick charts
- Trend lines
- Moving averages
- Prediction overlays

## Configuration

Edit `main.py` to configure:
- API rate limits
- Default date ranges
- Prediction parameters
- Chart styling

## MongoDB Integration (Optional)

To enable MongoDB support:

1. Install MongoDB locally or use MongoDB Atlas (cloud)
2. Update connection string in the application
3. Configure database and collection names

```python
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "stock_analysis"
```

## Limitations & Known Issues

- Prediction accuracy depends on historical data quality
- Real-time data may have slight delays (15-20 minutes for free tier)
- Large datasets may require optimization
- MongoDB integration is optional and not required for core functionality

## Troubleshooting

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### API Rate Limiting
- Yahoo Finance has rate limits; add delays between requests
- Consider using paid tier for production use

### Tkinter Not Found (Linux)
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

## Performance Tips

1. **Optimize Data Fetching**: Cache historical data when possible
2. **Batch Processing**: Analyze multiple stocks in sequence
3. **Memory Management**: Clear unused data from memory
4. **Database Queries**: Index frequently searched fields in MongoDB

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

Private use only. For license information, see LICENSE file.

## Author

**Aryan Maurya**

## Support

For questions, issues, or suggestions, please open an issue on GitHub or contact the author.

## Disclaimer

This project is for educational and analytical purposes. Stock market predictions are not guaranteed and should not be used as sole investment advice. Always conduct your own research and consult with financial advisors before making investment decisions.

---

**Last Updated**: April 2026  
**Python Version**: 3.10+  
**Status**: Active Development
