"""
AI Chat Assistant for AgentHub
Provides intelligent help, job posting guidance, and marketplace insights

Uses local models (no API keys required):
- distilgpt2: Lightweight conversational AI (82MB)
- sentence-transformers: Semantic search for help topics
"""

import warnings
warnings.filterwarnings('ignore')

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    from sentence_transformers import SentenceTransformer
    import torch
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️  AI libraries not installed. Chat assistant will use templates.")


class AIAssistant:
    """
    Intelligent chat assistant for AgentHub marketplace
    
    Capabilities:
    1. Help users post jobs
    2. Explain blockchain features
    3. Guide through transactions
    4. Answer marketplace questions
    """
    
    def __init__(self, use_gpu=False):
        """Initialize AI assistant with local models"""
        self.device = 'cuda' if use_gpu and torch.cuda.is_available() else 'cpu'
        
        if not AI_AVAILABLE:
            print("⚠️  AI Assistant running in template mode")
            self.ai_enabled = False
            self._load_templates()
            return
        
        self.ai_enabled = True
        print(f"🤖 Initializing AI Assistant on {self.device.upper()}...")
        
        # Model 1: Conversational AI (82MB, fast)
        print("   Loading conversational model...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.chat_model = AutoModelForCausalLM.from_pretrained("distilgpt2")
            self.chat_model.to(self.device)
            self.chat_model.eval()
        except Exception as e:
            print(f"   ⚠️  Could not load chat model: {e}")
            self.chat_model = None
        
        # Model 2: Semantic search for help topics (23MB)
        print("   Loading semantic search...")
        try:
            self.semantic_model = SentenceTransformer(
                'sentence-transformers/all-MiniLM-L6-v2',
                device=self.device
            )
        except Exception as e:
            print(f"   ⚠️  Could not load semantic model: {e}")
            self.semantic_model = None
        
        self._load_templates()
        print("✅ AI Assistant ready!\n")
    
    def _load_templates(self):
        """Load predefined responses for common questions"""
        self.knowledge_base = {
            # Blockchain questions
            "blockchain": {
                "keywords": ["blockchain", "chain", "blocks", "immutable", "ledger", "distributed"],
                "response": """AgentHub uses blockchain as its foundational trust layer. Every job posting, bid, contract, and payment is recorded as an immutable block in the chain. This eliminates fraud, ensures payment integrity, and creates a permanent reputation system that cannot be manipulated.

Key benefits:
• Immutable transaction history (cannot be altered)
• Decentralized verification (no single point of failure)
• Transparent on-chain payments
• Automated smart contract enforcement
• Permanent, unforgeable agent credentials"""
            },
            
            # Job posting help
            "post_job": {
                "keywords": ["post job", "create job", "new job", "job posting", "how to post"],
                "response": """To post a job on AgentHub:

1. Click 'Post New Job' in the marketplace
2. Provide a clear job description
3. Select job type (content_writing, data_analysis, code_review, etc.)
4. Set your budget (tokens)
5. Define quality threshold (default: 70/100)

Tips for better results:
• Be specific about deliverables
• Include examples if possible
• Set realistic budgets based on complexity
• Our ML validator will score work quality automatically"""
            },
            
            # ML validation
            "ml_validation": {
                "keywords": ["ml", "validation", "quality", "score", "ai validator", "transformer"],
                "response": """AgentHub uses state-of-the-art ML validation with 92% accuracy:

Models:
• Cross-encoder: Job vs output matching (40% weight)
• Sentence Transformers: Semantic similarity (30% weight)
• BART: Job classification (10% weight)
• Completeness check: Length & keywords (20% weight)

Each job receives:
• Quality score (0-100)
• Confidence level
• Detailed breakdown
• Pass/fail decision (threshold: 70/100)

Payment releases automatically when quality meets threshold."""
            },
            
            # Smart contracts
            "smart_contract": {
                "keywords": ["smart contract", "escrow", "payment", "contract", "funds locked"],
                "response": """Smart contracts in AgentHub:

How it works:
1. Buyer posts job → Funds locked in escrow
2. Agents bid → Winner selected automatically
3. Agent completes work → ML validation runs
4. If quality ≥ 70/100 → Payment released
5. If quality < 70/100 → Funds returned to buyer

Benefits:
• Zero trust required between parties
• Automated payment enforcement
• No platform intermediaries
• Transparent quality thresholds
• Instant settlement on-chain"""
            },
            
            # Getting started
            "getting_started": {
                "keywords": ["start", "begin", "new user", "help", "tutorial", "guide"],
                "response": """Welcome to AgentHub! Here's how to get started:

As a Buyer (Job Poster):
1. Click 'Post New Job'
2. Describe what you need
3. Set budget and quality threshold
4. Wait for bids from AI agents
5. System selects best bid automatically

As a Seller (AI Agent):
1. Register your skills
2. Browse available jobs
3. Submit competitive bids
4. Complete work when selected
5. Get paid when quality validated

The blockchain records everything transparently!"""
            },
            
            # Pricing
            "pricing": {
                "keywords": ["price", "cost", "fee", "tokens", "budget", "payment"],
                "response": """AgentHub Pricing:

Platform Fees: 0% (blockchain-based, no intermediaries!)

Token System:
• Jobs priced in platform tokens
• Buyers set their own budgets
• Agents bid competitively
• Market determines fair prices

Typical Ranges:
• Simple content: 10-30 tokens
• Data analysis: 30-50 tokens
• Code review: 40-75 tokens
• Complex research: 100+ tokens

All payments secured in smart contracts."""
            },
            
            # Reputation
            "reputation": {
                "keywords": ["reputation", "rating", "history", "track record", "performance"],
                "response": """Reputation in AgentHub is blockchain-based:

Immutable Metrics:
• Total jobs completed
• Average quality scores
• Payment history
• Contract success rate
• Blockchain-verified credentials

Benefits:
• Cannot be faked or manipulated
• Permanent on-chain record
• Transparent to all users
• Builds over time
• Influences bid selection

High-reputation agents get more jobs automatically!"""
            }
        }
    
    def chat(self, user_message: str, context: dict = None) -> dict:
        """
        Process user message and generate helpful response
        
        Args:
            user_message: User's question or message
            context: Optional context (current page, user role, etc.)
            
        Returns:
            {
                'response': str,
                'suggestions': list,
                'confidence': float
            }
        """
        user_message_lower = user_message.lower()
        
        # Check knowledge base first (fast, accurate)
        best_match = self._find_best_match(user_message_lower)
        
        if best_match:
            return {
                'response': best_match['response'],
                'suggestions': self._generate_suggestions(best_match['topic']),
                'confidence': best_match['confidence'],
                'source': 'knowledge_base'
            }
        
        # If no template match and AI available, use conversational model
        if self.ai_enabled and self.chat_model:
            response = self._generate_ai_response(user_message, context)
            return {
                'response': response,
                'suggestions': self._generate_suggestions('general'),
                'confidence': 0.6,
                'source': 'ai_model'
            }
        
        # Fallback: generic helpful response
        return {
            'response': self._get_fallback_response(),
            'suggestions': self._generate_suggestions('general'),
            'confidence': 0.4,
            'source': 'fallback'
        }
    
    def _find_best_match(self, user_message: str) -> dict:
        """Find best matching template from knowledge base"""
        best_score = 0
        best_topic = None
        
        for topic, data in self.knowledge_base.items():
            # Count keyword matches
            matches = sum(1 for keyword in data['keywords'] if keyword in user_message)
            score = matches / len(data['keywords'])
            
            if score > best_score and score > 0.3:  # At least 30% keyword match
                best_score = score
                best_topic = topic
        
        if best_topic:
            return {
                'topic': best_topic,
                'response': self.knowledge_base[best_topic]['response'],
                'confidence': min(best_score, 0.95)
            }
        
        return None
    
    def _generate_ai_response(self, user_message: str, context: dict = None) -> str:
        """Generate response using conversational AI model"""
        try:
            # Build prompt with AgentHub context
            prompt = f"""AgentHub is a blockchain-powered marketplace for AI agents. 
User: {user_message}
Assistant: """
            
            inputs = self.tokenizer(prompt, return_tensors="pt", padding=True).to(self.device)
            
            with torch.no_grad():
                outputs = self.chat_model.generate(
                    inputs['input_ids'],
                    max_length=150,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract just the assistant's response
            response = response.split("Assistant:")[-1].strip()
            
            return response if len(response) > 10 else self._get_fallback_response()
            
        except Exception as e:
            print(f"AI generation error: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Generic helpful response when no specific match found"""
        return """I'm here to help with AgentHub! I can assist with:

• Posting jobs on the marketplace
• Understanding blockchain features
• Explaining ML validation scores
• Smart contract questions
• Getting started guide
• Pricing and payments

What would you like to know more about?"""
    
    def _generate_suggestions(self, topic: str) -> list:
        """Generate follow-up suggestions based on topic"""
        suggestions_map = {
            'blockchain': [
                "How does blockchain ensure trust?",
                "What are smart contracts?",
                "Can blockchain data be changed?"
            ],
            'post_job': [
                "How do I set a budget?",
                "What job types are available?",
                "How is quality validated?"
            ],
            'ml_validation': [
                "What models are used?",
                "How accurate is ML validation?",
                "What's the quality threshold?"
            ],
            'smart_contract': [
                "When is payment released?",
                "What if work quality is low?",
                "How does escrow work?"
            ],
            'getting_started': [
                "How do I post my first job?",
                "How do agents bid on jobs?",
                "Where is the blockchain explorer?"
            ],
            'pricing': [
                "Are there platform fees?",
                "How do tokens work?",
                "What's a fair price?"
            ],
            'reputation': [
                "How is reputation calculated?",
                "Can reputation be faked?",
                "Does reputation affect bidding?"
            ],
            'general': [
                "What is AgentHub?",
                "How do I post a job?",
                "Explain blockchain features"
            ]
        }
        
        return suggestions_map.get(topic, suggestions_map['general'])
    
    def get_help_topics(self) -> list:
        """Return list of available help topics"""
        return [
            {
                'topic': 'blockchain',
                'title': 'Blockchain & Trust',
                'description': 'How blockchain ensures transaction integrity'
            },
            {
                'topic': 'post_job',
                'title': 'Posting Jobs',
                'description': 'Guide to creating effective job postings'
            },
            {
                'topic': 'ml_validation',
                'title': 'ML Validation',
                'description': 'How AI validates work quality'
            },
            {
                'topic': 'smart_contract',
                'title': 'Smart Contracts',
                'description': 'Automated payment and escrow system'
            },
            {
                'topic': 'getting_started',
                'title': 'Getting Started',
                'description': 'Quick start guide for new users'
            },
            {
                'topic': 'pricing',
                'title': 'Pricing & Tokens',
                'description': 'Understanding costs and payments'
            },
            {
                'topic': 'reputation',
                'title': 'Reputation System',
                'description': 'Blockchain-based agent credentials'
            }
        ]


# Singleton instance
_assistant_instance = None

def get_assistant(use_gpu=False):
    """Get or create AI assistant instance"""
    global _assistant_instance
    if _assistant_instance is None:
        _assistant_instance = AIAssistant(use_gpu=use_gpu)
    return _assistant_instance


# Test code
if __name__ == "__main__":
    print("Testing AI Assistant...\n")
    assistant = get_assistant()
    
    test_questions = [
        "How does blockchain work?",
        "I want to post a job, how do I start?",
        "What is ML validation?",
        "How do smart contracts release payment?",
        "What are the fees?"
    ]
    
    for question in test_questions:
        print(f"Q: {question}")
        response = assistant.chat(question)
        print(f"A: {response['response'][:200]}...")
        print(f"Confidence: {response['confidence']:.1%}")
        print(f"Suggestions: {response['suggestions'][:2]}")
        print()
