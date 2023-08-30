# Flappy Bird BOT

This is an AI bot that learns to play the game Flappy Bird by itself. It use the [NEAT](https://neat-python.readthedocs.io/en/latest/) module in python to achieve this.

[Run the application in your browser]()

# Installation

1. Download the code in a ZIP format and unzip it in a folder of your choice.
2. Open Terminal and install neat-python and pygame modules.

```bash
  pip install pygame
  pip install neat-python
  python3 -u main.py
```

3. Run the main.py file.

## Working

This code uses search and optimise technique called genetic algorithm which creates a particular number of random configurations, the best configuration of them is used to create the next generation of neural networks, as we repeat the process, with time, we observe that the performance gets better.

## Screenshots

Running
![running](https://user-images.githubusercontent.com/97015991/264217835-f9719a48-5cad-473f-b077-e9e69bb5204c.png)
Output
![output](https://user-images.githubusercontent.com/97015991/264217857-71a1c0e0-4c6b-4486-89bc-2744491598d0.png)
