from database.db_manager import DatabaseManager
import pandas as pd
import numpy as np

class PerformanceAnalyzer:
    def __init__(self):
        self.db = DatabaseManager()
    
    def analyze_results(self):
        """
        Enhanced analysis including trend and prediction buffer impact
        """
        conn = self.db.get_connection()
        df = pd.read_sql_query("""
            SELECT * FROM trade_logs
        """, conn)
        
        # Analyze trades by trend
        trend_analysis = df.groupby(['market_condition', 'trend']).agg({
            'id': 'count',
            'profit_loss_percent': ['mean', 'std'],
            'prediction_diff': 'mean'
        }).round(4)
        
        # Analyze prediction accuracy vs buffer
        buffer_analysis = df.apply(
            lambda row: abs(row['prediction_diff']) >= 3.0,  # 3% buffer
            axis=1
        ).mean()
        
        results = {
            'trend_analysis': trend_analysis,
            'buffer_effectiveness': buffer_analysis,
            'avg_prediction_lag': df['prediction_lag'].mean()
        }
        
        return results
    
    def _calculate_prediction_lag(self, prediction, entry_price, exit_price):
        """
        Quantifies how far behind Allora's predictions are:
        - Compares predicted price movement vs actual movement
        - Larger differences indicate Allora is "chasing" the price
        - Critical for proving Allora is reactive during volatility
        """
        actual_move = (exit_price - entry_price) / entry_price
        predicted_move = (prediction - entry_price) / entry_price
        return abs(actual_move - predicted_move)
    
    def generate_report(self):
        """
        Creates detailed performance report showing:
        1. High Volatility Performance
           - Expecting larger losses
           - Lower win rates
           - Higher average volatility
        2. Normal Period Performance (control group)
        3. Prediction Lag Analysis
           - Shows Allora's delayed response to price movements
        """
        results = self.analyze_results()
        
        report = """
        Allora Strategy Performance Report
        ================================
        
        High Volatility Periods:
        - Total Trades: {}
        - Average Loss: {:.2f}%
        - Maximum Loss: {:.2f}%
        - Win Rate: {:.2f}%
        - Average Volatility: {:.2f}%
        
        Normal Volatility Periods:
        - Total Trades: {}
        - Average Loss: {:.2f}%
        - Maximum Loss: {:.2f}%
        - Win Rate: {:.2f}%
        - Average Volatility: {:.2f}%
        
        Prediction Lag Analysis:
        - Average Price Movement Lag: {:.2f}%
        """.format(
            results['high_volatility']['total_trades'],
            results['high_volatility']['avg_loss'],
            results['high_volatility']['max_loss'],
            results['high_volatility']['win_rate'] * 100,
            results['high_volatility']['avg_volatility'] * 100,
            results['normal_volatility']['total_trades'],
            results['normal_volatility']['avg_loss'],
            results['normal_volatility']['max_loss'],
            results['normal_volatility']['win_rate'] * 100,
            results['normal_volatility']['avg_volatility'] * 100,
            results['avg_prediction_lag'] * 100
        )
        
        return report 
    
    def analyze_trend_impact(self):
        """
        Analyze how trend filtering affects performance
        """
        query = """
        SELECT 
            trend,
            direction,
            COUNT(*) as total_trades,
            AVG(profit_loss_percent) as avg_pnl,
            market_condition
        FROM trade_logs 
        GROUP BY trend, direction, market_condition
        """
        # Implementation details... 