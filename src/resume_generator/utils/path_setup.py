"""Path setup utility for project imports"""
import sys
import os


def setup_project_path():
    """Add the src directory to Python path for project imports"""
    # Get the project root directory (where this script is located)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, '..', '..')
    
    # Add to Python path if not already present
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)


def setup_src_path_from_root(file_path):
    """
    Add src directory to Python path from a root-level script.
    
    Args:
        file_path (str): Usually __file__ from the calling script
    """
    root_dir = os.path.dirname(os.path.abspath(file_path))
    src_dir = os.path.join(root_dir, 'src')
    
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)


def setup_test_path_from_tests(file_path):
    """
    Add src directory to Python path from a test file.
    
    Args:
        file_path (str): Usually __file__ from the calling test script
    """
    test_dir = os.path.dirname(os.path.abspath(file_path))
    project_root = os.path.dirname(test_dir)
    src_dir = os.path.join(project_root, 'src')
    
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)