"""
AI Validator for AgentHub
Validates work quality before payment release
Uses rule-based system for assignment (can be upgraded to LLM later)
"""

import random


class AIValidator:
    """
    AI-powered work quality validator
    Simulates quality assessment before payment release
    
    In production, this would use:
    - Hugging Face transformers for text quality
    - Computer vision models for image validation
    - Code analyzers for code review
    
    For this demo: Rule-based scoring with some randomness
    """
    
    def __init__(self, validator_id="ValidatorAgent"):
        self.validator_id = validator_id
        self.validation_history = []
    
    def validate_work(self, job_type, work_output, job_description):
        """
        Validate work quality and return score
        Args:
            job_type: Type of work performed
            work_output: Output from agent
            job_description: Original job requirements
        Returns: Quality score (0-100)
        """
        print(f"\n🔍 {self.validator_id} validating work...")
        print(f"   Job Type: {job_type}")
        print(f"   Output: {work_output[:100]}...")
        
        # Simulate validation logic based on job type
        base_score = self._calculate_base_score(job_type, work_output)
        
        # Add some randomness to simulate real-world variance
        variance = random.randint(-15, 15)
        final_score = max(0, min(100, base_score + variance))
        
        validation = {
            'job_type': job_type,
            'score': final_score,
            'output_length': len(work_output),
            'passed': final_score >= 70
        }
        
        self.validation_history.append(validation)
        
        print(f"   Score: {final_score}/100")
        print(f"   Status: {'✅ PASSED' if validation['passed'] else '❌ FAILED'}")
        
        return final_score
    
    def _calculate_base_score(self, job_type, work_output):
        """
        Calculate base quality score based on job type
        Args:
            job_type: Type of work
            work_output: Work result
        Returns: Base score (0-100)
        """
        # Basic quality checks
        output_length = len(work_output)
        
        # Different criteria for different job types
        scoring_rules = {
            'data_analysis': {
                'min_length': 50,
                'keywords': ['analysis', 'dataset', 'correlation', 'insights'],
                'base_score': 75
            },
            'image_generation': {
                'min_length': 40,
                'keywords': ['image', 'generated', 'visual', 'quality'],
                'base_score': 80
            },
            'text_generation': {
                'min_length': 60,
                'keywords': ['content', 'professional', 'created'],
                'base_score': 70
            },
            'code_review': {
                'min_length': 50,
                'keywords': ['review', 'code', 'issues', 'improvements'],
                'base_score': 85
            },
            'validation': {
                'min_length': 30,
                'keywords': ['validation', 'quality', 'metrics'],
                'base_score': 90
            }
        }
        
        rules = scoring_rules.get(job_type, {'min_length': 40, 'keywords': [], 'base_score': 70})
        
        score = rules['base_score']
        
        # Length check
        if output_length < rules['min_length']:
            score -= 20
        
        # Keyword check
        keywords_found = sum(1 for kw in rules['keywords'] if kw.lower() in work_output.lower())
        keyword_bonus = (keywords_found / len(rules['keywords'])) * 15 if rules['keywords'] else 0
        score += keyword_bonus
        
        return int(score)
    
    def get_validation_stats(self):
        """Get validation statistics"""
        if not self.validation_history:
            return {
                'total_validations': 0,
                'pass_rate': 0,
                'average_score': 0
            }
        
        total = len(self.validation_history)
        passed = sum(1 for v in self.validation_history if v['passed'])
        avg_score = sum(v['score'] for v in self.validation_history) / total
        
        return {
            'total_validations': total,
            'pass_rate': round((passed / total) * 100, 1),
            'average_score': round(avg_score, 1)
        }
    
    def display_stats(self):
        """Display validation statistics"""
        stats = self.get_validation_stats()
        
        print(f"\n{'='*60}")
        print(f"VALIDATOR STATISTICS: {self.validator_id}")
        print(f"{'='*60}")
        print(f"Total Validations: {stats['total_validations']}")
        print(f"Pass Rate: {stats['pass_rate']}%")
        print(f"Average Score: {stats['average_score']}/100")
        print(f"{'='*60}\n")


class LLMValidator(AIValidator):
    """
    Advanced LLM-based validator (placeholder for future implementation)
    
    In production, this would:
    - Use Hugging Face transformers for text classification
    - Load pre-trained models (BERT, RoBERTa)
    - Perform semantic analysis
    - Check for quality, coherence, relevance
    
    Example implementation with transformers:
    
    from transformers import pipeline
    
    self.classifier = pipeline(
        'text-classification',
        model='bert-base-uncased'
    )
    
    result = self.classifier(work_output)
    score = result[0]['score'] * 100
    """
    
    def __init__(self, validator_id="LLMValidator"):
        super().__init__(validator_id)
        print(f"⚠️  LLM Validator initialized (using rule-based fallback)")
        print(f"   To enable true LLM validation, install: transformers, torch")
    
    def validate_with_llm(self, work_output):
        """
        Placeholder for LLM-based validation
        Returns: Quality score from LLM
        """
        # This would use actual transformer model in production
        print("   [LLM validation would run here with Hugging Face transformers]")
        return self._calculate_base_score('text_generation', work_output)
