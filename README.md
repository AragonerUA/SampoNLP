<h1 align="center">SampoNLP</h1>
<p align="center">Unsupervised Morpheme Discovery for Uralic Languages</p>

[![PyPI version](https://badge.fury.io/py/samponlp.svg)](https://badge.fury.io/py/samponlp)
[![Downloads](https://static.pepy.tech/badge/samponlp)](https://pepy.tech/project/samponlp)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

SampoNLP is a high-performance library for **unsupervised morpheme discovery** from raw text corpora. It implements the **Iterative Morpheme Decomposition with Positional Priors (IMDP)** algorithm, specifically designed for morphologically rich languages such as Finnish, Estonian, and Hungarian.

The library uses a Rust-accelerated core for efficient computation, wrapped in a user-friendly Python API.

## 🌟 Features

- ✨ **Unsupervised Learning**: No annotated data required
- 🚀 **High Performance**: Rust-powered core with Python bindings via PyO3
- 🔬 **Linguistically Motivated**: Incorporates positional priors for roots vs. affixes
- 🌍 **Multi-Language Support**: Pre-configured for Finnish, Estonian, Hungarian, and general Uralic languages
- 📊 **Automatic Thresholding**: Uses Otsu's method for intelligent morpheme filtering
- 🔄 **Iterative Refinement**: Converges to stable morpheme representations

## 📦 Installation

### From PyPI (recommended)

```bash
pip install samponlp
```

### From source

```bash
git clone https://github.com/yourusername/samponlp.git
cd samponlp
pip install maturin
maturin develop --release
```

## 🚀 Quick Start

### Basic Usage

```python
from samponlp import MorphemeCleaner

# Initialize the cleaner for Estonian
cleaner = MorphemeCleaner(
    language='estonian',
    min_length=1,
    min_type_support=3,
    max_iterations=100,
    convergence_threshold=1e-7
)

# Process morphemes from a file
results = cleaner.process(
    raw_morphemes_path='data/estonian_morphemes.txt',
    output_dir='results/estonian_output'
)

print(f"Found {results.morpheme_count} atomic morphemes")
print(f"Discarded {len(results.discarded)} tokens")
```

### Analyzing Results

```python
# Access cleaned morphemes
for morpheme in results.morphemes[:10]:
    print(morpheme)

# Check discarded tokens with reasons
for token, reason in results.discarded[:5]:
    print(f"{token}: {reason}")

# Examine final scores
print(results.final_scores['ház'])  # 0.334
```

## 📚 Supported Languages

SampoNLP comes with pre-configured settings for:

- 🇫🇮 **Finnish** (`language='finnish'`)
- 🇪🇪 **Estonian** (`language='estonian'`)
- 🇭🇺 **Hungarian** (`language='hungarian'`)
- 🌐 **General Uralic** (`language='uralic'`)

Each language has customized:
- Alphabet validation patterns
- Single-character morpheme whitelists
- Language-specific filtering rules

## 🔬 Algorithm Overview

SampoNLP implements the **IMDP (Iterative Morpheme Decomposition with Positional Priors)** algorithm:

1. **Initial Filtering**: Removes noise based on alphabet, type-support, and heuristics
2. **Iterative Scoring**: Uses dynamic programming to find optimal morpheme decompositions
3. **Positional Priors**: Applies different rules for roots (can split anywhere) vs. affixes (edge-only splits)
4. **Automatic Thresholding**: Employs Otsu's method to separate atomic from composite morphemes

For detailed algorithm description, see our paper (link coming soon).

## 📖 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) folder:

- [Usage Guide](docs/usage.md) - Detailed examples and API reference
- [Algorithm Details](docs/algorithm.md) - Mathematical formulation
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

## 🛠️ Development

### Building from Source

```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Clone the repository
git clone https://github.com/yourusername/samponlp.git
cd samponlp

# Build with maturin
pip install maturin
maturin develop --release

# Run tests
pytest tests/
```

### Running the Pipeline

```bash
python run_pipeline.py
```

## 📄 License

SampoNLP is released under the [Apache 2.0 License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 🙏 Acknowledgments

This project was inspired by morphological analysis needs in computational linguistics research for Uralic languages.

---

<p align="center">Made with ❤️ for the Uralic NLP community</p>
