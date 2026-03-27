import os
import sys
import logging

# Ensure backend directory is in the python path
sys.path.append(os.path.dirname(__file__))

# Configure logging to see all debug messages
logging.basicConfig(level=logging.DEBUG)

from app.model_manager import ModelManager

def main():
    print("Testing ModelManager...")
    manager = ModelManager(os.environ.get("MODEL_ROOT", "../models"))
    manager.verbose = True
    
    # Try fetching the sentiment model
    model = manager.get_sentiment_model("custom")
    if model is None:
        print("Model failed to load.")
    else:
        print("Model loaded successfully!")
    
    # Try fetching category model to test it as well
    print("Testing category model:")
    cat_model = manager.get_category_model()
    if cat_model is None:
        print("Category model failed to load.")
    else:
        print("Category model loaded successfully!")

if __name__ == "__main__":
    main()
