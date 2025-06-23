import tkinter as tk
from tkinter import ttk, messagebox

class Process:
    def __init__(self, name, arrival, burst, priority):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.priority = priority
        self.remaining = burst
        self.completion = 0
        self.turnaround = 0
        self.waiting = 0
        self.response = -1
        self.gantt = []

class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Scheduling Master")
        self.processes = []

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=10)

        ttk.Label(frame, text="Name").grid(row=0, column=0)
        self.name_entry = ttk.Entry(frame, width=10)
        self.name_entry.grid(row=0, column=1)

        ttk.Label(frame, text="Arrival").grid(row=0, column=2)
        self.arrival_entry = ttk.Entry(frame, width=10)
        self.arrival_entry.grid(row=0, column=3)

        ttk.Label(frame, text="Burst").grid(row=0, column=4)
        self.burst_entry = ttk.Entry(frame, width=10)
        self.burst_entry.grid(row=0, column=5)

        ttk.Label(frame, text="Priority").grid(row=0, column=6)
        self.priority_entry = ttk.Entry(frame, width=10)
        self.priority_entry.grid(row=0, column=7)

        ttk.Button(frame, text="Add Process", command=self.add_process).grid(row=0, column=8, padx=5)

        algo_frame = ttk.Frame(self.root)
        algo_frame.pack(pady=5)
        ttk.Label(algo_frame, text="Algorithm:").pack(side=tk.LEFT)
        self.algorithm = ttk.Combobox(algo_frame, values=["FCFS", "SJF", "RR", "Priority (NP)", "Priority (P)", "SRTF"])
        self.algorithm.pack(side=tk.LEFT)
        self.algorithm.current(0)

        ttk.Label(algo_frame, text="Quantum:").pack(side=tk.LEFT, padx=(10, 0))
        self.quantum_entry = ttk.Entry(algo_frame, width=5)
        self.quantum_entry.pack(side=tk.LEFT)

        ttk.Button(algo_frame, text="Run", command=self.run_scheduling).pack(side=tk.LEFT, padx=10)
        ttk.Button(algo_frame, text="Clear", command=self.clear_all).pack(side=tk.LEFT)

        self.tree = ttk.Treeview(self.root, columns=("Name", "Arrival", "Burst", "Priority", "CT", "TAT", "WT", "RT"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(padx=10, pady=10, fill=tk.X)

        self.avg_label = tk.Label(self.root, text="", font=("Arial", 10, "bold"))
        self.avg_label.pack()

        self.canvas = tk.Canvas(self.root, height=80, bg="white")
        self.canvas.pack(padx=10, pady=10, fill=tk.X)

    def add_process(self):
        try:
            name = self.name_entry.get()
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            priority = int(self.priority_entry.get())

            if not name:
                raise ValueError("Name cannot be empty.")

            if any(p.name == name for p in self.processes):
                messagebox.showerror("Duplicate Name", f"Process '{name}' already exists.")
                return

            new_proc = Process(name, arrival, burst, priority)
            self.processes.append(new_proc)

            self.tree.insert("", tk.END, values=(name, arrival, burst, priority, "", "", "", ""))

            self.name_entry.delete(0, tk.END)
            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
            self.priority_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values and a non-empty name.")

    def clear_all(self):
        self.processes.clear()
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.canvas.delete("all")
        self.avg_label.config(text="")

    def run_scheduling(self):
        algo = self.algorithm.get()
        for p in self.processes:
            p.remaining = p.burst
            p.completion = p.turnaround = p.waiting = 0
            p.response = -1
            p.gantt = []

        if algo == "FCFS":
            self.fcfs()
        elif algo == "SJF":
            self.sjf()
        elif algo == "RR":
            try:
                quantum = int(self.quantum_entry.get())
                self.rr(quantum)
            except ValueError:
                messagebox.showerror("Invalid Quantum", "Please enter a valid time quantum.")
                return
        elif algo == "Priority (NP)":
            self.priority_np()
        elif algo == "Priority (P)":
            self.priority_p()
        elif algo == "SRTF":
            self.srtf()
        self.display_results()
        self.draw_gantt()

    def display_results(self):
        self.tree.delete(*self.tree.get_children())
        total_wt = total_tat = 0
        for p in self.processes:
            self.tree.insert("", tk.END, values=(p.name, p.arrival, p.burst, p.priority, p.completion, p.turnaround, p.waiting, p.response))
            total_wt += p.waiting
            total_tat += p.turnaround
        n = len(self.processes)
        if n > 0:
            avg_text = f"Average Waiting Time: {total_wt/n:.2f} | Average Turnaround Time: {total_tat/n:.2f}"
            self.avg_label.config(text=avg_text)

    def draw_gantt(self):
        self.canvas.delete("all")
        time_unit = 30
        x = 10
        y = 30
        timeline = []
        for p in self.processes:
            timeline.extend(p.gantt)

        for block in timeline:
            name, start, end = block
            width = (end - start) * time_unit
            self.canvas.create_rectangle(x, y, x + width, y + 30, fill="#4caf50", outline="black")
            self.canvas.create_text(x + width / 2, y + 15, text=name, fill="white")
            self.canvas.create_text(x, y + 40, text=str(start), anchor="n")
            x += width
        if timeline:
            self.canvas.create_text(x, y + 40, text=str(timeline[-1][2]), anchor="n")

    def fcfs(self):
        self.processes.sort(key=lambda p: p.arrival)
        time = 0
        for p in self.processes:
            if time < p.arrival:
                time = p.arrival
            if p.response == -1:
                p.response = time - p.arrival
            p.gantt.append((p.name, time, time + p.burst))
            time += p.burst
            p.completion = time
            p.turnaround = p.completion - p.arrival
            p.waiting = p.turnaround - p.burst

    def sjf(self):
        time = 0
        completed = 0
        n = len(self.processes)
        visited = [False] * n
        while completed < n:
            available = [(i, p) for i, p in enumerate(self.processes) if not visited[i] and p.arrival <= time]
            if not available:
                time += 1
                continue
            idx, proc = min(available, key=lambda x: x[1].burst)
            if proc.response == -1:
                proc.response = time - proc.arrival
            proc.gantt.append((proc.name, time, time + proc.burst))
            time += proc.burst
            proc.completion = time
            proc.turnaround = proc.completion - proc.arrival
            proc.waiting = proc.turnaround - proc.burst
            visited[idx] = True
            completed += 1

    def rr(self, quantum):
        time = 0
        queue = sorted(self.processes, key=lambda p: p.arrival)
        n = len(queue)
        completed = 0
        ready_queue = []
        index = 0
        while completed < n:
            for p in queue:
                if p.arrival <= time and p not in ready_queue and p.remaining > 0:
                    ready_queue.append(p)

            if not ready_queue:
                time += 1
                continue

            p = ready_queue.pop(0)
            if p.response == -1:
                p.response = time - p.arrival
            run_time = min(p.remaining, quantum)
            p.gantt.append((p.name, time, time + run_time))
            time += run_time
            p.remaining -= run_time
            if p.remaining == 0:
                p.completion = time
                p.turnaround = p.completion - p.arrival
                p.waiting = p.turnaround - p.burst
                completed += 1
            else:
                for proc in queue:
                    if proc.arrival <= time and proc not in ready_queue and proc.remaining > 0:
                        ready_queue.append(proc)
                ready_queue.append(p)

    def priority_np(self):
        time = 0
        completed = 0
        n = len(self.processes)
        visited = [False] * n
        while completed < n:
            available = [(i, p) for i, p in enumerate(self.processes) if not visited[i] and p.arrival <= time]
            if not available:
                time += 1
                continue
            idx, proc = min(available, key=lambda x: x[1].priority)
            if proc.response == -1:
                proc.response = time - proc.arrival
            proc.gantt.append((proc.name, time, time + proc.burst))
            time += proc.burst
            proc.completion = time
            proc.turnaround = proc.completion - proc.arrival
            proc.waiting = proc.turnaround - proc.burst
            visited[idx] = True
            completed += 1

    def priority_p(self):
        time = 0
        completed = 0
        n = len(self.processes)
        while completed < n:
            available = [p for p in self.processes if p.arrival <= time and p.remaining > 0]
            if not available:
                time += 1
                continue
            proc = min(available, key=lambda p: p.priority)
            if proc.response == -1:
                proc.response = time - proc.arrival
            proc.gantt.append((proc.name, time, time + 1))
            proc.remaining -= 1
            time += 1
            if proc.remaining == 0:
                proc.completion = time
                proc.turnaround = proc.completion - proc.arrival
                proc.waiting = proc.turnaround - proc.burst
                completed += 1

    def srtf(self):
        time = 0
        completed = 0
        n = len(self.processes)
        while completed < n:
            available = [p for p in self.processes if p.arrival <= time and p.remaining > 0]
            if not available:
                time += 1
                continue
            proc = min(available, key=lambda p: p.remaining)
            if proc.response == -1:
                proc.response = time - proc.arrival
            proc.gantt.append((proc.name, time, time + 1))
            proc.remaining -= 1
            time += 1
            if proc.remaining == 0:
                proc.completion = time
                proc.turnaround = proc.completion - proc.arrival
                proc.waiting = proc.turnaround - proc.burst
                completed += 1

if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()
