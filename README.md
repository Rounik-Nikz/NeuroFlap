## 🧠 `NeuroFlap` – Flappy Bird AI Trained with NEAT

Train an AI to play **Flappy Bird** using **NEAT (NeuroEvolution of Augmenting Topologies)** – a genetic algorithm that evolves neural networks without requiring backpropagation. In this project, birds learn to fly *by evolving brains* through generations.

---

### 📚 What is NEAT?

**NEAT (NeuroEvolution of Augmenting Topologies)** is an evolutionary algorithm that:
- Starts with simple neural networks (minimal topology).
- Evolves them over generations using **mutation**, **crossover**, and **selection**.
- Adds **new nodes and connections** over time to grow smarter, more complex networks.
- Keeps innovations safe through **speciation**, so new ideas have time to improve.

In short: **NEAT teaches AI how to think**, from scratch, by simulating evolution.

---

### 🧠 How NEAT Works in This Project

In `NeuroFlap`:

1. **Initial Population**  
   100+ birds are spawned with random brains (neural networks).

2. **Fitness Evaluation**  
   Each bird plays Flappy Bird. Its **score** becomes its **fitness**.

3. **Evolution**  
   After each generation:
   - Top-performing birds are selected.
   - New birds are created via crossover and mutation.
   - Networks may grow by adding nodes or connections.
   - NEAT ensures innovative birds aren't immediately wiped out.

4. **Training Loop**  
   This process continues for 50–100+ generations until one bird learns to master the pipes.

---

### 🎮 How It Plays

- The neural network gets inputs like:
  - Bird's vertical position
  - Distance to next pipe
  - Gap size
  - Bird's velocity

- It outputs a **single value**:
  - If the value > 0.5 → bird flaps.
  - Else → bird does nothing and falls.

Over time, the bird **learns when to flap** to pass through pipes and stay alive longer.

---

## 🚀 Features

✅ NEAT-Python Integration  
✅ Pygame-based Simulation  
✅ Training & Inference Modes  
✅ NEAT Configurable Parameters  
✅ Visualize Neural Networks via Graphviz  

---

## 🛠 Tech Stack

- Python 🐍
- Pygame 🎮
- NEAT-Python 🧬
- Graphviz-Python 🖼️

---

## ⭐ Show your support!

If this project helped you learn or gave you cool AI ideas, drop a ⭐ on the repo!
