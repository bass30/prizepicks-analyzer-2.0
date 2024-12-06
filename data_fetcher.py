import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from espn_api.basketball import Basketball
from espn_api.football import Football
import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class SportDataFetcher:
    def __init__(self):
        self.setup_selenium()
        self.setup_espn_api()
        
    def setup_selenium(self):
        """Setup Selenium WebDriver with headless mode"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
    def setup_espn_api(self):
        """Setup ESPN API clients"""
        self.espn_nba = Basketball()
        self.espn_nfl = Football()
        
    async def fetch_yahoo_stats(self, player_name, sport):
        """Fetch player stats from Yahoo Sports"""
        sport_code = "nba" if sport == "basketball" else "nfl"
        url = f"https://sports.yahoo.com/{sport_code}/players/{player_name.replace(' ', '-').lower()}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    stats = self._parse_yahoo_stats(soup, sport)
                    return stats
                return None
                
    def fetch_espn_stats(self, player_name, sport):
        """Fetch player stats from ESPN"""
        try:
            if sport == "basketball":
                player = self.espn_nba.player_info(player_name)
                return self._parse_espn_basketball_stats(player)
            else:
                player = self.espn_nfl.player_info(player_name)
                return self._parse_espn_football_stats(player)
        except Exception as e:
            print(f"Error fetching ESPN stats: {e}")
            return None
            
    def fetch_prizepicks_odds(self, player_name):
        """Fetch current PrizePicks odds"""
        # Note: This is a placeholder. You would need to implement the actual
        # PrizePicks API integration or web scraping logic
        url = "https://api.prizepicks.com/projections"  # Replace with actual API endpoint
        headers = {"Authorization": f"Bearer {os.getenv('PRIZEPICKS_API_KEY')}"}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # Parse the response to find the player's odds
                return self._parse_prizepicks_data(data, player_name)
        except Exception as e:
            print(f"Error fetching PrizePicks odds: {e}")
            return None
            
    def _parse_yahoo_stats(self, soup, sport):
        """Parse Yahoo Sports HTML for player stats"""
        stats = {}
        
        if sport == "basketball":
            # Find the stats table
            stats_table = soup.find('div', class_='player-stats')
            if stats_table:
                # Extract recent game stats
                recent_games = []
                for row in stats_table.find_all('tr')[1:6]:  # Last 5 games
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        game_stats = {
                            'date': cols[0].text.strip(),
                            'points': float(cols[2].text.strip()),
                            'rebounds': float(cols[3].text.strip()),
                            'assists': float(cols[4].text.strip())
                        }
                        recent_games.append(game_stats)
                
                stats['recent_games'] = recent_games
                
                # Calculate averages
                if recent_games:
                    stats['avg_points'] = sum(g['points'] for g in recent_games) / len(recent_games)
                    stats['avg_rebounds'] = sum(g['rebounds'] for g in recent_games) / len(recent_games)
                    stats['avg_assists'] = sum(g['assists'] for g in recent_games) / len(recent_games)
        
        return stats
        
    def _parse_espn_basketball_stats(self, player_data):
        """Parse ESPN basketball stats"""
        stats = {
            'name': player_data.name,
            'team': player_data.team,
            'position': player_data.position,
            'recent_games': []
        }
        
        # Get recent game stats
        for game in player_data.stats['2023']:  # Current season
            game_stats = {
                'date': game.date,
                'points': game.points,
                'rebounds': game.rebounds,
                'assists': game.assists,
                'minutes': game.minutes
            }
            stats['recent_games'].append(game_stats)
            
        return stats
        
    def _parse_espn_football_stats(self, player_data):
        """Parse ESPN football stats"""
        stats = {
            'name': player_data.name,
            'team': player_data.team,
            'position': player_data.position,
            'recent_games': []
        }
        
        # Get recent game stats
        for game in player_data.stats['2023']:  # Current season
            game_stats = {
                'date': game.date,
                'passing_yards': game.passing_yards,
                'rushing_yards': game.rushing_yards,
                'touchdowns': game.touchdowns
            }
            stats['recent_games'].append(game_stats)
            
        return stats
        
    def _parse_prizepicks_data(self, data, player_name):
        """Parse PrizePicks API response"""
        projections = []
        
        for projection in data.get('projections', []):
            if projection['player_name'].lower() == player_name.lower():
                projections.append({
                    'stat_type': projection['stat_type'],
                    'line': projection['line'],
                    'timestamp': projection['timestamp']
                })
                
        return projections
        
    async def get_complete_player_data(self, player_name, sport):
        """Get comprehensive player data from multiple sources"""
        # Fetch data from multiple sources concurrently
        yahoo_stats_task = asyncio.create_task(self.fetch_yahoo_stats(player_name, sport))
        espn_stats = self.fetch_espn_stats(player_name, sport)
        prizepicks_odds = self.fetch_prizepicks_odds(player_name)
        
        # Wait for async tasks to complete
        yahoo_stats = await yahoo_stats_task
        
        # Combine data from all sources
        combined_data = {
            'player_name': player_name,
            'sport': sport,
            'yahoo_stats': yahoo_stats,
            'espn_stats': espn_stats,
            'prizepicks_odds': prizepicks_odds,
            'last_updated': datetime.now().isoformat()
        }
        
        return combined_data
        
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()
