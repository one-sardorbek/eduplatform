import csv
import pandas as pd
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime
import os
import logging

# Set up logging
logging.basicConfig(filename='export.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class DataExporter:
    def __init__(self, data: Dict):
        """
        Initialize the exporter with data to be exported.
        
        Args:
            data (Dict): Dictionary containing data to export (e.g., {"users": [...], "schedules": [...]})
        """
        self.data = data
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.export_dir = "exports"
        
        # Create export directory if it doesn't exist
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_to_csv(self) -> bool:
        """
        Export data to CSV files (one file per table).
        
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            for key, items in self.data.items():
                if not items:
                    continue
                    
                filename = os.path.join(self.export_dir, f"{self.timestamp}_{key}.csv")
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=items[0].keys())
                    writer.writeheader()
                    writer.writerows(items)
            
            logging.info(f"Successfully exported data to CSV files with timestamp {self.timestamp}")
            return True
        except Exception as e:
            logging.error(f"CSV export failed: {str(e)}")
            return False
    
    def export_to_xlsx(self) -> bool:
        """
        Export data to a single XLSX file with multiple sheets.
        
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            filename = os.path.join(self.export_dir, f"{self.timestamp}_export.xlsx")
            with pd.ExcelWriter(filename) as writer:
                for key, items in self.data.items():
                    if not items:
                        continue
                        
                    df = pd.DataFrame(items)
                    df.to_excel(writer, sheet_name=key, index=False)
            
            logging.info(f"Successfully exported data to XLSX file with timestamp {self.timestamp}")
            return True
        except Exception as e:
            logging.error(f"XLSX export failed: {str(e)}")
            return False
    
    def export_to_sql(self, db_name: str = "eduplatform") -> bool:
        """
        Generate SQL statements for SSMS and optionally create a SQLite database.
        
        Args:
            db_name (str): Name for the SQLite database file
            
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            # Create SQLite database file
            sqlite_file = os.path.join(self.export_dir, f"{db_name}.db")
            conn = sqlite3.connect(sqlite_file)
            cursor = conn.cursor()
            
            # Generate SQL statements file
            sql_file = os.path.join(self.export_dir, f"{self.timestamp}_sql_export.sql")
            with open(sql_file, "w", encoding="utf-8") as f:
                # Write table creation and data insertion statements
                for table_name, items in self.data.items():
                    if not items:
                        continue
                    
                    # Generate CREATE TABLE statement
                    columns = []
                    for col_name, col_value in items[0].items():
                        if isinstance(col_value, int):
                            col_type = "INTEGER"
                        elif isinstance(col_value, float):
                            col_type = "REAL"
                        else:
                            col_type = "TEXT"
                        columns.append(f"{col_name} {col_type}")
                    
                    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
                    create_table_sql += ",\n".join(columns)
                    
                    # Add primary key if 'id' column exists
                    if 'id' in items[0]:
                        create_table_sql += ",\nPRIMARY KEY (id)"
                    
                    create_table_sql += "\n);\n\n"
                    f.write(create_table_sql)
                    
                    # Generate INSERT statements
                    for item in items:
                        columns = ", ".join(item.keys())
                        values = ", ".join([f"'{str(v)}'" if not isinstance(v, (int, float)) else str(v) for v in item.values()])
                        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values});\n"
                        f.write(insert_sql)
                    
                    f.write("\n")
            
            logging.info(f"Successfully generated SQL statements with timestamp {self.timestamp}")
            return True
        except Exception as e:
            logging.error(f"SQL export failed: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()
    
    def export_all(self) -> bool:
        """
        Export data to all formats (CSV, XLSX, SQL).
        
        Returns:
            bool: True if all exports were successful, False otherwise
        """
        csv_success = self.export_to_csv()
        xlsx_success = self.export_to_xlsx()
        sql_success = self.export_to_sql()
        
        return csv_success and xlsx_success and sql_success

def export_data(data: Dict, file_type: str = "all", filename: Optional[str] = None) -> bool:
    """
    Export system data to specified file type(s).
    
    Args:
        data (Dict): Dictionary containing data to export (e.g., {"users": [...], "schedules": [...]})
        file_type (str): File type ("csv", "xlsx", "sql", or "all")
        filename (str, optional): Base filename for the export (without extension)
    
    Returns:
        bool: True if export successful, False otherwise
    """
    exporter = DataExporter(data)
    
    if file_type.lower() == "csv":
        return exporter.export_to_csv()
    elif file_type.lower() == "xlsx":
        return exporter.export_to_xlsx()
    elif file_type.lower() == "sql":
        return exporter.export_to_sql()
    elif file_type.lower() == "all":
        return exporter.export_all()
    else:
        logging.error(f"Unsupported file type: {file_type}")
        return False