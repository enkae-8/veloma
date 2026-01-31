import time
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Console

from engine.sentry import Sentry
from engine.controller import Controller

console = Console()
risk_history = [] 

def generate_layout(step, vitality, risk, recovery, message="", breaches=0, price=0):
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body", size=10),
        Layout(name="history", size=6),
        Layout(name="footer", size=3)
    )

    stability = "STABLE" if risk < 40 else "UNSTABLE" if risk < 75 else "CRITICAL"
    s_color = "green" if risk < 40 else "yellow" if risk < 75 else "red"
    
    layout["header"].update(Panel(
        f"[bold white]VELOMA LIVE[/] | STEP: [yellow]{step}[/] | BTC: [green]${price:,.2f}[/] | BREACHES: [cyan]{breaches}[/]", 
        border_style="blue"
    ))

    table = Table(expand=True, border_style="dim")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    table.add_column("Gauge", justify="center")

    v_perc = max(0, int(vitality * 20))
    v_color = "green" if vitality > 0.6 else "yellow" if vitality > 0.3 else "red"
    table.add_row("VITALITY", f"{vitality:.2f}", f"[{v_color}]" + "█" * v_perc + "░" * (20 - v_perc) + "[/]")

    r_perc = min(20, int(risk / 5))
    r_color = "red" if risk > 75 else "yellow" if risk > 40 else "green"
    table.add_row("RISK", f"{risk:.1f}%", f"[{r_color}]" + "█" * r_perc + "░" * (20 - r_perc) + "[/]")
    
    layout["body"].update(Panel(table, title=f"Telemetry: [{s_color}]{stability}[/]"))

    bars = " ▂▃▄▅▆▇█"
    sparkline = "".join([f"[red]{bars[min(7, int(r/12.5))]}[/]" for r in risk_history[-60:]])
    layout["history"].update(Panel(sparkline, title="Market Stress Map (Real-time)"))

    layout["footer"].update(Panel(message if message else "[green]CONNECTED TO COINBASE FEED[/]", border_style="white"))
    return layout

def run_visual_veloma():
    sentry = Sentry()
    brain = Controller()
    step = 0
    msg = ""
    
    # screen=True creates a full-screen "App" feel
    with Live(generate_layout(0, 1, 0, 0), refresh_per_second=4, screen=True) as live:
        try:
            while brain.vitality > 0.01:
                step += 1
                risk = sentry.get_risk()
                price = sentry.last_price
                risk_history.append(risk) 
                
                recovery = brain.apply_recovery(risk)
                live.update(generate_layout(step, brain.vitality, risk, recovery, msg, brain.breach_count, price))
                
                if risk > 65:
                    live.stop()
                    console.print(f"\n[bold red]⚠️  HIGH VOLATILITY DETECTED! RISK: {risk:.1f}%[/]")
                    cost = brain.calculate_breach_cost()
                    action = console.input(f"[white]Action: [B]reach (-{cost:.2f}) or [H]old? [/]").upper()
                    
                    if action == 'B':
                        actual_cost = brain.execute_breach()
                        sentry.risk = 15.0 
                        msg = f"[bold cyan]BREACH SUCCESSFUL (-{actual_cost:.2f})[/]"
                    else:
                        brain.vitality -= 0.10 # Harder hit for being baked/slow
                        msg = "[bold red]STRAIN ABSORBED[/]"
                    live.start()
                
                time.sleep(1)
        except Exception as e:
            msg = f"ERROR: {e}"
        except KeyboardInterrupt:
            msg = "USER TERMINATED"

    # --- THE LOCK: This prevents the window from closing ---
    console.print("\n" + "!" * 50)
    console.print(f"[bold red]FATAL COLLAPSE AT STEP {step}[/bold red]")
    console.print(f"Final Vitality: {brain.vitality:.2f}")
    console.print(f"Total Breaches: {brain.breach_count}")
    console.print("!" * 50)
    input("\n[PAUSED] Press [ENTER] to kill the terminal session completely...")

if __name__ == "__main__":
    run_visual_veloma()