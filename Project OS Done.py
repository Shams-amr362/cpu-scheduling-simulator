import random
import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=None, color=None):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.color = color
        self.start_time = None
        self.finish_time = None
        self.waiting_time = None
        self.turnaround_time = None
        
    def _generate_color(self):
        colors = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F',
                 '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F', '#BAB0AC']
        return colors[self.pid % len(colors)]

def fcfs(processes):
    time = 0
    completed = []
    gantt = []
    processes.sort(key=lambda p: p.arrival_time)
    for p in processes:
        if time < p.arrival_time:
            time = p.arrival_time
        p.start_time = time
        p.finish_time = time + p.burst_time
        p.waiting_time = p.start_time - p.arrival_time
        p.turnaround_time = p.finish_time - p.arrival_time
        completed.append(p)
        gantt.append((f"P{p.pid}", p.start_time, p.finish_time, p.color))
        time = p.finish_time
    return completed, gantt

def sjf(processes):
    time = 0
    completed = []
    gantt = []
    ready = []
    while len(completed) < len(processes):
        for p in processes:
            if p.arrival_time <= time and p not in completed and p not in ready:
                ready.append(p)
        if not ready:
            time += 1
            continue
        ready.sort(key=lambda p: p.burst_time)
        current = ready.pop(0)
        current.start_time = time
        current.finish_time = time + current.burst_time
        current.waiting_time = current.start_time - current.arrival_time
        current.turnaround_time = current.finish_time - current.arrival_time
        completed.append(current)
        gantt.append((f"P{current.pid}", current.start_time, current.finish_time, current.color))
        time = current.finish_time
    return completed, gantt

def priority_scheduling(processes):
    time = 0
    completed = []
    gantt = []
    ready = []
    while len(completed) < len(processes):
        for p in processes:
            if p.arrival_time <= time and p not in completed and p not in ready:
                ready.append(p)
        if not ready:
            time += 1
            continue
        ready.sort(key=lambda p: p.priority)
        current = ready.pop(0)
        current.start_time = time
        current.finish_time = time + current.burst_time
        current.waiting_time = current.start_time - current.arrival_time
        current.turnaround_time = current.finish_time - current.arrival_time
        completed.append(current)
        gantt.append((f"P{current.pid}", current.start_time, current.finish_time, current.color))
        time = current.finish_time
    return completed, gantt

def round_robin(processes, quantum=2):
    time = 0
    queue = []
    completed = []
    gantt = []
    remaining = {p.pid: p.burst_time for p in processes}
    processes.sort(key=lambda p: p.arrival_time)
    i = 0
    queue.append(processes[0])
    i += 1
    while queue:
        current = queue.pop(0)
        if current.start_time is None:
            current.start_time = time
        run_time = min(quantum, remaining[current.pid])
        gantt.append((f"P{current.pid}", time, time + run_time, current.color))
        time += run_time
        remaining[current.pid] -= run_time
        if remaining[current.pid] == 0:
            current.finish_time = time
            current.turnaround_time = current.finish_time - current.arrival_time
            current.waiting_time = current.turnaround_time - current.burst_time
            completed.append(current)
        else:
            while i < len(processes) and processes[i].arrival_time <= time:
                queue.append(processes[i])
                i += 1
            queue.append(current)
        if not queue and len(completed) < len(processes):
            while i < len(processes):
                if processes[i].arrival_time > time:
                    time = processes[i].arrival_time
                queue.append(processes[i])
                i += 1
                break
    return completed, gantt

class CPUSchedulingSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Simulator")
        self.root = root
        self.root.title("CPU Scheduling Simulator")
        self.root.geometry("1000x700")
        self.processes = []
        self.gantt = []
        self.completed = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Input frame
        input_frame = LabelFrame(main_frame, text="Input Parameters", padx=10, pady=10)
        input_frame.pack(fill=X, pady=5)
        
        # Algorithm selection
        Label(input_frame, text="Scheduling Algorithm:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.algo_var = StringVar(value="FCFS")
        algo_options = ["FCFS", "SJF", "Priority", "Round Robin"]
        self.algo_menu = ttk.Combobox(input_frame, textvariable=self.algo_var, values=algo_options, state="readonly")
        self.algo_menu.grid(row=0, column=1, padx=5, pady=5, sticky=W)
        self.algo_menu.bind("<<ComboboxSelected>>", self.update_ui_for_algorithm)
        
        # Quantum input (hidden by default)
        self.quantum_frame = Frame(input_frame)
        self.quantum_frame.grid(row=0, column=2, padx=5, pady=5, sticky=W)
        Label(self.quantum_frame, text="Time Quantum:").pack(side=LEFT)
        self.quantum_entry = Entry(self.quantum_frame, width=5)
        self.quantum_entry.pack(side=LEFT, padx=5)
        self.quantum_entry.insert(0, "2")
        self.quantum_frame.grid_remove()
        
        # Process count
        Label(input_frame, text="Number of Processes:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.process_count_entry = Entry(input_frame, width=5)
        self.process_count_entry.grid(row=1, column=1, padx=5, pady=5, sticky=W)
        self.process_count_entry.insert(0, "5")
        
        # Process table
        self.table_frame = LabelFrame(main_frame, text="Process Details", padx=10, pady=10)
        self.table_frame.pack(fill=BOTH, expand=True, pady=5)
        
        # Buttons frame
        button_frame = Frame(main_frame)
        button_frame.pack(fill=X, pady=5)
        
        self.generate_btn = Button(button_frame, text="Generate Processes", command=self.generate_processes)
        self.generate_btn.pack(side=LEFT, padx=5)
        
        self.run_btn = Button(button_frame, text="Run Simulation", command=self.run_simulation)
        self.run_btn.pack(side=LEFT, padx=5)
        
        # Results frame
        self.results_frame = LabelFrame(main_frame, text="Results", padx=10, pady=10)
        self.results_frame.pack(fill=BOTH, expand=True, pady=5)
        
        # Stats frame
        self.stats_frame = Frame(self.results_frame)
        self.stats_frame.pack(fill=X, pady=5)
        
        # Performance metrics frame
        self.metrics_frame = Frame(self.stats_frame)
        self.metrics_frame.pack(fill=X, pady=5)
        
        # Gantt chart frame
        self.gantt_frame = Frame(self.results_frame)
        self.gantt_frame.pack(fill=BOTH, expand=True)
        
        # Detailed results frame
        self.details_frame = Frame(self.results_frame)
        self.details_frame.pack(fill=BOTH, expand=True)
        # Create process table
        self.create_process_table()
        
    def update_ui_for_algorithm(self, event=None):
        if self.algo_var.get() == "Round Robin":
            self.quantum_frame.grid()
        else:
            self.quantum_frame.grid_remove()
    
    def create_process_table(self):
        # Create treeview for process table
        self.tree = ttk.Treeview(self.table_frame, columns=("PID", "Arrival", "Burst", "Priority"), show="headings")
        
        # Define headings
        self.tree.heading("PID", text="PID")
        self.tree.heading("Arrival", text="Arrival Time")
        self.tree.heading("Burst", text="Burst Time")
        self.tree.heading("Priority", text="Priority")
        
        # Set column widths
        self.tree.column("PID", width=50, anchor=CENTER)
        self.tree.column("Arrival", width=100, anchor=CENTER)
        self.tree.column("Burst", width=100, anchor=CENTER)
        self.tree.column("Priority", width=100, anchor=CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
    
    def generate_processes(self):
        try:
            num = int(self.process_count_entry.get())
            if num <= 0:
                messagebox.showerror("Error", "Number of processes must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            return
            
        self.processes = []
        for i in range(num):
            arrival = random.randint(0, 5)
            burst = random.randint(2, 7)
            priority = random.randint(1, 5)
            self.processes.append(Process(i+1, arrival, burst, priority))
        
        self.update_process_table()
    
    def update_process_table(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add new items
        for p in self.processes:
            self.tree.insert("", "end", values=(f"P{p.pid}", p.arrival_time, p.burst_time, p.priority))
    
    def run_simulation(self):
        if not self.processes:
            messagebox.showerror("Error", "No processes to simulate. Generate processes first.")
            return
            
        algo = self.algo_var.get()
        quantum = 2
        
        if algo == "Round Robin":
            try:
                quantum = int(self.quantum_entry.get())
                if quantum <= 0:
                    messagebox.showerror("Error", "Time quantum must be positive")
                    return
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid time quantum")
                return
        
        if algo == "FCFS":
            self.completed, self.gantt = fcfs(self.processes)
        elif algo == "SJF":
            self.completed, self.gantt = sjf(self.processes)
        elif algo == "Priority":
            self.completed, self.gantt = priority_scheduling(self.processes)
        elif algo == "Round Robin":
            self.completed, self.gantt = round_robin(self.processes, quantum)
        else:
            messagebox.showerror("Error", "Invalid algorithm selected")
            return
            
        self.display_results()
    
    def display_results(self):
        # Clear previous results
        for widget in self.gantt_frame.winfo_children():
            widget.destroy()
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()
        for widget in self.details_frame.winfo_children():
            widget.destroy()
            
        # Draw Gantt chart
        self.draw_gantt_chart()
        
        # Calculate performance metrics
        avg_wt = sum(p.waiting_time for p in self.completed) / len(self.completed)
        avg_tat = sum(p.turnaround_time for p in self.completed) / len(self.completed)
        
        # Display performance metrics prominently
        metrics_label = Label(self.metrics_frame, text="Performance Metrics", font=('Arial', 12, 'bold'))
        metrics_label.pack(pady=5)
        
        # Create a frame for the metrics display
        metrics_display = Frame(self.metrics_frame)
        metrics_display.pack(pady=5)
        
        # Waiting time
        wt_frame = Frame(metrics_display, bd=2, relief=GROOVE, padx=10, pady=5)
        wt_frame.pack(side=LEFT, padx=10)
        Label(wt_frame, text="Average Waiting Time", font=('Arial', 10, 'bold')).pack()
        Label(wt_frame, text=f"{avg_wt:.2f} units", font=('Arial', 12)).pack()
        
        # Turnaround time
        tat_frame = Frame(metrics_display, bd=2, relief=GROOVE, padx=10, pady=5)
        tat_frame.pack(side=LEFT, padx=10)
        Label(tat_frame, text="Average Turnaround Time", font=('Arial', 10, 'bold')).pack()
        Label(tat_frame, text=f"{avg_tat:.2f} units", font=('Arial', 12)).pack()
        
        # Create detailed results table
        details_label = Label(self.details_frame, text="Detailed Process Results", font=('Arial', 12, 'bold'))
        details_label.pack(pady=5)
        
        results_tree = ttk.Treeview(self.details_frame, 
                                  columns=("PID", "Arrival", "Burst", "Priority", "Start", "Finish", "Waiting", "Turnaround"), 
                                  show="headings")
        
        # Define headings
        results_tree.heading("PID", text="PID")
        results_tree.heading("Arrival", text="Arrival")
        results_tree.heading("Burst", text="Burst")
        results_tree.heading("Priority", text="Priority")
        results_tree.heading("Start", text="Start Time")
        results_tree.heading("Finish", text="Finish Time")
        results_tree.heading("Waiting", text="Waiting Time")
        results_tree.heading("Turnaround", text="Turnaround Time")
        
        # Set column widths
        for col in ("PID", "Arrival", "Burst", "Priority", "Start", "Finish", "Waiting", "Turnaround"):
            results_tree.column(col, width=80, anchor=CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.details_frame, orient="vertical", command=results_tree.yview)
        results_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        results_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Add data
        for p in self.completed:
            results_tree.insert("", "end", values=(
                f"P{p.pid}", p.arrival_time, p.burst_time, p.priority,
                p.start_time, p.finish_time, p.waiting_time, p.turnaround_time
            ))
    
    def draw_gantt_chart(self):
        # Create a larger figure with adjusted dimensions
        fig, ax = plt.subplots(figsize=(14, 6))  # Increased size for better visibility
        y = 15  # Increased y-position for taller bars
        
        # Calculate the maximum time for proper scaling
        max_time = max(end for _, _, end, _ in self.gantt) + 1
        
        # Draw each process in the Gantt chart with enhanced styling
        for name, start, end, color in self.gantt:
            duration = end - start
            
            # Draw the process bar with enhanced styling
            bar = ax.broken_barh([(start, duration)], (y - 8, 16),  # Taller bars
                               facecolors=color,edgecolor='black', 
                               linewidth=1.5,
                               alpha=0.8)  # Slight transparency
            
            # Add process name in the center of the bar
            ax.text(start + duration/2, y, name,
                   ha='center', va='center',
                   color='white', fontsize=14, fontweight='bold',
                   bbox=dict(facecolor='black', alpha=0.5, boxstyle='round,pad=0.2'))
            
            # Add time markers with improved styling
            ax.text(start, y - 10, f"Start: {start}",
                   ha='center', va='top',
                   fontsize=10, color='black',
                   bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.2'))
            
            ax.text(end, y - 10, f"End: {end}",
                   ha='center', va='top',
                   fontsize=10, color='black',
                   bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.2'))
        
        # Customize the chart appearance
        ax.set_ylim(0, 30)
        ax.set_xlim(0, max_time)
        
        # Enhanced axis styling
        ax.set_yticks([y])
        ax.set_yticklabels(["Process Execution Timeline"], fontsize=12, fontweight='bold')
        ax.set_xticks(range(0, max_time + 1, max(1, max_time//20)))  # Dynamic tick spacing
        ax.tick_params(axis='x', labelsize=10, rotation=45)
        ax.tick_params(axis='y', labelsize=12)
        
        # Add major and minor grid lines
        ax.grid(which='major', linestyle='-', linewidth=0.5, alpha=0.7)
        ax.grid(which='minor', linestyle=':', linewidth=0.5, alpha=0.5)
        ax.minorticks_on()
        
        # Add title and labels with enhanced styling
        plt.title(f"CPU Scheduling Gantt Chart ({self.algo_var.get()} Algorithm)", 
                 fontsize=16, pad=20, fontweight='bold')
        ax.set_xlabel("Time Units", fontsize=14, labelpad=10)
        
        # Add a subtle background color
        ax.set_facecolor('#f5f5f5')
        fig.patch.set_facecolor('#f0f0f0')
        
        # Add border around the chart
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(1.5)
        
        # Adjust layout to prevent clipping
        plt.tight_layout()
        
        # Embed the plot in the Tkinter window with padding
        canvas = FigureCanvasTkAgg(fig, master=self.gantt_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=15, pady=15)

if __name__ == "__main__":
    root = tk.Tk()  # إنشاء نافذة tkinter
    app = CPUSchedulingSimulator(root)  # تمرير نافذة tkinter إلى الكائن
    root.mainloop()  # تشغيل واجهة المستخدم