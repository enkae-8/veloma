from engine.sentry import Sentry
from engine.controller import Controller
import time

def run_veloma():
    sentry = Sentry()
    brain = Controller()
    
    print("\n" + "="*40)
    print("--- VELOMA SYSTEM V2.1: ADAPTIVE ---")
    print("   STATUS: ACTIVE | ENGINE: V-SENTRY")
    print("="*40)
    
    step = 0
    while brain.vitality > 0:
        step += 1
        # Update system state based on external hype/stress
        sentry.update_state(hype_input=0.6)
        risk = sentry.get_risk()
        
        # Apply Self-Healing if Risk is low (< 30%)
        recovery = brain.apply_recovery(risk)
        
        # UI: Format the status line
        recovery_msg = f" [RECOVERY +{recovery:.3f}]" if recovery > 0 else ""
        strain_msg = " [CRITICAL STRAIN]" if risk > 80 else ""
        
        print(f"\n[STEP {step}] Vitality: {brain.vitality:.2f}{recovery_msg} | Risk: {risk:.1f}%{strain_msg}")
        
        # Decision Logic
        if risk > 60:
            print(">> CAUTION: SYSTEM INTEGRITY BREACH IMMINENT")
            action = input("Action: [H]old or [B]reach? ").upper()
            
            if action == 'B':
                # The 'Breach' resets risk but costs permanent Vitality
                cost = brain.execute_breach()
                sentry.state = [0.7, 0.4, 0.3] # Tactical Reset
                print(f"--- REWRITE SUCCESSFUL: Vitality Cost -{cost:.2f} ---")
                time.sleep(0.5)
            else:
                # Holding under high risk drains Vitality faster
                strain_penalty = 0.04
                brain.vitality -= strain_penalty
                print(f"--- STAYING THE COURSE: Absorbed -{strain_penalty} Strain ---")
        
        # Emergency Shutdown check
        if brain.vitality <= 0:
            break

    print("\n" + "!"*40)
    print("!!! CRITICAL FAILURE: SYSTEM BURNOUT !!!")
    print(f"Final Step Count: {step}")
    print("!"*40 + "\n")

if __name__ == "__main__":
    run_veloma()