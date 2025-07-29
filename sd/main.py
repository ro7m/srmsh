
from rule_based_matcher import RuleBasedIdentityMatcher
from ml_matcher import MLIdentityMatcher
from models import IdentityRecord, SimilarityResult
from config import settings
from loguru import logger
import argparse
import json

def compare_records(record1_data: dict, record2_data: dict) -> dict:
    """Compare two records using both approaches"""
    
    # Create record objects
    record1 = IdentityRecord(**record1_data)
    record2 = IdentityRecord(**record2_data)
    
    # Rule-based approach
    rule_matcher = RuleBasedIdentityMatcher()
    rule_result = rule_matcher.compute_similarity(record1, record2)
    
    # ML-based approach
    ml_matcher = MLIdentityMatcher()
    try:
        # Try to load pre-trained model
        ml_matcher.load_model("models/identity_matcher_model.joblib")
    except FileNotFoundError:
        logger.warning("No pre-trained model found. Training new model...")
        ml_matcher.train(n_samples=1000)  # Quick training for demo
        # In production, you'd want to save the model after training
    
    try:
        ml_similarity = ml_matcher.predict_similarity(record1, record2)
        ml_result = SimilarityResult(
            similarity_score=ml_similarity,
            is_same_person=ml_similarity >= settings.ML_THRESHOLD,
            method="ml_based",
            confidence=ml_similarity  # For ML, confidence is the probability
        )
    except Exception as e:
        logger.error(f"ML prediction failed: {e}")
        ml_result = SimilarityResult(
            similarity_score=0.0,
            is_same_person=False,
            method="ml_based",
            confidence=0.0,
            details={'error': str(e)}
        )
    
    return {
        'rule_based': rule_result.dict(),
        'ml_based': ml_result.dict()
    }

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Identity Matching System')
    parser.add_argument('--record1', type=str, help='First record JSON')
    parser.add_argument('--record2', type=str, help='Second record JSON')
    parser.add_argument('--train', action='store_true', help='Train ML model')
    parser.add_argument('--save-model', type=str, help='Save trained model to file')
    
    args = parser.parse_args()
    
    if args.train:
        logger.info("Training ML model...")
        ml_matcher = MLIdentityMatcher()
        results = ml_matcher.train(n_samples=settings.TRAINING_SAMPLES)
        logger.info(f"Training completed: {results}")
        
        if args.save_model:
            ml_matcher.save_model(args.save_model)
            logger.info(f"Model saved to {args.save_model}")
    
    elif args.record1 and args.record2:
        try:
            record1_data = json.loads(args.record1)
            record2_data = json.loads(args.record2)
            
            results = compare_records(record1_data, record2_data)
            print(json.dumps(results, indent=2))
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON input: {e}")
        except Exception as e:
            logger.error(f"Error comparing records: {e}")
    
    else:
        # Demo mode
        logger.info("Running demo comparison...")
        
        # Test case 1: Same person with email variation
        record1 = {
            'name': 'John Michael Doe',
            'email': 'john.doe@gmail.com',
            'phone': '555-123-4567',
            'address': '123 Main Street, Anytown, USA'
        }
        
        record2 = {
            'name': 'John Doe',
            'email': 'johndoe123@gmail.com',
            'phone': '5551234567',
            'address': '123 Main St, Anytown, USA'
        }
        
        results = compare_records(record1, record2)
        print("Demo Comparison Results:")
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
