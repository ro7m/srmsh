
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib
from typing import Dict, List, Optional
from faker import Faker
import random
import string
import re
from difflib import SequenceMatcher
from jellyfish import jaro_winkler_similarity, soundex
import Levenshtein
from config import settings
from utils import extract_email_username, normalize_phone_number, standardize_address_abbreviations
from loguru import logger
from models import IdentityRecord

class MLIdentityMatcher:
    def __init__(self, model_type: str = "random_forest"):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.fake = Faker()
        self.model_type = model_type
        self.is_trained = False
        
    def _extract_features(self, record1: IdentityRecord, record2: IdentityRecord) -> np.array:
        """Extract comprehensive features for ML model"""
        # Normalize fields
        email1_norm = extract_email_username(record1.email or '')
        email2_norm = extract_email_username(record2.email or '')
        
        name1_norm = re.sub(r'[^\w\s]', '', (record1.name or '').lower()).strip()
        name2_norm = re.sub(r'[^\w\s]', '', (record2.name or '').lower()).strip()
        
        try:
            phone1_norm, _ = normalize_phone_number(record1.phone or '')
            phone2_norm, _ = normalize_phone_number(record2.phone or '')
        except:
            phone1_norm = record1.phone or ''
            phone2_norm = record2.phone or ''
        
        addr1_norm = standardize_address_abbreviations(record1.address or '', settings.ADDRESS_ABBREVIATIONS)
        addr2_norm = standardize_address_abbreviations(record2.address or '', settings.ADDRESS_ABBREVIATIONS)
        
        # Compute similarities
        email_sim = SequenceMatcher(None, email1_norm, email2_norm).ratio() if email1_norm and email2_norm else (1.0 if not email1_norm and not email2_norm else 0.0)
        name_sim = jaro_winkler_similarity(name1_norm, name2_norm) if name1_norm and name2_norm else (1.0 if not name1_norm and not name2_norm else 0.0)
        
        try:
            phonetic_sim = 1.0 if soundex(name1_norm) == soundex(name2_norm) else 0.0
        except:
            phonetic_sim = 0.0
            
        phone_sim = 1.0 if phone1_norm == phone2_norm else 0.0
        address_sim = SequenceMatcher(None, addr1_norm, addr2_norm).ratio() if addr1_norm and addr2_norm else (1.0 if not addr1_norm and not addr2_norm else 0.0)
        
        # Exact matches
        email_exact = 1.0 if email1_norm == email2_norm else 0.0
        name_exact = 1.0 if name1_norm == name2_norm else 0.0
        phone_exact = 1.0 if phone1_norm == phone2_norm else 0.0
        address_exact = 1.0 if addr1_norm == addr2_norm else 0.0
        
        # Pattern features
        email_has_numbers1 = 1.0 if re.search(r'\d', record1.email or '') else 0.0
        email_has_numbers2 = 1.0 if re.search(r'\d', record2.email or '') else 0.0
        email_numbers_diff = abs(email_has_numbers1 - email_has_numbers2)
        
        # Edit distances
        email_edit_dist = 1.0 - email_sim if email_sim > 0 else 1.0
        name_edit_dist = 1.0 - name_sim if name_sim > 0 else 1.0
        address_edit_dist = 1.0 - address_sim if address_sim > 0 else 1.0
        
        # Length differences
        email_len_diff = abs(len(email1_norm) - len(email2_norm)) / (max(len(email1_norm), len(email2_norm)) or 1)
        name_len_diff = abs(len(name1_norm) - len(name2_norm)) / (max(len(name1_norm), len(name2_norm)) or 1)
        
        # Levenshtein ratios
        email_lev_ratio = 1.0 - (Levenshtein.distance(email1_norm, email2_norm) / max(len(email1_norm), len(email2_norm), 1))
        name_lev_ratio = 1.0 - (Levenshtein.distance(name1_norm, name2_norm) / max(len(name1_norm), len(name2_norm), 1))
        
        # Domain matching
        try:
            domain1 = record1.email.split('@')[1] if record1.email and '@' in record1.email else ''
            domain2 = record2.email.split('@')[1] if record2.email and '@' in record2.email else ''
            domain_match = 1.0 if domain1 == domain2 and domain1 else 0.0
        except:
            domain_match = 0.0
        
        # Combine all features
        features = [
            email_sim, name_sim, phonetic_sim, phone_sim, address_sim,
            email_exact, name_exact, phone_exact, address_exact,
            email_has_numbers1, email_has_numbers2, email_numbers_diff,
            email_edit_dist, name_edit_dist, address_edit_dist,
            email_len_diff, name_len_diff,
            email_lev_ratio, name_lev_ratio,
            domain_match
        ]
        
        return np.array(features)
    
    def _generate_variation(self, base_record: IdentityRecord, variation_type: str) -> IdentityRecord:
        """Generate a variation of a base record"""
        if variation_type == 'email':
            # Modify email
            if base_record.email and '@' in base_record.email:
                email_parts = base_record.email.split('@')
                username = email_parts[0]
                domain = email_parts[1]
                # Add numbers or change format
                if random.random() < 0.5:
                    new_username = username + str(random.randint(1, 999))
                else:
                    new_username = re.sub(r'[._]', '', username)
                variant_email = f"{new_username}@{domain}"
            else:
                variant_email = self.fake.email()
            return IdentityRecord(
                name=base_record.name,
                email=variant_email,
                phone=base_record.phone,
                address=base_record.address
            )
        elif variation_type == 'name':
            # Modify name slightly
            if base_record.name:
                name_parts = base_record.name.split()
                if len(name_parts) >= 2:
                    if random.random() < 0.5:
                        # Add middle initial
                        variant_name = f"{name_parts[0]} {random.choice(string.ascii_uppercase)}. {name_parts[1]}"
                    else:
                        # Reverse order
                        variant_name = f"{name_parts[1]} {name_parts[0]}"
                else:
                    variant_name = base_record.name + " " + self.fake.last_name()
            else:
                variant_name = self.fake.name()
            return IdentityRecord(
                name=variant_name,
                email=base_record.email,
                phone=base_record.phone,
                address=base_record.address
            )
        elif variation_type == 'phone':
            # Format phone differently
            if base_record.phone:
                digits = re.sub(r'\D', '', base_record.phone)
                if len(digits) >= 10:
                    variant_phone = f"({digits[-10:-7]}) {digits[-7:-4]}-{digits[-4:]}"
                else:
                    variant_phone = base_record.phone
            else:
                variant_phone = self.fake.phone_number()
            return IdentityRecord(
                name=base_record.name,
                email=base_record.email,
                phone=variant_phone,
                address=base_record.address
            )
        elif variation_type == 'address':
            # Slightly modify address
            if base_record.address:
                variant_address = base_record.address.replace('Street', 'St').replace('Avenue', 'Ave')
            else:
                variant_address = self.fake.address().replace('\n', ', ')
            return IdentityRecord(
                name=base_record.name,
                email=base_record.email,
                phone=base_record.phone,
                address=variant_address
            )
        else:  # mixed
            # Apply multiple modifications
            temp_record = base_record
            modifications = random.sample(['email', 'name', 'phone', 'address'], random.randint(2, 3))
            for mod in modifications:
                temp_record = self._generate_variation(temp_record, mod)
            return temp_record
    
    def generate_synthetic_data(self, n_samples: int = 10000) -> pd.DataFrame:
        """Generate synthetic identity data for training"""
        data = []
        feature_names = None
        
        for i in range(n_samples):
            # Generate base person
            base_record = IdentityRecord(
                name=self.fake.name(),
                email=self.fake.email(),
                phone=self.fake.phone_number(),
                address=self.fake.address().replace('\n', ', ')
            )
            
            # Decide if we're creating a match or non-match
            is_match = random.random() < 0.5
            
            if is_match:
                # Create variation of the same person
                variation_types = ['email', 'name', 'phone', 'address', 'mixed']
                variation_type = random.choice(variation_types)
                variant_record = self._generate_variation(base_record, variation_type)
            else:
                # Create completely different person
                variant_record = IdentityRecord(
                    name=self.fake.name(),
                    email=self.fake.email(),
                    phone=self.fake.phone_number(),
                    address=self.fake.address().replace('\n', ', ')
                )
            
            # Extract features
            features = self._extract_features(base_record, variant_record)
            
            # Set feature names on first iteration
            if feature_names is None:
                feature_names = [
                    'email_sim', 'name_sim', 'phonetic_sim', 'phone_sim', 'address_sim',
                    'email_exact', 'name_exact', 'phone_exact', 'address_exact',
                    'email_has_numbers1', 'email_has_numbers2', 'email_numbers_diff',
                    'email_edit_dist', 'name_edit_dist', 'address_edit_dist',
                    'email_len_diff', 'name_len_diff',
                    'email_lev_ratio', 'name_lev_ratio',
                    'domain_match'
                ]
            
            # Create row
            row = list(features) + [int(is_match)]
            data.append(row)
        
        self.feature_names = feature_names
        columns = feature_names + ['is_match']
        return pd.DataFrame(data, columns=columns)
    
    def train(self, n_samples: int = None) -> dict:
        """Train the ML model"""
        if n_samples is None:
            n_samples = settings.TRAINING_SAMPLES
            
        logger.info(f"Generating {n_samples} synthetic training samples...")
        df = self.generate_synthetic_data(n_samples)
        
        # Prepare features and target
        X = df[self.feature_names].values
        y = df['is_match'].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, 
            test_size=settings.TEST_SIZE, 
            random_state=settings.RANDOM_STATE
        )
        
        # Train model
        logger.info(f"Training {self.model_type} model...")
        if self.model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=settings.RANDOM_STATE,
                n_jobs=-1
            )
        elif self.model_type == "logistic_regression":
            self.model = LogisticRegression(
                random_state=settings.RANDOM_STATE,
                max_iter=1000
            )
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        auc_score = roc_auc_score(y_test, y_pred_proba)
        
        evaluation_results = {
            'accuracy': accuracy,
            'auc_score': auc_score,
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
        
        logger.info(f"Model training completed. Accuracy: {accuracy:.3f}, AUC: {auc_score:.3f}")
        return evaluation_results
    
    def save_model(self, filepath: str):
        """Save trained model to disk"""
        if not self.is_trained:
            raise ValueError("Model not trained yet. Call train() first.")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_type': self.model_type
        }
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model from disk"""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.model_type = model_data['model_type']
        self.is_trained = True
        logger.info(f"Model loaded from {filepath}")
    
    def predict_similarity(self, record1: IdentityRecord, record2: IdentityRecord) -> float:
        """Predict similarity probability"""
        if not self.is_trained:
            raise ValueError("Model not trained yet. Call train() first.")
        
        features = self._extract_features(record1, record2)
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        probability = self.model.predict_proba(features_scaled)[0][1]  # Probability of match
        return float(probability)
    
    def is_same_person(self, record1: IdentityRecord, record2: IdentityRecord, threshold: float = None) -> bool:
        """Determine if two records likely represent the same person"""
        if threshold is None:
            threshold = settings.ML_THRESHOLD
        similarity = self.predict_similarity(record1, record2)
        return similarity >= threshold
