"""
AI Agent Marketplace
Handles job posting, bidding, agent matching, and transaction coordination
Simulates x402-style autonomous agent-to-agent transactions
"""

import random


class Marketplace:
    """
    Decentralized marketplace for AI agent services
    Features:
    - Job posting and discovery
    - Automated bidding system
    - Agent matching algorithm
    - Transaction coordination
    """
    
    def __init__(self, blockchain, smart_contract, validator):
        self.blockchain = blockchain
        self.smart_contract = smart_contract
        self.validator = validator
        self.active_jobs = []
        self.completed_jobs = []
        self.agents = {}
    
    def register_agent(self, agent):
        """
        Register an agent in the marketplace
        Args:
            agent: Agent instance
        """
        self.agents[agent.agent_id] = agent
        print(f"✅ {agent.agent_id} registered in marketplace")
        print(f"   Skills: {', '.join(agent.skills)}")
        print(f"   Initial Balance: {agent.balance} tokens")
    
    def post_job(self, poster_agent, job_description, job_type, budget):
        """
        Post a new job to the marketplace
        Args:
            poster_agent: Agent posting the job
            job_description: Description of work needed
            job_type: Type of service required
            budget: Maximum payment
        Returns: Job ID or None
        """
        job = poster_agent.post_job(job_description, job_type, budget)
        
        if job:
            self.active_jobs.append(job)
            return job['job_id']
        
        return None
    
    def collect_bids(self, job_id):
        """
        Collect bids from eligible agents for a job
        Args:
            job_id: Job identifier
        Returns: List of bids
        """
        job = self._find_job(job_id)
        if not job:
            return []
        
        print(f"\n📋 Collecting bids for {job_id}...")
        
        bids = []
        for agent_id, agent in self.agents.items():
            # Skip the job poster
            if agent_id == job['poster']:
                continue
            
            # Only sellers can bid
            if agent.agent_type != 'seller':
                continue
            
            bid = agent.bid_on_job(job)
            if bid:
                bids.append(bid)
        
        job['bids'] = bids
        
        print(f"   Total bids received: {len(bids)}")
        
        return bids
    
    def select_winner(self, job_id):
        """
        Select winning bid using reputation-weighted algorithm
        Args:
            job_id: Job identifier
        Returns: Winning agent ID or None
        """
        job = self._find_job(job_id)
        if not job or not job['bids']:
            print(f"❌ No bids found for {job_id}")
            return None
        
        print(f"\n🎯 Selecting winner for {job_id}...")
        
        # Score each bid: lower price is better, higher reputation is better
        best_score = -1
        winner = None
        
        for bid in job['bids']:
            # Normalize price score (lower is better, scaled 0-1)
            price_score = 1 - (bid['amount'] / job['budget'])
            
            # Normalize reputation score (higher is better, scaled 0-1)
            reputation_score = bid['reputation'] / 5.0
            
            # Weighted combination (60% reputation, 40% price)
            total_score = (reputation_score * 0.6) + (price_score * 0.4)
            
            if total_score > best_score:
                best_score = total_score
                winner = bid
        
        if winner:
            print(f"   🏆 Winner: {winner['bidder']}")
            print(f"   Amount: {winner['amount']} tokens")
            print(f"   Reputation: {winner['reputation']:.1f}⭐")
            print(f"   Score: {best_score:.2f}")
            
            job['winner'] = winner['bidder']
            job['final_price'] = winner['amount']
            job['status'] = 'assigned'
        
        return winner['bidder'] if winner else None
    
    def execute_job(self, job_id):
        """
        Execute a job: create contract, perform work, validate, release payment
        Args:
            job_id: Job identifier
        Returns: True if successful, False otherwise
        """
        job = self._find_job(job_id)
        if not job or job['status'] != 'assigned':
            print(f"❌ Job {job_id} not ready for execution")
            return False
        
        buyer_id = job['poster']
        seller_id = job['winner']
        amount = job['final_price']
        
        buyer = self.agents[buyer_id]
        seller = self.agents[seller_id]
        
        print(f"\n{'='*80}")
        print(f"EXECUTING JOB: {job_id}")
        print(f"{'='*80}")
        
        # Step 1: Create smart contract and escrow payment
        print("\n[STEP 1: SMART CONTRACT & ESCROW]")
        if not buyer.make_payment(amount):
            print(f"❌ {buyer_id} has insufficient balance")
            return False
        
        contract_id = self.smart_contract.create_contract(
            buyer_id,
            seller_id,
            job['description'],
            amount
        )
        
        # Step 2: Seller performs work
        print("\n[STEP 2: WORK EXECUTION]")
        print(f"   🔨 {seller_id} performing work...")
        work_output = seller.perform_work(job['description'])
        print(f"   ✅ Work completed")
        print(f"   Output: {work_output}")
        
        # Step 3: AI validation
        print("\n[STEP 3: AI VALIDATION]")
        
        # Check if using ML validator or legacy validator
        if hasattr(self.validator, 'validate_work'):
            # ML Validator returns a dict with 'score' key
            validation_result = self.validator.validate_work(
                job['description'],
                work_output,
                job['type']
            )
            # Handle both ML validator (dict) and legacy validator (int) return types
            if isinstance(validation_result, dict):
                quality_score = validation_result['score']
                print(f"   🎯 ML Confidence: {validation_result.get('confidence', 'N/A')}")
            else:
                quality_score = validation_result
        else:
            # Fallback for legacy validator
            quality_score = self.validator.validate_work(
                job['type'],
                work_output,
                job['description']
            )
        
        # Step 4: Smart contract validates and releases payment
        print("\n[STEP 4: PAYMENT SETTLEMENT]")
        payment_released = self.smart_contract.validate_and_release(
            contract_id,
            quality_score,
            self.validator.validator_id
        )
        
        if payment_released:
            # Update agent balances and reputation
            seller.receive_payment(amount)
            seller.update_reputation(quality_score)
            
            job['status'] = 'completed'
            job['quality_score'] = quality_score
            job['contract_id'] = contract_id
            
            self.completed_jobs.append(job)
            self.active_jobs.remove(job)
            
            print(f"\n{'='*80}")
            print(f"JOB COMPLETED SUCCESSFULLY ✅")
            print(f"{'='*80}\n")
            
            return True
        else:
            print(f"\n{'='*80}")
            print(f"JOB DISPUTED - PAYMENT WITHHELD ❌")
            print(f"{'='*80}\n")
            
            return False
    
    def _find_job(self, job_id):
        """Find a job by ID"""
        for job in self.active_jobs + self.completed_jobs:
            if job['job_id'] == job_id:
                return job
        return None
    
    def display_marketplace_stats(self):
        """Display marketplace statistics"""
        print(f"\n{'='*80}")
        print("MARKETPLACE STATISTICS")
        print(f"{'='*80}")
        
        print(f"\nRegistered Agents: {len(self.agents)}")
        for agent_id, agent in self.agents.items():
            stats = agent.get_stats()
            print(f"\n  {agent_id}:")
            print(f"    Type: {stats['type']}")
            print(f"    Balance: {stats['balance']} tokens")
            print(f"    Reputation: {stats['reputation']}⭐")
            print(f"    Jobs Completed: {stats['jobs_completed']}")
            print(f"    Total Earned: {stats['total_earned']} tokens")
        
        print(f"\nActive Jobs: {len(self.active_jobs)}")
        print(f"Completed Jobs: {len(self.completed_jobs)}")
        
        if self.completed_jobs:
            total_value = sum(job['final_price'] for job in self.completed_jobs)
            avg_value = total_value / len(self.completed_jobs)
            avg_quality = sum(job.get('quality_score', 0) for job in self.completed_jobs) / len(self.completed_jobs)
            
            print(f"\nTransaction Metrics:")
            print(f"  Total Transaction Value: {total_value} tokens")
            print(f"  Average Job Value: {avg_value:.2f} tokens")
            print(f"  Average Quality Score: {avg_quality:.1f}/100")
        
        print(f"{'='*80}\n")
    
    def run_full_job_cycle(self, poster_id, job_description, job_type, budget):
        """
        Run a complete job cycle: post → bid → select → execute
        Args:
            poster_id: Agent posting job
            job_description: Job description
            job_type: Type of job
            budget: Maximum budget
        Returns: True if successful
        """
        poster = self.agents.get(poster_id)
        if not poster:
            print(f"❌ Agent {poster_id} not found")
            return False
        
        # Post job
        job_id = self.post_job(poster, job_description, job_type, budget)
        if not job_id:
            return False
        
        # Collect bids
        bids = self.collect_bids(job_id)
        if not bids:
            print(f"❌ No bids received for {job_id}")
            return False
        
        # Select winner
        winner = self.select_winner(job_id)
        if not winner:
            return False
        
        # Execute job
        return self.execute_job(job_id)
