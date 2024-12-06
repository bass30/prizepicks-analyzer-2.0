# PrizePicks Analyzer

## Overview
A real-time sports betting analyzer that pulls data from multiple sources to provide informed betting recommendations for PrizePicks.

## Features
- Real-time player statistics from ESPN, Yahoo Sports, and other sources
- Advanced performance analysis
- Injury tracking
- Matchup analysis
- Confidence scoring
- Interactive visualizations

## Live Demo
Check out the live demo at: [PrizePicks Analyzer on Streamlit](https://prizepicks-analyzer.streamlit.app)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/prizepicks-analyzer.git
cd prizepicks-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with your API keys:
```
NBA_API_KEY=your_nba_api_key
NFL_API_KEY=your_nfl_api_key
```

4. Run the app:
```bash
streamlit run streamlit_app.py
```

## Usage
1. Select your sport (NBA or NFL)
2. Enter player name
3. Input the betting line
4. Get instant analysis and recommendations

## Technology Stack
- Python
- Streamlit
- Pandas
- Plotly
- ESPN API
- Yahoo Sports API
- BeautifulSoup4
- Selenium

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
MIT
