"""Data validation schemas and quality checkers.

Implements Pydantic schemas for data validation and automated quality control
following institutional standards (completeness ≥95%, consistency 100%).
"""

from datetime import datetime
from typing import Optional, Dict, List
import pandas as pd
import numpy as np
from pydantic import BaseModel, field_validator, Field

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class StockDataSchema(BaseModel):
    """Pydantic schema for validating OHLCV stock data.
    
    Attributes:
        ticker: Stock ticker symbol (format: XXXX.JK for Indonesian stocks)
        date: Trading date
        open: Opening price (must be positive)
        high: High price (must be positive)
        low: Low price (must be positive)
        close: Closing price (must be positive)
        volume: Trading volume (non-negative)
        adjusted_close: Adjusted closing price (optional)
    """
    
    ticker: str = Field(..., pattern=r'^[A-Z]{4}\.JK$')
    date: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: int = Field(..., ge=0)
    adjusted_close: Optional[float] = Field(None, gt=0)
    
    @field_validator('high')
    @classmethod
    def high_gte_low(cls, v: float, info) -> float:
        """Validate high >= low."""
        if 'low' in info.data and v < info.data['low']:
            raise ValueError(f'High price {v} must be >= low price {info.data["low"]}')
        return v
    
    @field_validator('close')
    @classmethod
    def close_within_range(cls, v: float, info) -> float:
        """Validate close within [low, high]."""
        if 'low' in info.data and 'high' in info.data:
            if v < info.data['low'] or v > info.data['high']:
                raise ValueError(
                    f'Close price {v} must be within [{info.data["low"]}, {info.data["high"]}]'
                )
        return v
    
    @field_validator('volume')
    @classmethod
    def volume_reasonable(cls, v: int) -> int:
        """Check for unrealistic volume."""
        if v > 1e10:  # 10 billion shares
            raise ValueError(f'Unrealistic volume: {v}')
        return v
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True


class DataQualityChecker:
    """Automated data quality validation.
    
    Performs comprehensive quality checks following institutional standards:
    - Completeness: ≥95%
    - Consistency: 100%
    - Timeliness: <24h
    - Accuracy: Statistical validation
    
    Examples:
        >>> checker = DataQualityChecker(df)
        >>> report = checker.run_all_checks()
        >>> print(report['overall_status'])
        'PASS'
    """
    
    def __init__(self, data: pd.DataFrame):
        """Initialize data quality checker.
        
        Args:
            data: DataFrame with OHLCV data
        """
        self.data = data
        self.report: Dict = {}
        logger.info(f"Initialized DataQualityChecker with {len(data)} rows")
    
    def run_all_checks(self) -> Dict:
        """Run all quality checks and return comprehensive report.
        
        Returns:
            Dictionary with check results and overall status
        """
        logger.info("Running all quality checks...")
        
        self.check_completeness()
        self.check_consistency()
        self.check_timeliness()
        self.check_accuracy()
        
        return self._generate_report()
    
    def check_completeness(self) -> None:
        """Check for missing data (target: ≥95%)."""
        total_rows = len(self.data)
        missing_rows = self.data.isnull().sum()
        
        completeness = (1 - missing_rows / total_rows) * 100
        
        self.report['completeness'] = {
            'score': float(completeness.mean()),
            'details': completeness.to_dict(),
            'passed': completeness.mean() >= 95
        }
        
        logger.info(f"Completeness check: {completeness.mean():.2f}% (target: ≥95%)")
    
    def check_consistency(self) -> None:
        """Check data consistency rules (target: 100%)."""
        inconsistencies: List[str] = []
        
        # Rule 1: High >= Low
        invalid_hl = self.data[self.data['High'] < self.data['Low']]
        if not invalid_hl.empty:
            inconsistencies.append(f"High < Low: {len(invalid_hl)} rows")
            logger.warning(f"Found {len(invalid_hl)} rows where High < Low")
        
        # Rule 2: Close within [Low, High]
        invalid_close = self.data[
            (self.data['Close'] < self.data['Low']) | 
            (self.data['Close'] > self.data['High'])
        ]
        if not invalid_close.empty:
            inconsistencies.append(f"Close outside [Low,High]: {len(invalid_close)} rows")
            logger.warning(f"Found {len(invalid_close)} rows where Close outside range")
        
        # Rule 3: Volume >= 0
        negative_vol = self.data[self.data['Volume'] < 0]
        if not negative_vol.empty:
            inconsistencies.append(f"Negative volume: {len(negative_vol)} rows")
            logger.warning(f"Found {len(negative_vol)} rows with negative volume")
        
        self.report['consistency'] = {
            'passed': len(inconsistencies) == 0,
            'issues': inconsistencies
        }
        
        status = "PASS" if len(inconsistencies) == 0 else "FAIL"
        logger.info(f"Consistency check: {status}")
    
    def check_timeliness(self) -> None:
        """Check data freshness (target: <24h)."""
        if 'Date' not in self.data.columns:
            logger.warning("'Date' column not found, skipping timeliness check")
            self.report['timeliness'] = {'passed': False, 'reason': 'No date column'}
            return
        
        latest_date = pd.to_datetime(self.data['Date']).max()
        days_old = (datetime.now() - latest_date).days
        
        self.report['timeliness'] = {
            'latest_date': latest_date.strftime('%Y-%m-%d'),
            'days_old': days_old,
            'passed': days_old < 2  # Data must be <2 days old
        }
        
        logger.info(f"Timeliness check: Latest data is {days_old} days old")
    
    def check_accuracy(self) -> None:
        """Statistical accuracy checks."""
        # Check for unrealistic price movements
        returns = self.data['Close'].pct_change()
        extreme_returns = returns[abs(returns) > 0.5]  # >50% daily change
        
        # Check for zero volume days
        zero_volume = self.data[self.data['Volume'] == 0]
        
        self.report['accuracy'] = {
            'extreme_returns_count': len(extreme_returns),
            'zero_volume_days': len(zero_volume),
            'passed': len(extreme_returns) < 5  # Max 5 extreme days acceptable
        }
        
        logger.info(
            f"Accuracy check: {len(extreme_returns)} extreme returns, "
            f"{len(zero_volume)} zero volume days"
        )
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive QC report.
        
        Returns:
            Dictionary with overall status and detailed check results
        """
        all_passed = all(check.get('passed', False) for check in self.report.values())
        
        overall_report = {
            'overall_status': 'PASS' if all_passed else 'FAIL',
            'timestamp': datetime.now().isoformat(),
            'checks': self.report
        }
        
        logger.info(f"Quality control: {overall_report['overall_status']}")
        
        return overall_report
