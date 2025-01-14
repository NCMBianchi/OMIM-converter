"""
OMIM CONVERTER: a JavaScript conversion tool for Open Data Science URIs
Created on January 13th 2025
@author: Niccolò Bianchi [https://github.com/NCMBianchi]

'updateMapping.py' generates (and eventually overwrites) the 'monarch-omim.json'
mapping file, containing all corresponding IDs for diseases, genes and phenotypes.
By default this script only extrapolates IDs for disease, to save time.

: param '-- genes':        also extrapolates corresponding IDs for genes (biolink:Gene)
: param '-- phenotypes':   also extrapolates corresponding IDs for phenotypes (biolingk:PhenotypicFeature)

The parameters above allow to also extrapolate IDs for genes and phenotypes.
They can be concatenated in the same prompt.

The script first generates the monarch-to-omim mapping file, then it generates
automatically an omim-to-monarch mapping.

: param '-- reverse':   overrides any other operation and only runs the generation of
                        omim-to-monarch mapping
"""

import json
import os
import requests  # requires 'pip install requests'
import argparse  
from typing import Dict, Any, List
from pathlib import Path
from time import sleep

def get_all_monarch_ids(category: str) -> List[str]:
    """
    Get all IDs from Monarch Initiative for a specific category.
    Args:
        category: One of 'biolink:Disease', 'biolink:Gene', or 'biolink:PhenotypicFeature'
    Returns a list of IDs (MONDO, HGNC, or HP IDs respectively)
    """
    all_ids = []
    limit = 100  # Number of results per page
    offset = 0
    
    # ID prefix based on category
    prefix_map = {
        'biolink:Disease': 'MONDO:',
        'biolink:Gene': 'HGNC:',
        'biolink:PhenotypicFeature': 'HP:'
    }
    expected_prefix = prefix_map.get(category)
    
    while True:
        try:
            response = requests.get(
                'https://api-v3.monarchinitiative.org/v3/api/search',
                params={
                    'category': category,
                    'limit': limit,
                    'offset': offset
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract IDs from this page
            items = data.get('items', [])
            if not items:
                break
                
            # Add only IDs with correct prefix
            valid_ids = [item['id'] for item in items if item['id'].startswith(expected_prefix)]
            all_ids.extend(valid_ids)
            
            offset += limit
            print(f"Retrieved {len(all_ids)} {category} IDs so far...")
            
            # Small delay to be nice to the API
            sleep(0.1)
            
        except requests.RequestException as e:
            print(f"Error retrieving {category} IDs at offset {offset}: {e}")
            break
    
    return all_ids

def save_monarch_ids(ids: Dict[str, List[str]], output_path: str = 'data/monarch-ids.json') -> None:
    """Save all Monarch IDs to a JSON file, organized by category"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(ids, f, indent=2)
    print(f"Saved IDs to {output_path}")
    for category, id_list in ids.items():
        print(f"  {category}: {len(id_list)} IDs")

def update_mapping_file(ids_file: str = 'data/monarch-ids.json', 
                       output_path: str = 'data/monarch-omim.json',
                       genes: bool = False,
                       phenotypes: bool = False) -> None:
    """
    Create or update the Monarch Initiative ID to OMIM mapping file.
    Args:
        ids_file: Path to the JSON file containing all Monarch IDs
        output_path: Path where to save the mapping file
        genes: Whether to include gene mappings
        phenotypes: Whether to include phenotype mappings
    """
    try:
        # Load IDs from file
        with open(ids_file, 'r') as f:
            all_ids = json.load(f)
        
        # Create mappings dictionary with categories
        mappings: Dict[str, Dict[str, Any]] = {}
        
        # Filter categories based on arguments
        categories_to_process = ['disease']
        if genes:
            categories_to_process.append('gene')
        if phenotypes:
            categories_to_process.append('phenotype')
            
        for category in categories_to_process:
            if category not in all_ids:
                print(f"Warning: No IDs found for category {category}")
                continue
                
            print(f"\nProcessing {category}...")
            id_list = all_ids[category]
            total = len(id_list)
            
            for i, monarch_id in enumerate(id_list, 1):
                try:
                    response = requests.get(
                        f'https://api-v3.monarchinitiative.org/v3/api/entity/{monarch_id}'
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Find OMIM ID in xrefs
                    xrefs = data.get('xref') or []  # If xref is None, use empty list
                    omim_ref = next(
                        (ref for ref in xrefs if ref.startswith('OMIM:')),
                        None
                    )
                    
                    if omim_ref:
                        mappings[monarch_id] = {
                            'omimId': omim_ref.replace('OMIM:', ''),
                            'name': data.get('name', ''),
                            'category': category
                        }
                    
                    if i % 100 == 0:
                        print(f"Processed {i}/{total} IDs...")
                    
                    # Small delay to be nice to the API
                    sleep(0.1)
                        
                except requests.RequestException as e:
                    print(f"Error processing {monarch_id}: {e}")
                    continue
                
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Backup existing file if it exists
        if os.path.exists(output_path):
            backup_path = output_path.replace('.json', '.backup.json')
            with open(output_path, 'r') as f:
                existing_data = f.read()
            with open(backup_path, 'w') as f:
                f.write(existing_data)
            print(f"Created backup at {backup_path}")
            
        # Write new mappings
        with open(output_path, 'w') as f:
            json.dump(mappings, f, indent=2)
            
        print(f"\nSuccessfully updated mappings at {output_path}")
        print(f"Total entries: {len(mappings)}")
        
    except Exception as e:
        print(f"Error updating mappings: {e}")
        raise

def create_reverse_mapping(input_path: str = 'data/monarch-omim.json',
                         output_path: str = 'data/omim-monarch.json') -> None:
    """
    Create a reverse mapping file (OMIM to Monarch).
    Args:
        input_path: Path to the original mapping file
        output_path: Path where to save the reversed mapping file
    """
    try:
        # Load original mappings
        with open(input_path, 'r') as f:
            monarch_mappings = json.load(f)
        
        # Create reverse mappings
        omim_mappings = {}
        for monarch_id, data in monarch_mappings.items():
            omim_id = data['omimId']
            omim_mappings[omim_id] = {
                'monarchId': monarch_id,
                'name': data['name'],
                'category': data['category']
            }
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write reverse mappings
        with open(output_path, 'w') as f:
            json.dump(omim_mappings, f, indent=2)
            
        print(f"\nSuccessfully created reverse mappings at {output_path}")
        print(f"Total entries: {len(omim_mappings)}")
        
    except Exception as e:
        print(f"Error creating reverse mappings: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Update Monarch Initiative to OMIM mappings')
    parser.add_argument('--genes', action='store_true',
                      help='Include gene mappings (default: False)')
    parser.add_argument('--phenotypes', action='store_true',
                      help='Include phenotype mappings (default: False)')
    parser.add_argument('--reverse', action='store_true',
                      help='Create reverse mapping file (OMIM to Monarch)')
    args = parser.parse_args()

    if args.reverse:
        create_reverse_mapping()
    else:
        # First get and save all IDs for requested categories
        all_ids = {'disease': get_all_monarch_ids('biolink:Disease')}
        
        if args.genes:
            print("\nFetching gene IDs (this might take a while)...")
            all_ids['gene'] = get_all_monarch_ids('biolink:Gene')
    
        if args.phenotypes:
            print("\nFetching phenotype IDs...")
            all_ids['phenotype'] = get_all_monarch_ids('biolink:PhenotypicFeature')
    
        save_monarch_ids(all_ids)
    
        # Then create the mapping file
        update_mapping_file(genes=args.genes, phenotypes=args.phenotypes)
        create_reverse_mapping()

if __name__ == "__main__":
    main()