import sys
sys.path.insert(0, r'c:\Users\Milano\Desktop\1m')

try:
    from services import *
    print("services.py import successful!")
    
    # Test creating a service instance
    service = RecommendationService()
    print("RecommendationService created successfully!")
    
    print("\nAll imports and instantiations passed!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
