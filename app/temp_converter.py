"""
Temperature Unit Converter
==========================
Utility to detect and convert temperatures between Kelvin and Celsius.

Handles mixed unit data and converts everything to Celsius.

Usage:
    from temp_converter import standardize_temperature, detect_temperature_unit
    
    # Option 1: Auto-detect and convert individual value
    temp = standardize_temperature(273.15)  # Returns 0.0 (Celsius)
    
    # Option 2: Detect unit in a dataset
    temps = [273.15, 275.15, 300.0]
    unit = detect_temperature_unit(temps)  # Returns "Kelvin"
    
    # Option 3: Convert entire DataFrame column
    df['temp'] = standardize_temperature(df['temp'])
"""

import pandas as pd
import numpy as np
from typing import Union, List, Tuple


# ========================================
# TEMPERATURE UNIT DETECTION
# ========================================

def detect_temperature_unit(temperatures: Union[List[float], pd.Series]) -> str:
    """
    Detect whether temperatures are in Kelvin or Celsius.
    
    Logic:
    - If most values > 200, likely Kelvin (absolute zero is -273.15°C or 0K)
    - If most values <= 200, likely Celsius
    - Threshold of 200 chosen because:
      * Celsius rarely goes above 150°C in natural observations
      * Kelvin for typical earth temps is 250-310K (−23°C to 37°C)
    
    Args:
        temperatures: List of temperature values or pandas Series
    
    Returns:
        String: "Kelvin", "Celsius", or "mixed"
    
    Examples:
        >>> detect_temperature_unit([273.15, 275.15, 300.0])
        'Kelvin'
        
        >>> detect_temperature_unit([10.0, 15.5, 20.0])
        'Celsius'
        
        >>> detect_temperature_unit([273.15, 20.0, 15.0])
        'mixed'
    """
    
    # Convert Series to list if needed
    if isinstance(temperatures, pd.Series):
        temperatures = temperatures.dropna().tolist()
    
    if not temperatures:
        return "unknown"
    
    # Threshold for detection
    KELVIN_THRESHOLD = 200.0
    
    # Count how many values are above threshold (likely Kelvin)
    above_threshold = sum(1 for t in temperatures if t > KELVIN_THRESHOLD)
    below_threshold = sum(1 for t in temperatures if t <= KELVIN_THRESHOLD)
    
    total = above_threshold + below_threshold
    
    if total == 0:
        return "unknown"
    
    # Calculate percentages
    pct_above = above_threshold / total * 100
    pct_below = below_threshold / total * 100
    
    # If clearly one or the other (>90%), return that
    if pct_above > 90:
        return "Kelvin"
    elif pct_below > 90:
        return "Celsius"
    else:
        # Mixed
        return "mixed"


# ========================================
# TEMPERATURE CONVERSION
# ========================================

def kelvin_to_celsius(kelvin: Union[float, int]) -> float:
    """
    Convert temperature from Kelvin to Celsius.
    
    Formula: Celsius = Kelvin - 273.15
    
    Args:
        kelvin: Temperature in Kelvin
    
    Returns:
        Temperature in Celsius
    
    Examples:
        >>> kelvin_to_celsius(273.15)
        0.0
        >>> kelvin_to_celsius(300)
        26.850000000000023
    """
    if pd.isna(kelvin):
        return kelvin
    return kelvin - 273.15


def celsius_to_kelvin(celsius: Union[float, int]) -> float:
    """
    Convert temperature from Celsius to Kelvin.
    
    Formula: Kelvin = Celsius + 273.15
    
    Args:
        celsius: Temperature in Celsius
    
    Returns:
        Temperature in Kelvin
    
    Examples:
        >>> celsius_to_kelvin(0.0)
        273.15
        >>> celsius_to_kelvin(25)
        298.15
    """
    if pd.isna(celsius):
        return celsius
    return celsius + 273.15


def standardize_temperature(temperatures: Union[float, int, List, pd.Series],
                           threshold: float = 200.0) -> Union[float, List, pd.Series]:
    """
    Standardize temperatures to Celsius.
    
    Auto-detects if data is in Kelvin (values > threshold) and converts to Celsius.
    Handles single values, lists, and pandas Series.
    
    Args:
        temperatures: Temperature value(s) to convert
        threshold: Value above which temperature is considered Kelvin (default: 200.0)
    
    Returns:
        Temperature(s) in Celsius (same type as input)
    
    Examples:
        >>> standardize_temperature(273.15)
        0.0
        
        >>> standardize_temperature([273.15, 275.15, 25.0])
        [0.0, 2.0, 25.0]
        
        >>> df['temp'] = standardize_temperature(df['temp'])
    """
    
    # Handle single value
    if isinstance(temperatures, (int, float)):
        if pd.isna(temperatures):
            return temperatures
        
        if temperatures > threshold:
            return kelvin_to_celsius(temperatures)
        else:
            return temperatures
    
    # Handle pandas Series
    elif isinstance(temperatures, pd.Series):
        # Detect unit from series
        unit = detect_temperature_unit(temperatures)
        
        if unit == "Kelvin":
            # Convert all values
            return temperatures.apply(
                lambda x: kelvin_to_celsius(x) if pd.notna(x) else x
            )
        elif unit == "mixed":
            # Mixed: convert values > threshold, keep others
            return temperatures.apply(
                lambda x: kelvin_to_celsius(x) if (pd.notna(x) and x > threshold) else x
            )
        else:
            # Already Celsius, return as-is
            return temperatures
    
    # Handle list
    elif isinstance(temperatures, list):
        # Detect unit from list
        unit = detect_temperature_unit(temperatures)
        
        if unit == "Kelvin":
            # Convert all values
            return [kelvin_to_celsius(t) if pd.notna(t) else t for t in temperatures]
        elif unit == "mixed":
            # Mixed: convert values > threshold, keep others
            return [kelvin_to_celsius(t) if (pd.notna(t) and t > threshold) else t for t in temperatures]
        else:
            # Already Celsius, return as-is
            return temperatures
    
    else:
        raise TypeError(f"Unsupported type: {type(temperatures)}")


# ========================================
# INTEGRATION WITH DATA LOADING
# ========================================

def standardize_temperature_column(df: pd.DataFrame,
                                  column: str,
                                  threshold: float = 200.0,
                                  inplace: bool = False) -> pd.DataFrame:
    """
    Convert temperature column in DataFrame to Celsius.
    
    Args:
        df: DataFrame with temperature column
        column: Name of the temperature column
        threshold: Value above which is considered Kelvin
        inplace: If True, modify DataFrame in place
    
    Returns:
        DataFrame with converted temperatures (or None if inplace=True)
    
    Examples:
        >>> df = standardize_temperature_column(df, 'temperature')
    """
    
    if not inplace:
        df = df.copy()
    
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    # Standardize the temperatures
    df[column] = standardize_temperature(df[column], threshold=threshold)
    
    if not inplace:
        return df


# ========================================
# VALIDATION & DIAGNOSTICS
# ========================================

def validate_temperatures(temperatures: Union[List[float], pd.Series],
                         min_allowed: float = -100.0,
                         max_allowed: float = 100.0) -> Tuple[bool, List[float]]:
    """
    Validate that temperatures are in reasonable range (after conversion).
    
    Args:
        temperatures: Temperature values to validate
        min_allowed: Minimum reasonable Celsius temperature
        max_allowed: Maximum reasonable Celsius temperature
    
    Returns:
        Tuple of (is_valid, list_of_outliers)
    
    Examples:
        >>> is_valid, outliers = validate_temperatures([0, 25, 100, 500])
        >>> print(is_valid)
        False
        >>> print(outliers)
        [500]
    """
    
    if isinstance(temperatures, pd.Series):
        temperatures = temperatures.dropna().tolist()
    
    outliers = []
    
    for temp in temperatures:
        if pd.isna(temp):
            continue
        if temp < min_allowed or temp > max_allowed:
            outliers.append(temp)
    
    return len(outliers) == 0, outliers


def get_temperature_stats(temperatures: Union[List[float], pd.Series]) -> dict:
    """
    Get statistics about temperatures.
    
    Args:
        temperatures: Temperature values
    
    Returns:
        Dictionary with stats
    
    Examples:
        >>> stats = get_temperature_stats([273.15, 300, 25])
        >>> print(stats['detected_unit'])
        'mixed'
    """
    
    if isinstance(temperatures, pd.Series):
        temps_list = temperatures.dropna().tolist()
    else:
        temps_list = temperatures
    
    if not temps_list:
        return {'error': 'No valid temperatures'}
    
    # Standardize all to Celsius for stats
    celsius_temps = standardize_temperature(temps_list)
    
    return {
        'detected_unit': detect_temperature_unit(temps_list),
        'count': len(temps_list),
        'min': min(celsius_temps),
        'max': max(celsius_temps),
        'mean': np.mean(celsius_temps),
        'median': np.median(celsius_temps),
        'std': np.std(celsius_temps),
    }


# ========================================
# COMMAND LINE INTERFACE
# ========================================

if __name__ == "__main__":
    import sys
    
    """
    Command line usage:
    
    # Convert a CSV file with temperature column
    python temp_converter.py data.csv --column temperature
    
    # Validate temperatures
    python temp_converter.py data.csv --validate
    
    # Show stats
    python temp_converter.py data.csv --stats
    """
    
    if len(sys.argv) < 2:
        print("Usage: python temp_converter.py <file.csv> [--column <name>] [--validate] [--stats]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    # Get column name
    temp_col = 'temperature'
    if "--column" in sys.argv:
        idx = sys.argv.index("--column")
        if idx + 1 < len(sys.argv):
            temp_col = sys.argv[idx + 1]
    
    if temp_col not in df.columns:
        print(f"Error: Column '{temp_col}' not found in file")
        print(f"Available columns: {list(df.columns)}")
        sys.exit(1)
    
    # Show stats
    if "--stats" in sys.argv:
        stats = get_temperature_stats(df[temp_col])
        print(f"Temperature Statistics for '{temp_col}':")
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
    
    # Validate
    elif "--validate" in sys.argv:
        is_valid, outliers = validate_temperatures(df[temp_col])
        print(f"Validating '{temp_col}' column...")
        print(f"Total values: {len(df)}")
        print(f"Valid: {is_valid}")
        if outliers:
            print(f"Outliers found: {len(outliers)}")
            for outlier in outliers[:10]:
                print(f"  - {outlier}")
    
    # Convert
    else:
        unit = detect_temperature_unit(df[temp_col])
        print(f"Detected unit: {unit}")
        print(f"Converting '{temp_col}' to Celsius...")
        
        df = standardize_temperature_column(df, temp_col)
        
        output_file = file_path.replace('.csv', '_celsius.csv')
        df.to_csv(output_file, index=False)
        print(f"Saved to: {output_file}")
