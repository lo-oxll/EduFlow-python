import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, r'c:\Users\Milano\Desktop\1m')

try:
    # Try importing the services module
    import services
    print("services.py imported successfully!")
    
    # Check if RecommendationService exists
    if hasattr(services, 'RecommendationService'):
        print("RecommendationService class found!")
        
        # Try creating an instance
        try:
            rs = services.RecommendationService()
            print("RecommendationService instance created successfully!")
        except Exception as e:
            print(f"Error creating RecommendationService instance: {e}")
    else:
        print("ERROR: RecommendationService class not found in services module!")
        
    # Check if recommendation_service instance exists
    if hasattr(services, 'recommendation_service'):
        print("recommendation_service instance found!")
    else:
        print("ERROR: recommendation_service instance not found!")
        
except Exception as e:
    print(f"Error importing services: {e}")
    import traceback
    traceback.print_exc()
