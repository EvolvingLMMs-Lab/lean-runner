#!/usr/bin/env python3
"""
Test script to demonstrate file support in LeanClient.
"""

import asyncio
from pathlib import Path

from lean_client import LeanClient


async def test_file_support():
    """Test the file support functionality of LeanClient."""
    
    # Create a test Lean file
    test_file = Path("test_proof.lean")
    test_content = """
theorem test_theorem : 1 + 1 = 2 := by
  rw [add_comm]
  rw [add_zero]
  rfl
"""
    
    try:
        # Write test content to file
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"Created test file: {test_file}")
        
        # Initialize client
        client = LeanClient(base_url="http://localhost:8000")
        
        async with client:
            print("\n=== Testing with file path (string) ===")
            try:
                result = await client.check_proof(str(test_file))
                print(f"Result: {result}")
            except Exception as e:
                print(f"Error: {e}")
            
            print("\n=== Testing with Path object ===")
            try:
                result = await client.check_proof(test_file)
                print(f"Result: {result}")
            except Exception as e:
                print(f"Error: {e}")
            
            print("\n=== Testing with string content ===")
            try:
                result = await client.check_proof(test_content)
                print(f"Result: {result}")
            except Exception as e:
                print(f"Error: {e}")
                
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()
            print(f"\nCleaned up test file: {test_file}")


if __name__ == "__main__":
    asyncio.run(test_file_support()) 