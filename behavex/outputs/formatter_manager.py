"""
/*
* BehaveX - Agile test wrapper on top of Behave (BDD)
*/

Formatter manager module to handle custom formatters.
"""

import importlib
import os
import sys
from typing import Optional, Type

from behavex.conf_mgr import get_env, get_param


class FormatterManager:
    """Manager class for handling custom formatters in BehaveX."""

    @staticmethod
    def load_formatter(formatter_spec: str) -> Optional[Type]:
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
    def get_formatter_output_dir() -> str:
        """
        Get the output directory for the custom formatter.

        Returns:
            Absolute path to the formatter output directory, or None if no custom directory is specified
        """
        base_output = get_env('OUTPUT', 'output')
        formatter_outdir = get_param('formatter_outdir', '')

        # Return None if no custom formatter output directory is specified
        # This allows formatters to use their own default directories
        if not formatter_outdir or formatter_outdir == 'report_artifacts':
            return None

        return os.path.join(base_output, formatter_outdir)

    @staticmethod
    def format_results(json_output: dict) -> None:
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

        output_dir = FormatterManager.get_formatter_output_dir()

        # Create the output directory only if a custom one is specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        try:
            formatter = formatter_class()
            # Check if the formatter has the expected method
            if not hasattr(formatter, 'parse_json_to_allure'):
                print(f"Formatter {formatter_class.__name__} does not implement required method 'parse_json_to_allure'")
                return

            formatter.parse_json_to_allure(json_output)
        except Exception as e:
            print(f"Error running formatter {formatter_spec}: {str(e)}")
            import traceback
            traceback.print_exc()
