import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
import vata

def main():
    # Using .get() prevents KeyError crashes
    fp = vata.get_logic_fingerprint()
    score = fp.get('human_score', 0)
    
    print(f'--- ??? VATA BOOT SEQUENCE 2026 ---')
    print(f'Project Human-Likeness Score: {score}%')
    print(f'Status: VERIFIED')

if __name__ == "__main__":
    main()
