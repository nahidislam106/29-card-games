# 🃏 29 Card Game - Modern Minimalist

A beautiful, modern implementation of the popular South Asian card game "29" using Python and PyGame. Features clean, minimalist card designs with smooth animations and intuitive gameplay.

![Screenshot](https://screenshot.png)

---

## 🎮 Features
- Complete 32-card deck for the traditional 29 card game  
- Modern minimalist design with rounded corners and subtle shadows  
- Smooth animations for card movement, flipping, and shuffling  
- Interactive gameplay with drag-and-drop functionality  
- Game instructions and scoring rules built-in  
- Responsive design that adapts to different screen sizes  

---

## 🎯 Game Rules (29 Card Game)

29 is a trick-taking game popular in South Asia, particularly in India, Pakistan, and Bangladesh.

**Basic Rules:**  
- **Players:** 4 players in 2 teams of 2  
- **Deck:** 32 cards (7 through Ace in all 4 suits)  
- **Trump Suit:** Determined by bidding  
- **Objective:** Win tricks containing high-value cards  

**Scoring:**

| Card | Points |
|------|--------|
| Jack | 3      |
| 9    | 2      |
| Ace  | 1      |
| 10   | 1      |
| King | 0      |
| Queen| 0      |
| 8    | 0      |
| 7    | 0      |

**Total points in deck:** 29 (hence the name!)  

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher  
- PyGame 2.5.0 or higher  

### Setup
```bash
git clone https://github.com/yourusername/29-card-game.git
cd 29-card-game
pip install pygame
python main.py

| Key         | Action                       |
| ----------- | ---------------------------- |
| Left Click  | Select and drag cards        |
| Right Click | Flip cards over              |
| Space       | Shuffle deck                 |
| R           | Reset deck to original order |
| I           | Toggle instructions panel    |
| ESC         | Quit game                    |

🎨 Design Features

Card Design:

Rounded corners with subtle shadows for depth

Clean gradient backgrounds (light gray to white)

Red color for hearts and diamonds

Black color for spades and clubs

Large stylized suit symbols in the center

Top-left and bottom-right corners showing card value and suit

Subtle texture on card surface for realism

UI Features:

Modern color palette with teal and coral accents

Smooth hover animations and selection effects

Informative overlays with game rules

Real-time card counter

Clean, uncluttered interface

📁 Project Structure
29-card-game/
├── main.py              # Main game entry point
├── README.md            # This file
├── requirements.txt     # Python dependencies
├── screenshot.png       # Game screenshot
└── assets/              # Optional assets folder
    ├── fonts/           # Custom fonts
    └── sounds/          # Sound effects

🛠️ Technical Implementation

Built With:

Python 3.12+

PyGame 2.6+

Object-Oriented Design for modular code

Key Components:

Card Class - Represents individual playing cards

Deck Class - Manages the 32-card deck

CardRenderer Class - Handles card drawing and rendering

CardGame29 Class - Main game controller

Animation System - Smooth transitions and effects

🔧 Development

Running Tests
python main.py

📝 License

This project is licensed under the MIT License - see the LICENSE
 file for details.
