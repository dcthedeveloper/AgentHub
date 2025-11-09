"""
Autonomous AI Agent
Each agent has: wallet, skills, reputation, transaction history
Can post jobs, bid on jobs, perform work
"""

import random


class Agent:
    """
    Autonomous AI Agent for the marketplace
    Features:
    - Digital wallet with token balance
    - Skill set and pricing
    - Reputation system
    - Transaction history
    """
    
    def __init__(self, agent_id, agent_type, skills, initial_balance=100):
        self.agent_id = agent_id
        self.agent_type = agent_type  # 'buyer', 'seller', or 'validator'
        self.skills = skills  # List of services this agent can provide
        self.balance = initial_balance
        self.reputation_score = 5.0  # Out of 5 stars
        self.jobs_completed = 0
        self.jobs_requested = 0
        self.total_earned = 0
        self.total_spent = 0
        self.active_jobs = []
        self.pricing = self._generate_pricing()
    
    def _generate_pricing(self):
        """Generate pricing for each skill based on reputation"""
        pricing = {}
        base_prices = {
            'data_analysis': 10,
            'image_generation': 8,
            'text_generation': 6,
            'code_review': 12,
            'validation': 2
        }
        
        for skill in self.skills:
            base = base_prices.get(skill, 5)
            # Higher reputation = higher prices
            reputation_multiplier = self.reputation_score / 5.0
            pricing[skill] = round(base * reputation_multiplier, 2)
        
        return pricing
    
    def post_job(self, job_description, job_type, budget):
        """
        Post a job request to the marketplace
        Args:
            job_description: What work needs to be done
            job_type: Type of service needed
            budget: Maximum payment willing to make
        Returns: Job posting dict
        """
        if self.balance < budget:
            print(f"❌ {self.agent_id}: Insufficient balance for job posting")
            return None
        
        job = {
            'job_id': f"job_{random.randint(1000, 9999)}",
            'poster': self.agent_id,
            'description': job_description,
            'type': job_type,
            'budget': budget,
            'status': 'open',
            'bids': []
        }
        
        print(f"\n📢 {self.agent_id} posted job: {job['job_id']}")
        print(f"   Type: {job_type}")
        print(f"   Budget: {budget} tokens")
        print(f"   Description: {job_description}")
        
        return job
    
    def bid_on_job(self, job):
        """
        Submit a bid for a job
        Args:
            job: Job posting dict
        Returns: Bid dict or None
        """
        job_type = job['type']
        
        # Check if agent has required skill
        if job_type not in self.skills:
            return None
        
        # Calculate bid price (slightly below budget to be competitive)
        max_price = job['budget']
        my_price = self.pricing.get(job_type, 5)
        
        # Bid at my price or budget, whichever is lower
        bid_price = min(my_price, max_price - 1)
        
        if bid_price <= 0:
            return None
        
        bid = {
            'bidder': self.agent_id,
            'amount': bid_price,
            'reputation': self.reputation_score,
            'completion_rate': self._calculate_completion_rate()
        }
        
        print(f"   💰 {self.agent_id} bid {bid_price} tokens (reputation: {self.reputation_score:.1f}⭐)")
        
        return bid
    
    def perform_work(self, job_description):
        """
        Simulate performing work
        Returns: Work output (string)
        """
        outputs = {
            'data_analysis': f"Analysis complete: Dataset processed, key insights extracted. Correlation: 0.85",
            'image_generation': f"Image generated: High-quality visual based on prompt '{job_description}'",
            'text_generation': f"Content created: Professional text matching requirements",
            'code_review': f"Code review complete: 3 issues found, 5 improvements suggested",
            'validation': f"Validation complete: Quality metrics calculated"
        }
        
        # Return generic output based on agent's primary skill
        skill = self.skills[0] if self.skills else 'generic'
        return outputs.get(skill, "Work completed successfully")
    
    def receive_payment(self, amount):
        """Receive payment for completed work"""
        self.balance += amount
        self.total_earned += amount
        self.jobs_completed += 1
        print(f"   💵 {self.agent_id} received {amount} tokens (balance: {self.balance})")
    
    def make_payment(self, amount):
        """Make payment for received work"""
        if self.balance >= amount:
            self.balance -= amount
            self.total_spent += amount
            self.jobs_requested += 1
            return True
        return False
    
    def update_reputation(self, quality_score):
        """
        Update reputation based on work quality
        Args:
            quality_score: Quality score from validator (0-100)
        """
        # Convert 0-100 score to 1-5 star rating
        new_rating = (quality_score / 100) * 5
        
        # Weighted average with existing reputation
        weight = 0.2  # New rating has 20% weight
        self.reputation_score = (self.reputation_score * (1 - weight)) + (new_rating * weight)
        
        print(f"   ⭐ {self.agent_id} reputation updated: {self.reputation_score:.2f}/5.00")
    
    def _calculate_completion_rate(self):
        """Calculate job completion rate"""
        total_jobs = self.jobs_completed + len(self.active_jobs)
        if total_jobs == 0:
            return 1.0
        return self.jobs_completed / total_jobs
    
    def get_stats(self):
        """Get agent statistics"""
        return {
            'agent_id': self.agent_id,
            'type': self.agent_type,
            'balance': self.balance,
            'reputation': round(self.reputation_score, 2),
            'jobs_completed': self.jobs_completed,
            'jobs_requested': self.jobs_requested,
            'total_earned': self.total_earned,
            'total_spent': self.total_spent,
            'completion_rate': round(self._calculate_completion_rate() * 100, 1)
        }
    
    def display_profile(self):
        """Display agent profile"""
        print(f"\n{'='*60}")
        print(f"AGENT PROFILE: {self.agent_id}")
        print(f"{'='*60}")
        print(f"Type: {self.agent_type.upper()}")
        print(f"Skills: {', '.join(self.skills)}")
        print(f"Balance: {self.balance} tokens")
        print(f"Reputation: {self.reputation_score:.2f} ⭐")
        print(f"Jobs Completed: {self.jobs_completed}")
        print(f"Jobs Requested: {self.jobs_requested}")
        print(f"Total Earned: {self.total_earned} tokens")
        print(f"Total Spent: {self.total_spent} tokens")
        print(f"Completion Rate: {self._calculate_completion_rate() * 100:.1f}%")
        
        if self.pricing:
            print(f"\nPricing:")
            for skill, price in self.pricing.items():
                print(f"  - {skill}: {price} tokens")
        
        print(f"{'='*60}\n")
