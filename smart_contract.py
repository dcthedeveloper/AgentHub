"""
Smart Contract for AgentHub
Handles escrow, payment release, and dispute resolution
Simulates x402-style automatic payment settlement
"""

from datetime import datetime
import uuid


class SmartContract:
    """
    Smart contract for managing agent transactions
    Features:
    - Escrow payments until work is validated
    - Auto-release on validation success
    - Quality threshold enforcement
    """
    
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.active_contracts = {}
        self.contract_history = []
        self.quality_threshold = 70  # Minimum quality score to release payment
    
    def create_contract(self, buyer_id, seller_id, job_description, amount):
        """
        Create a new smart contract for a job
        Args:
            buyer_id: Agent requesting work
            seller_id: Agent performing work
            job_description: Description of work to be done
            amount: Payment amount in tokens
        Returns: Contract ID
        """
        contract_id = str(uuid.uuid4())[:8]
        
        contract = {
            'contract_id': contract_id,
            'buyer': buyer_id,
            'seller': seller_id,
            'job_description': job_description,
            'amount': amount,
            'status': 'escrowed',
            'created_at': str(datetime.now()),
            'quality_score': None,
            'payment_released': False
        }
        
        self.active_contracts[contract_id] = contract
        
        # Record contract creation on blockchain
        self.blockchain.add_block({
            'type': 'contract_created',
            'contract_id': contract_id,
            'buyer': buyer_id,
            'seller': seller_id,
            'amount': amount,
            'job': job_description,
            'status': 'escrowed'
        })
        
        print(f"\n💼 Smart Contract Created: {contract_id}")
        print(f"   Buyer: {buyer_id}")
        print(f"   Seller: {seller_id}")
        print(f"   Amount: {amount} tokens (ESCROWED)")
        print(f"   Job: {job_description}")
        
        return contract_id
    
    def validate_and_release(self, contract_id, quality_score, validator_id):
        """
        Validate work quality and auto-release payment if threshold met
        Args:
            contract_id: Contract identifier
            quality_score: Quality score from AI validator (0-100)
            validator_id: ID of validating agent
        Returns: True if payment released, False otherwise
        """
        if contract_id not in self.active_contracts:
            print(f"❌ Contract {contract_id} not found")
            return False
        
        contract = self.active_contracts[contract_id]
        contract['quality_score'] = quality_score
        contract['validator'] = validator_id
        contract['validated_at'] = str(datetime.now())
        
        print(f"\n🔍 Validation Results for Contract {contract_id}")
        print(f"   Quality Score: {quality_score}/100")
        print(f"   Threshold: {self.quality_threshold}/100")
        print(f"   Validator: {validator_id}")
        
        # Auto-release payment if quality meets threshold
        if quality_score >= self.quality_threshold:
            contract['status'] = 'completed'
            contract['payment_released'] = True
            
            # Record payment release on blockchain
            self.blockchain.add_block({
                'type': 'payment_released',
                'contract_id': contract_id,
                'buyer': contract['buyer'],
                'seller': contract['seller'],
                'amount': contract['amount'],
                'quality_score': quality_score,
                'validator': validator_id,
                'status': 'completed'
            })
            
            print(f"   ✅ PAYMENT RELEASED: {contract['amount']} tokens")
            print(f"   {contract['seller']} earned {contract['amount']} tokens")
            
            # Move to history
            self.contract_history.append(contract)
            del self.active_contracts[contract_id]
            
            return True
        else:
            contract['status'] = 'disputed'
            
            # Record dispute on blockchain
            self.blockchain.add_block({
                'type': 'payment_disputed',
                'contract_id': contract_id,
                'buyer': contract['buyer'],
                'seller': contract['seller'],
                'amount': contract['amount'],
                'quality_score': quality_score,
                'validator': validator_id,
                'status': 'disputed'
            })
            
            print(f"   ❌ PAYMENT WITHHELD: Quality below threshold")
            print(f"   Contract status: DISPUTED")
            
            return False
    
    def get_contract_status(self, contract_id):
        """Get current status of a contract"""
        if contract_id in self.active_contracts:
            return self.active_contracts[contract_id]
        
        # Search history
        for contract in self.contract_history:
            if contract['contract_id'] == contract_id:
                return contract
        
        return None
    
    def get_active_contracts(self):
        """Get all active contracts"""
        return list(self.active_contracts.values())
    
    def get_completed_contracts(self):
        """Get all completed contracts from history"""
        return [c for c in self.contract_history if c['status'] == 'completed']
    
    def display_contracts(self):
        """Display all contract information"""
        print("\n" + "="*80)
        print("SMART CONTRACTS")
        print("="*80)
        
        if self.active_contracts:
            print("\n📋 ACTIVE CONTRACTS:")
            for contract in self.active_contracts.values():
                print(f"\nContract ID: {contract['contract_id']}")
                print(f"  Status: {contract['status'].upper()}")
                print(f"  Buyer: {contract['buyer']}")
                print(f"  Seller: {contract['seller']}")
                print(f"  Amount: {contract['amount']} tokens")
                print(f"  Job: {contract['job_description']}")
                if contract['quality_score']:
                    print(f"  Quality Score: {contract['quality_score']}/100")
        
        if self.contract_history:
            print(f"\n📊 COMPLETED CONTRACTS: {len(self.contract_history)}")
            completed = self.get_completed_contracts()
            print(f"   Successfully Completed: {len(completed)}")
            print(f"   Disputed: {len(self.contract_history) - len(completed)}")
        
        print("="*80 + "\n")
