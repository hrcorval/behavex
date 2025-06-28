"""
/*
* BehaveX - Agile test wrapper on top of Behave (BDD)
*/

Formatter manager module to handle custom formatters.
"""

import importlib
import os
import sys
from typing import (Any, Dict, Optional,  # pyright: ignore[reportDeprecated]
                    Type)

from behavex.conf_mgr import get_env, get_param

# Formatter Constants
DEFAULT_FORMATTER_DIR = 'report-artifacts'


class FormatterManager:
    """Manager class for handling custom formatters in BehaveX."""

    @staticmethod
    def load_formatter(formatter_spec: str) -> Optional[Type[Any]]: #pyright: ignore[reportDeprecated]
        """
        Load a formatter class from a module path specification.

        Args:
            formatter_spec: String in format "module_path:FormatterClass"

        Returns:
            The formatter class if found, None otherwise
        """
        try:
            if not formatter_spec or ':' not in formatter_spec:
                print("Invalid formatter specification. Format should be 'module_path:FormatterClass'")
                return None

            # Clean up the formatter spec by removing any extra whitespace
            formatter_spec = formatter_spec.strip()
            module_path, class_name = [part.strip() for part in formatter_spec.split(':')]

            # Try to import the module
            try:
                module = importlib.import_module(module_path)
            except ImportError as e:
                # If import fails, try to add the current directory to sys.path
                current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                if current_dir not in sys.path:
                    sys.path.append(current_dir)
                try:
                    module = importlib.import_module(module_path)
                except ImportError:
                    print(f"Could not import module '{module_path}'. Error: {str(e)}")
                    return None

            # Get the formatter class
            if not hasattr(module, class_name):
                print(f"Module '{module_path}' does not contain class '{class_name}'")
                return None

            formatter_class = getattr(module, class_name)
            return formatter_class

        except Exception as e:
            print(f"Error loading formatter {formatter_spec}: {str(e)}")
            return None

    @staticmethod
    def get_formatter_output_dir(formatter_spec: str) -> Optional[str]: #pyright: ignore[reportDeprecated]
        """
        Get the preferred output directory from a formatter class.

        Args:
            formatter_spec: String in format "module_path:FormatterClass"

        Returns:
            The formatter's preferred output directory, or None if not found
        """
        try:
            formatter_class = FormatterManager.load_formatter(formatter_spec)
            if formatter_class and hasattr(formatter_class, 'DEFAULT_OUTPUT_DIR'):
                return formatter_class.DEFAULT_OUTPUT_DIR
        except Exception as e:
            print(f"Warning: Could not load formatter {formatter_spec} to get output directory: {str(e)}")

        return None

    @staticmethod
    def format_results(json_output: Dict[str, Any]) -> None: #pyright: ignore[reportDeprecated]
        """
        Format test results using the specified custom formatter.

        Args:
            json_output: Dictionary containing the test results
        """
        formatter_spec = get_param('formatter')
        if not formatter_spec:
            return

        formatter_class = FormatterManager.load_formatter(formatter_spec)
        if not formatter_class:
            return

        # The formatter will handle its own output directory setup
        # No need to create directories here since formatters manage their own paths

        try:
            formatter = formatter_class()
            # Check if the formatter has the expected method
            if not hasattr(formatter, 'launch_json_formatter'):
                print(f"Formatter {formatter_class.__name__} does not implement required method 'launch_json_formatter'")
                return

            formatter.launch_json_formatter(json_output)
        except Exception as e:
            print(f"Error running formatter {formatter_spec}: {str(e)}")
            import traceback
            traceback.print_exc()
