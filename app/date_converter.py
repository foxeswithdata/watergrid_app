"""
Date Format Converter
====================
Utility to detect and convert dates between dd/mm/YYYY and YYYY-mm-dd formats.
Handles mixed format CSVs and converts everything to a standard format.

Usage:
    from date_converter import standardize_dates, detect_date_format, convert_csv_dates
    
    # Option 1: Convert individual date strings
    date_str = "25/12/2020"
    standardized = standardize_dates(date_str)  # Returns "2020-12-25"
    
    # Option 2: Detect format in a list of dates
    dates = ["25/12/2020", "26/12/2020", "27/12/2020"]
    fmt = detect_date_format(dates)  # Returns "dd/mm/YYYY"
    
    # Option 3: Convert entire CSV file
    df = pd.read_csv("data.csv")
    df = convert_csv_dates(df, date_column='date')
    df['date'] = pd.to_datetime(df['date'])  # Now safe to convert
"""

import pandas as pd
import re
from typing import List, Tuple, Union
from pathlib import Path


# ========================================
# DATE FORMAT DETECTION
# ========================================

def detect_date_format(dates: Union[List[str], pd.Series], allow_mixed: bool = True) -> str:
    """
    Detect the date format from a list of date strings.
    
    Handles:
    - dd/mm/YYYY format (e.g., "25/12/2020")
    - YYYY-mm-dd format (e.g., "2020-12-25")
    - Mixed formats (returns "mixed" if allow_mixed=True)
    - Ambiguous dates (uses unambiguous dates to infer format)
    
    Args:
        dates: List of date strings or pandas Series
        allow_mixed: If True, returns "mixed" for mixed formats; if False, returns most common
    
    Returns:
        String indicating format: "dd/mm/YYYY", "YYYY-mm-dd", "mixed", or "unknown"
    
    Examples:
        >>> detect_date_format(["25/12/2020", "26/12/2020"])
        'dd/mm/YYYY'
        
        >>> detect_date_format(["2020-12-25", "2020-12-26"])
        'YYYY-mm-dd'
        
        >>> detect_date_format(["25/12/2020", "2020-12-26"])
        'mixed'
    """
    
    # Convert Series to list if needed
    if isinstance(dates, pd.Series):
        dates = dates.dropna().tolist()
    
    if not dates:
        return "unknown"
    
    # Patterns for each format
    pattern_ddmmyyyy = r'^\d{1,2}[/-]\d{1,2}[/-]\d{4}$'
    pattern_yyyymmdd = r'^\d{4}[/-]\d{1,2}[/-]\d{1,2}$'
    
    format_counts = {
        'dd/mm/YYYY': 0,
        'YYYY-mm-dd': 0,
        'unknown': 0
    }
    
    # Sample up to 100 dates for efficiency
    sample_size = min(100, len(dates))
    sample_dates = dates[:sample_size]
    
    for date_str in sample_dates:
        date_str = str(date_str).strip()
        
        if re.match(pattern_ddmmyyyy, date_str):
            # Check if it's actually dd/mm by looking at first number
            parts = re.split(r'[/-]', date_str)
            first_num = int(parts[0])
            second_num = int(parts[1])
            
            # If first number > 12, it's definitely dd/mm
            if first_num > 12:
                format_counts['dd/mm/YYYY'] += 1
            # If second number > 12, second is definitely month (so first is day = dd/mm)
            elif second_num > 12:
                format_counts['dd/mm/YYYY'] += 1
            # If first < 12 and second < 12, it's ambiguous (could be either)
            # Mark as unknown for now, will infer from other dates
            else:
                format_counts['unknown'] += 1
        
        elif re.match(pattern_yyyymmdd, date_str):
            format_counts['YYYY-mm-dd'] += 1
        
        else:
            format_counts['unknown'] += 1
    
    # Determine format from unambiguous dates
    ddmm_count = format_counts['dd/mm/YYYY']
    yyyymmdd_count = format_counts['YYYY-mm-dd']
    ambiguous_count = format_counts['unknown']
    
    # If we have clear examples of one format, use that
    if ddmm_count > 0 and yyyymmdd_count == 0:
        return 'dd/mm/YYYY'
    elif yyyymmdd_count > 0 and ddmm_count == 0:
        return 'YYYY-mm-dd'
    elif ddmm_count > 0 and yyyymmdd_count > 0:
        # We have both formats in the data
        if allow_mixed:
            return 'mixed'
        else:
            # Return most common
            return 'dd/mm/YYYY' if ddmm_count >= yyyymmdd_count else 'YYYY-mm-dd'
    else:
        # All ambiguous - make a guess based on year (if 4-digit year comes first, likely YYYY-mm-dd)
        return 'unknown'


# ========================================
# DATE FORMAT CONVERSION
# ========================================

def _infer_date_format(date_str: str) -> str:
    """
    Intelligently infer the format of a single date string.
    
    Handles ambiguous dates by looking at structural clues:
    - If year is 4 digits at the start, likely YYYY-mm-dd
    - If day > 12, definitely dd/mm/YYYY
    - If month > 12, definitely dd/mm/YYYY
    - Default assumption: if no clear indicator, assume dd/mm/YYYY (more common globally)
    
    Args:
        date_str: Single date string
    
    Returns:
        Detected format: "dd/mm/YYYY" or "YYYY-mm-dd"
    """
    
    date_str = str(date_str).strip()
    
    # Pattern matching
    pattern_ddmmyyyy = r'^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$'
    pattern_yyyymmdd = r'^(\d{4})[/-](\d{1,2})[/-](\d{1,2})$'
    
    # Check if matches YYYY-mm-dd format structurally
    match = re.match(pattern_yyyymmdd, date_str)
    if match:
        year_str, month_str, day_str = match.groups()
        # Verify it's a valid YYYY-mm-dd
        month = int(month_str)
        day = int(day_str)
        if 1 <= month <= 12 and 1 <= day <= 31:
            return 'YYYY-mm-dd'
    
    # Check if matches dd/mm/YYYY format
    match = re.match(pattern_ddmmyyyy, date_str)
    if match:
        first_num, second_num, year_str = match.groups()
        first = int(first_num)
        second = int(second_num)
        
        # If first > 12, must be day (dd/mm/YYYY)
        if first > 12:
            return 'dd/mm/YYYY'
        # If second > 12, must be day (so first is month = dd/mm format... wait, second is month position, so it's dd/mm)
        elif second > 12:
            return 'dd/mm/YYYY'
        # If both <= 12, ambiguous. Default to dd/mm/YYYY (more common globally)
        else:
            return 'dd/mm/YYYY'
    
    # Default fallback
    return 'dd/mm/YYYY'


def convert_single_date(date_str: str, from_format: str = None, to_format: str = "YYYY-mm-dd") -> str:
    """
    Convert a single date string from one format to another.
    
    Now handles ambiguous dates intelligently!
    
    Args:
        date_str: Date string to convert
        from_format: Source format ("dd/mm/YYYY", "YYYY-mm-dd", or None for auto-detect)
                    Use None for intelligent detection of ambiguous dates
        to_format: Target format (default: "YYYY-mm-dd")
    
    Returns:
        Converted date string
    
    Examples:
        >>> convert_single_date("25/12/2020", from_format="dd/mm/YYYY")
        '2020-12-25'
        
        >>> convert_single_date("2020-12-25", from_format="YYYY-mm-dd")
        '2020-12-25'
        
        >>> convert_single_date("05/06/2020")  # Ambiguous, auto-detects as dd/mm
        '2020-06-05'
    """
    
    date_str = str(date_str).strip()
    
    # Handle null/empty values
    if not date_str or date_str.lower() in ['nan', 'nat', 'none', '']:
        return date_str
    
    # Auto-detect format if not specified or if it's "mixed"
    if from_format is None or from_format == "mixed":
        from_format = _infer_date_format(date_str)
    
    # If already in target format, return as-is
    if from_format == to_format:
        return date_str
    
    # Parse the date string
    if from_format == "dd/mm/YYYY":
        # Parse dd/mm/YYYY or dd-mm-yyyy variants
        pattern = r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
        match = re.match(pattern, date_str)
        
        if match:
            day, month, year = match.groups()
            day = int(day)
            month = int(month)
            year = int(year)
        else:
            raise ValueError(f"Cannot parse date '{date_str}' as dd/mm/YYYY")
    
    elif from_format == "YYYY-mm-dd":
        # Parse YYYY-mm-dd or YYYY/mm/dd variants
        pattern = r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})'
        match = re.match(pattern, date_str)
        
        if match:
            year, month, day = match.groups()
            year = int(year)
            month = int(month)
            day = int(day)
        else:
            raise ValueError(f"Cannot parse date '{date_str}' as YYYY-mm-dd")
    
    else:
        raise ValueError(f"Unknown format: {from_format}")
    
    # Validate the parsed values
    if not (1 <= month <= 12):
        raise ValueError(f"Invalid month {month} in date '{date_str}'")
    if not (1 <= day <= 31):
        raise ValueError(f"Invalid day {day} in date '{date_str}'")
    
    # Format output based on target format
    if to_format == "YYYY-mm-dd":
        return f"{year:04d}-{month:02d}-{day:02d}"
    elif to_format == "dd/mm/YYYY":
        return f"{day:02d}/{month:02d}/{year:04d}"
    else:
        raise ValueError(f"Unknown target format: {to_format}")


def standardize_dates(dates: Union[str, List[str], pd.Series], 
                     to_format: str = "YYYY-mm-dd") -> Union[str, List[str], pd.Series]:
    """
    Standardize dates by auto-detecting format and converting to target format.
    
    Automatically detects format of input dates and converts to standard format.
    Handles mixed formats within the same input.
    
    Args:
        dates: Single date string, list of dates, or pandas Series
        to_format: Target format (default: "YYYY-mm-dd")
    
    Returns:
        Converted dates (same type as input)
    
    Examples:
        >>> standardize_dates("25/12/2020")
        '2020-12-25'
        
        >>> standardize_dates(["25/12/2020", "2020-12-26"])
        ['2020-12-25', '2020-12-26']
        
        >>> df = pd.DataFrame({'date': ["25/12/2020", "2020-12-26"]})
        >>> df['date'] = standardize_dates(df['date'])
    """
    
    # Handle single string
    if isinstance(dates, str):
        from_format = detect_date_format([dates])
        return convert_single_date(dates, from_format=from_format, to_format=to_format)
    
    # Handle pandas Series
    elif isinstance(dates, pd.Series):
        # Convert each date individually (handles mixed formats)
        converted = dates.apply(
            lambda x: convert_single_date(
                x, 
                from_format=None,  # Auto-detect per date
                to_format=to_format
            ) if pd.notna(x) else x
        )
        return converted
    
    # Handle list
    elif isinstance(dates, list):
        # Convert each date individually (handles mixed formats)
        converted = [
            convert_single_date(d, from_format=None, to_format=to_format)  # Auto-detect per date
            if d and str(d).strip() else d
            for d in dates
        ]
        return converted
    
    else:
        raise TypeError(f"Unsupported type: {type(dates)}")


# ========================================
# CSV FILE CONVERSION
# ========================================

def convert_csv_dates(df: pd.DataFrame, 
                     date_column: str = 'date',
                     to_format: str = "YYYY-mm-dd",
                     inplace: bool = False) -> pd.DataFrame:
    """
    Convert date column in a pandas DataFrame.
    
    Detects date format and converts to standard format.
    Safe for mixed format dates.
    
    Args:
        df: DataFrame with date column
        date_column: Name of the date column (default: 'date')
        to_format: Target format (default: "YYYY-mm-dd")
        inplace: If True, modify DataFrame in place
    
    Returns:
        DataFrame with converted dates (or None if inplace=True)
    
    Examples:
        >>> df = pd.read_csv("data.csv")
        >>> df = convert_csv_dates(df, date_column='date')
        >>> df['date'] = pd.to_datetime(df['date'])
    """
    
    if not inplace:
        df = df.copy()
    
    if date_column not in df.columns:
        raise ValueError(f"Column '{date_column}' not found in DataFrame")
    
    # Standardize the dates
    df[date_column] = standardize_dates(df[date_column], to_format=to_format)
    
    if not inplace:
        return df


def convert_csv_file(input_file: Union[str, Path],
                    output_file: Union[str, Path] = None,
                    date_column: str = 'date',
                    to_format: str = "YYYY-mm-dd") -> pd.DataFrame:
    """
    Convert dates in a CSV file and save to new file.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file (default: input_file with '_converted' suffix)
        date_column: Name of the date column
        to_format: Target format
    
    Returns:
        DataFrame with converted dates
    
    Examples:
        >>> df = convert_csv_file("data.csv", "data_converted.csv")
    """
    
    input_file = Path(input_file)
    
    if not input_file.exists():
        raise FileNotFoundError(f"File not found: {input_file}")
    
    # Default output file name
    if output_file is None:
        output_file = input_file.parent / f"{input_file.stem}_converted.csv"
    else:
        output_file = Path(output_file)
    
    # Read CSV
    print(f"Reading: {input_file}")
    df = pd.read_csv(input_file)
    
    # Convert dates
    print(f"Converting '{date_column}' column...")
    df = convert_csv_dates(df, date_column=date_column, to_format=to_format)
    
    # Save CSV
    df.to_csv(output_file, index=False)
    print(f"Saved: {output_file}")
    
    return df


# ========================================
# BATCH PROCESSING
# ========================================

def convert_multiple_csv_files(folder: Union[str, Path],
                              pattern: str = "*.csv",
                              date_column: str = 'date',
                              to_format: str = "YYYY-mm-dd",
                              output_suffix: str = "_converted") -> None:
    """
    Convert dates in multiple CSV files in a folder.
    
    Args:
        folder: Folder containing CSV files
        pattern: File pattern (default: "*.csv")
        date_column: Name of the date column
        to_format: Target format
        output_suffix: Suffix for output files (default: "_converted")
    
    Examples:
        >>> convert_multiple_csv_files("data/")
    """
    
    folder = Path(folder)
    
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")
    
    csv_files = list(folder.glob(pattern))
    
    if not csv_files:
        print(f"No CSV files found in {folder}")
        return
    
    print(f"Found {len(csv_files)} CSV files to process\n")
    
    for csv_file in csv_files:
        try:
            output_file = csv_file.parent / f"{csv_file.stem}{output_suffix}.csv"
            print(f"Processing: {csv_file.name}")
            convert_csv_file(
                csv_file,
                output_file,
                date_column=date_column,
                to_format=to_format
            )
            print(f"  ✓ Converted to: {output_file.name}\n")
        except Exception as e:
            print(f"  ✗ Error: {e}\n")


# ========================================
# UTILITY FUNCTIONS
# ========================================

def validate_dates(dates: Union[List[str], pd.Series]) -> Tuple[bool, List[str]]:
    """
    Validate that all dates are in a recognizable format.
    
    Returns:
        Tuple of (is_valid, list_of_invalid_dates)
    
    Examples:
        >>> is_valid, invalid = validate_dates(["25/12/2020", "invalid"])
        >>> print(is_valid)
        False
        >>> print(invalid)
        ['invalid']
    """
    
    if isinstance(dates, pd.Series):
        dates = dates.dropna().tolist()
    
    invalid_dates = []
    pattern_ddmmyyyy = r'^\d{1,2}[/-]\d{1,2}[/-]\d{4}$'
    pattern_yyyymmdd = r'^\d{4}[/-]\d{1,2}[/-]\d{1,2}$'
    
    for date_str in dates:
        date_str = str(date_str).strip()
        if date_str and not (re.match(pattern_ddmmyyyy, date_str) or re.match(pattern_yyyymmdd, date_str)):
            invalid_dates.append(date_str)
    
    return len(invalid_dates) == 0, invalid_dates


# ========================================
# INTEGRATION WITH DATA LOADER
# ========================================

def load_csv_with_date_conversion(file_path: Union[str, Path],
                                 date_column: str = 'date',
                                 to_datetime: bool = True) -> pd.DataFrame:
    """
    Load CSV and automatically convert dates to standard format.
    
    Combines loading and date conversion in one step.
    
    Args:
        file_path: Path to CSV file
        date_column: Name of the date column
        to_datetime: If True, convert to pandas datetime after standardizing
    
    Returns:
        DataFrame with standardized dates
    
    Examples:
        >>> df = load_csv_with_date_conversion("data/temperature.csv")
        >>> df['date'].dtype
        datetime64[ns]
    """
    
    # Read CSV
    df = pd.read_csv(file_path)
    
    # Standardize date format
    df = convert_csv_dates(df, date_column=date_column)
    
    # Convert to datetime if requested
    if to_datetime:
        df[date_column] = pd.to_datetime(df[date_column])
    
    return df


# ========================================
# COMMAND LINE INTERFACE
# ========================================

if __name__ == "__main__":
    import sys
    
    """
    Command line usage:
    
    # Convert single file
    python date_converter.py data.csv
    
    # Convert with specific date column
    python date_converter.py data.csv --column date_col
    
    # Convert multiple files in folder
    python date_converter.py folder_path/ --batch
    
    # Validate dates
    python date_converter.py data.csv --validate
    """
    
    if len(sys.argv) < 2:
        print("Usage: python date_converter.py <file_or_folder> [--batch] [--column <name>] [--validate]")
        print("\nExamples:")
        print("  python date_converter.py data.csv")
        print("  python date_converter.py data.csv --column my_date")
        print("  python date_converter.py data/ --batch")
        print("  python date_converter.py data.csv --validate")
        sys.exit(1)
    
    path_arg = sys.argv[1]
    is_batch = "--batch" in sys.argv
    validate_only = "--validate" in sys.argv
    
    # Get date column if specified
    date_col = 'date'
    if "--column" in sys.argv:
        idx = sys.argv.index("--column")
        if idx + 1 < len(sys.argv):
            date_col = sys.argv[idx + 1]
    
    path = Path(path_arg)
    
    if not path.exists():
        print(f"Error: Path not found: {path_arg}")
        sys.exit(1)
    
    # Batch mode
    if is_batch and path.is_dir():
        convert_multiple_csv_files(path, date_column=date_col)
    
    # Validate mode
    elif validate_only and path.is_file():
        df = pd.read_csv(path)
        is_valid, invalid = validate_dates(df[date_col])
        
        print(f"Validating dates in '{date_col}' column...")
        print(f"Total rows: {len(df)}")
        print(f"Valid dates: {len(df) - len(invalid)}")
        print(f"Invalid dates: {len(invalid)}")
        
        if invalid:
            print("\nInvalid dates found:")
            for inv in invalid[:10]:
                print(f"  - {inv}")
            if len(invalid) > 10:
                print(f"  ... and {len(invalid) - 10} more")
    
    # Single file conversion
    elif path.is_file():
        convert_csv_file(path, date_column=date_col)
        print("\n✓ Conversion complete!")
    
    else:
        print(f"Error: Invalid path: {path_arg}")
        sys.exit(1)
