#!/usr/bin/env python
import sys
from hypermindz.crew import PerformanceCrew


def run():
    """
    Run the crew.
    """
    
    inputs = {'query': 'Show me the top 5 performing campaigns'}
    
    PerformanceCrew().crew().kickoff(inputs=inputs)
