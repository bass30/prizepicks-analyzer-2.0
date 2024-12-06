import argparse
import pandas as pd
import numpy as np
from typing import Dict, Any
import asyncio
from data_fetcher import SportDataFetcher

class PrizePicskAnalyzer:
    def __init__(self, sport: str):
        """
        Initialize the analyzer for a specific sport
        
        :param sport: 'basketball' or 'football'
        """
        self.sport = sport
        self.data_fetcher = SportDataFetcher()
    
    async def analyze_player_async(self, player_name: str, betting_line: float) -> Dict[str, Any]:
        """
        Analyze player performance against betting line
        
        :param player_name: Name of the player
        :param betting_line: Current betting line for the player
        :return: Analysis results
        """
        try:
            # Fetch comprehensive player data
            player_data = await self.data_fetcher.get_complete_player_data(player_name, self.sport)
            
            if not player_data:
                return {
                    'error': f'Could not fetch data for {player_name}',
                    'success': False
                }
            
            # Calculate performance metrics
            metrics = self._calculate_metrics(player_data)
            
            # Compare to betting line
            analysis = self._analyze_performance(metrics, betting_line)
            
            # Add injury and matchup analysis if available
            injury_analysis = self._analyze_injury_status(player_data)
            matchup_analysis = self._analyze_matchup(player_data)
            
            return {
                'player_name': player_name,
                'avg_performance': metrics['avg_performance'],
                'betting_line': betting_line,
                'performance_diff': metrics['avg_performance'] - betting_line,
                'recommendation': analysis['recommendation'],
                'confidence_score': analysis['confidence'],
                'recent_games': metrics['recent_games'],
                'injury_status': injury_analysis,
                'matchup_analysis': matchup_analysis,
                'success': True
            }
            
        except Exception as e:
            print(f"Error analyzing player: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    def analyze_player(self, player_name: str, betting_line: float) -> Dict[str, Any]:
        """
        Synchronous wrapper for analyze_player_async
        """
        return asyncio.run(self.analyze_player_async(player_name, betting_line))
    
    def _calculate_metrics(self, player_data: Dict) -> Dict[str, Any]:
        """Calculate performance metrics from player data"""
        metrics = {'recent_games': []}
        
        if self.sport == 'basketball':
            # Combine stats from different sources
            recent_games = (
                player_data.get('yahoo_stats', {}).get('recent_games', []) +
                player_data.get('espn_stats', {}).get('recent_games', [])
            )
            
            if recent_games:
                # Calculate average points (or relevant stat based on betting type)
                points = [game.get('points', 0) for game in recent_games if 'points' in game]
                metrics['avg_performance'] = np.mean(points) if points else 0
                metrics['recent_games'] = recent_games[:5]  # Last 5 games
                
        else:  # football
            recent_games = player_data.get('espn_stats', {}).get('recent_games', [])
            
            if recent_games:
                # Calculate average yards (or relevant stat based on betting type)
                total_yards = [
                    game.get('passing_yards', 0) + game.get('rushing_yards', 0)
                    for game in recent_games
                ]
                metrics['avg_performance'] = np.mean(total_yards) if total_yards else 0
                metrics['recent_games'] = recent_games[:5]
        
        return metrics
    
    def _analyze_performance(self, metrics: Dict, betting_line: float) -> Dict[str, Any]:
        """Analyze performance metrics against betting line"""
        avg_performance = metrics['avg_performance']
        recent_games = metrics['recent_games']
        
        # Calculate consistency and trend
        performances = [game.get('points', 0) for game in recent_games]
        consistency = np.std(performances) if performances else 0
        
        # Simple trend analysis
        trend = 0
        if len(performances) >= 2:
            trend = performances[0] - performances[-1]  # Positive means improving
        
        # Calculate confidence score (0-100)
        confidence = 50  # Base confidence
        
        # Adjust based on consistency (lower std dev = higher confidence)
        if consistency > 0:
            confidence += (20 * (1 / consistency))
        
        # Adjust based on trend
        confidence += (10 * (1 if trend > 0 else -1))
        
        # Clip confidence to 0-100 range
        confidence = max(min(confidence, 100), 0)
        
        return {
            'recommendation': 'Over' if avg_performance > betting_line else 'Under',
            'confidence': confidence
        }
    
    def _analyze_injury_status(self, player_data: Dict) -> Dict[str, Any]:
        """Analyze player injury status"""
        # Extract injury information from ESPN or Yahoo data
        espn_stats = player_data.get('espn_stats', {})
        injury_status = espn_stats.get('injury_status', 'Unknown')
        
        return {
            'status': injury_status,
            'details': espn_stats.get('injury_details', ''),
            'last_updated': espn_stats.get('injury_update_date', '')
        }
    
    def _analyze_matchup(self, player_data: Dict) -> Dict[str, Any]:
        """Analyze player matchup"""
        espn_stats = player_data.get('espn_stats', {})
        
        return {
            'opponent': espn_stats.get('next_opponent', 'Unknown'),
            'opponent_rank': espn_stats.get('opponent_rank', 'Unknown'),
            'home_away': espn_stats.get('game_location', 'Unknown'),
            'rest_days': espn_stats.get('days_rest', 'Unknown')
        }
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'data_fetcher'):
            self.data_fetcher.close()

def main():
    parser = argparse.ArgumentParser(description='PrizePicks Performance Analyzer')
    parser.add_argument('--sport', type=str, required=True, 
                        choices=['basketball', 'football'], 
                        help='Sport to analyze')
    parser.add_argument('--player', type=str, required=True, 
                        help='Player name to analyze')
    parser.add_argument('--line', type=float, required=True, 
                        help='Betting line for the player')
    
    args = parser.parse_args()
    
    analyzer = PrizePicskAnalyzer(args.sport)
    result = analyzer.analyze_player(args.player, args.line)
    
    print(f"Analysis Results for {args.player}:")
    for key, value in result.items():
        print(f"{key}: {value}")

if __name__ == '__main__':
    main()
