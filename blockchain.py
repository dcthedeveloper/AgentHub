"""
AgentHub Blockchain
Immutable ledger for tracking all agent-to-agent transactions
Inspired by x402 protocol and Coinbase Agent Pay architecture
"""

from datetime import datetime
import hashlib
import json


class Blockchain:
    """
    Blockchain for recording agent transactions
    Each block contains: transaction data, timestamp, hash, previous hash
    """
    
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        # Create genesis block
        self.add_block({
            'type': 'genesis',
            'message': 'AgentHub Blockchain Initialized'
        })
    
    def add_block(self, data):
        """
        Add a new block to the chain
        Args:
            data: Transaction data (dict)
        """
        if not self.chain:
            previous_hash = '0'
        else:
            previous_hash = self.chain[-1]['hash']
        
        block = {
            'index': len(self.chain),
            'data': data,
            'timestamp': str(datetime.now()),
            'previous_hash': previous_hash
        }
        
        # Create hash of the block
        block_string = json.dumps(block, sort_keys=True).encode()
        block_hash = hashlib.sha256(block_string).hexdigest()
        block['hash'] = block_hash
        
        self.chain.append(block)
        return block
    
    def is_valid(self):
        """
        Validate the entire blockchain
        Returns: True if valid, False otherwise
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Verify hash integrity
            current_block_copy = current_block.copy()
            stored_hash = current_block_copy.pop('hash')
            
            block_string = json.dumps(current_block_copy, sort_keys=True).encode()
            calculated_hash = hashlib.sha256(block_string).hexdigest()
            
            if stored_hash != calculated_hash:
                return False
            
            # Verify chain linkage
            if current_block['previous_hash'] != previous_block['hash']:
                return False
        
        return True
    
    def get_transaction_history(self, agent_id=None):
        """
        Get transaction history, optionally filtered by agent
        Args:
            agent_id: Optional agent ID to filter by
        Returns: List of transactions
        """
        transactions = []
        for block in self.chain[1:]:  # Skip genesis block
            if agent_id:
                data = block['data']
                if data.get('buyer') == agent_id or data.get('seller') == agent_id:
                    transactions.append(block)
            else:
                transactions.append(block)
        return transactions
    
    def get_agent_stats(self, agent_id):
        """
        Get statistics for a specific agent
        Args:
            agent_id: Agent identifier
        Returns: Dict with earnings, spending, job count
        """
        transactions = self.get_transaction_history(agent_id)
        
        earnings = 0
        spending = 0
        jobs_completed = 0
        jobs_requested = 0
        
        for tx in transactions:
            data = tx['data']
            if data.get('seller') == agent_id:
                earnings += data.get('amount', 0)
                if data.get('status') == 'completed':
                    jobs_completed += 1
            if data.get('buyer') == agent_id:
                spending += data.get('amount', 0)
                if data.get('status') == 'completed':
                    jobs_requested += 1
        
        return {
            'earnings': earnings,
            'spending': spending,
            'jobs_completed': jobs_completed,
            'jobs_requested': jobs_requested,
            'total_transactions': len(transactions)
        }
    
    def display_chain(self):
        """Display the entire blockchain in readable format"""
        print("\n" + "="*80)
        print("BLOCKCHAIN LEDGER")
        print("="*80)
        
        for block in self.chain:
            print(f"\nBlock #{block['index']}")
            print(f"Timestamp: {block['timestamp']}")
            print(f"Hash: {block['hash'][:16]}...")
            print(f"Previous Hash: {block['previous_hash'][:16]}...")
            print(f"Data: {json.dumps(block['data'], indent=2)}")
            print("-" * 80)
        
        print(f"\nBlockchain Valid: {self.is_valid()}")
        print(f"Total Blocks: {len(self.chain)}")
        print("="*80 + "\n")
