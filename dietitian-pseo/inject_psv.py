import json
import glob
import re

def main():
    files = glob.glob('/Users/k.far.88/.gemini/antigravity/scratch/perdiem-pseo/dietitian-pseo/database/json/*.json')
    
    psv_keywords = re.compile(r'(transcript|verification statement|degree|coursework|diploma|syllabus)', re.IGNORECASE)
    
    psv_count = 0
    
    for fpath in files:
        with open(fpath, 'r') as f:
            data = json.load(f)
            
        requires_psv = False
        
        # Check if any document requires primary source verification
        if 'documents' in data:
            for doc in data['documents']:
                item_text = doc.get('item', '')
                detail_text = doc.get('detail', '')
                
                # If the document explicitly mentions transcripts or verification statements
                if psv_keywords.search(item_text) or psv_keywords.search(detail_text):
                    # But exclude CDR Registration Verification (which is standard)
                    if 'cdr' not in item_text.lower() and 'registration' not in item_text.lower():
                        requires_psv = True
                        break
        
        # Add the field to the reciprocity block
        if 'reciprocity' in data:
            data['reciprocity']['requires_psv'] = requires_psv
            
        with open(fpath, 'w') as f:
            json.dump(data, f, indent=2)
            
        if requires_psv:
            psv_count += 1
            
    print(f"Added requires_psv to {len(files)} files. {psv_count} states require PSV.")

if __name__ == '__main__':
    main()
