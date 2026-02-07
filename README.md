# Wordle-Solves

A repository containing multiple strategies and approaches for solving the popular word game **Wordle**. The goal of this project is to explore algorithmic, heuristic, and machine learning-based solutions to efficiently solve Wordle puzzles.

---

## About

**Wordle-Solves** is an experimentation and research-oriented repository designed to explore different techniques for solving Wordle puzzles programmatically. This includes:

* Brute force strategies
* Heuristic-based solvers
* Information theory approaches
* Probabilistic models
* Reinforcement learning experiments
* Performance and efficiency comparisons between solving methods

The project aims to serve both as a practical solver collection and as a personal learning resource for algorithm design, optimization, and applied problem-solving.

---

## Data Sources

This project relies on publicly available Wordle word lists that define:

* Valid guess words
* Official daily solution words

These datasets are sourced from the following repository:

👉 [https://github.com/seanpatlan/wordle-words](https://github.com/seanpatlan/wordle-words)

### Included Datasets

* **valid-words.csv**
  Contains all words considered valid guesses by Wordle (~12,972 words).

* **word-bank.csv**
  Contains the list of words from which the daily Wordle solution is selected (~2,315 words).

These lists were accurate as of February 7, 2022, and may differ from newer Wordle versions following New York Times ownership changes.

---

## Acknowledgements

Special thanks to **Sean Patlan** for compiling and sharing the Wordle word lists that make this project possible:

👉 [https://github.com/seanpatlan/wordle-words](https://github.com/seanpatlan/wordle-words)

Providing these datasets significantly simplifies solver development and allows experimentation without needing to reconstruct the original game data.

Additional thanks go to:

* The original Wordle creator, Josh Wardle, for designing the game.
* The open-source community for tools, ideas, and discussions around algorithmic puzzle solving.

---

## Goals of the Repository

This project aims to:

* Compare solver strategies and their performance
* Analyze optimal guessing patterns
* Explore statistical and information-theoretic approaches
* Provide reusable and modular solver implementations
* Serve as an experimentation playground for optimization and AI techniques

---

## Disclaimer

This repository is intended for educational and experimental purposes. Word lists included or referenced are community-collected datasets and may not reflect the official or current Wordle word set.

---

## License

Refer to the repository license for usage terms and distribution rights.

---

## Contributions

Contributions, ideas, and solver strategies are welcome. Feel free to open issues or pull requests to discuss improvements or new solving approaches.
