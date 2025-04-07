# Football Scout Pro

A desktop application for football scouting and data analysis built with Python and PySide6.

## Features

- **Dashboard**: View aggregated player statistics and interactive visualizations
- **Player Profiles**: Detailed player statistics with interactive charts
- **Recommendation System**: Find similar players based on specific criteria using machine learning
- **Data Caching**: Efficient data retrieval with local caching to minimize API calls

## Requirements

- Python 3.10+
- PySide6
- Pandas
- NumPy
- scikit-learn
- requests
- requests-cache
- PyQtGraph
- Matplotlib

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/football-scout-pro.git
cd football-scout-pro
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the API key:
   - Sign up for an API key at [api-football.com](https://api-football.com/)
   - Open `utils/config.py` and replace the `API_KEY` value with your actual API key

## Usage

Run the application:
```bash
python main.py
```

### Dashboard

The dashboard displays aggregated statistics and visualizations. Use the sidebar to:
- Select different leagues and seasons
- Apply filters by position and age
- View top players by rating

### Player Finder

Search for players by:
- Name
- Position
- Team
- Minimum rating

Click on a player to view their detailed profile.

### Recommender

Find players similar to a reference player or based on specific criteria:
1. Enter a reference player name (optional)
2. Select position, minimum rating, and maximum age
3. Check additional criteria like passing ability, defensive skills, etc.
4. Click "Get Recommendations" to see the results

## Project Structure

```
football_scout_pro/
│
├── models/
│   ├── api_client.py       # API integration and caching
│   ├── data_processor.py   # Data processing with Pandas
│   └── recommender.py      # ML-based recommendation system
│
├── views/
│   ├── ui/                 # Qt Designer UI files
│   ├── dashboard_view.py   # Dashboard implementation
│   ├── player_view.py      # Player profile implementation
│   └── charts.py           # Custom visualization components
│
├── controllers/
│   ├── main_controller.py  # Main application logic
│   ├── dashboard_controller.py
│   └── player_controller.py
│
├── utils/
│   └── config.py           # Configuration settings
│
├── main.py                 # Application entry point
└── requirements.txt        # Dependencies
```

## Development

### Architecture

The application follows the Model-View-Controller (MVC) architecture:
- **Models**: Handle data retrieval, processing, and analysis
- **Views**: Display UI components and visualizations
- **Controllers**: Coordinate between models and views, handling user interactions

### UI Design

UI files are created using Qt Designer and can be found in the `views/ui/` directory. To modify the UI:
1. Open the `.ui` files with Qt Designer
2. Make your changes
3. Save the file

### Extending the Application

To add new features:
1. Add necessary model components in the `models/` directory
2. Create new view components in the `views/` directory
3. Implement controllers in the `controllers/` directory
4. Update the main controller to integrate your new feature

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- PySide6 for the UI framework
- PyQtGraph and Matplotlib for the visualizations
- scikit-learn for the machine learning capabilities
- api-football.com for providing the football data API