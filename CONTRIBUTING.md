# Contributing to SampoNLP

Thank you for your interest in contributing to SampoNLP! We welcome contributions from the community.

## Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit bug fixes
- ✨ Add new features
- 🌍 Add support for new languages

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/samponlp.git
   cd samponlp
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Rust (for building the core library)
- Git

### Installation

```bash
# Install Rust if you haven't already
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Python dependencies
pip install -r requirements-dev.txt

# Build the Rust extension
pip install maturin
maturin develop --release
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_pipeline.py

# Run with coverage
pytest --cov=samponlp tests/
```

## Code Style

### Python
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where appropriate
- Write docstrings for all public functions and classes

### Rust
- Follow [Rust style guidelines](https://doc.rust-lang.org/1.0.0/style/)
- Run `cargo fmt` before committing
- Run `cargo clippy` to catch common mistakes

## Commit Guidelines

- Use clear and meaningful commit messages
- Start with a verb in present tense (e.g., "Add", "Fix", "Update")
- Keep commits focused on a single change
- Reference issue numbers when applicable

Example:
```
Add support for Karelian language

- Add alphabet validation pattern
- Update whitelist for single-char morphemes
- Add language tests

Fixes #42
```

## Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Add tests** for new features
3. **Ensure all tests pass** locally
4. **Update CHANGELOG.md** with your changes
5. **Submit the pull request** with a clear description

### PR Description Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
Describe how you tested your changes

## Checklist
- [ ] My code follows the project's code style
- [ ] I have added tests for my changes
- [ ] All tests pass locally
- [ ] I have updated the documentation
- [ ] I have updated CHANGELOG.md
```

## Reporting Bugs

When reporting bugs, please include:

- **Description**: Clear description of the bug
- **Steps to reproduce**: Minimal code to reproduce the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: OS, Python version, SampoNLP version
- **Traceback**: Full error message if applicable

## Suggesting Features

Feature suggestions are welcome! Please:

1. Check if the feature has already been requested
2. Provide a clear use case
3. Explain why this feature would be useful
4. Consider offering to implement it yourself

## Questions?

If you have questions, feel free to:
- Open an issue with the "question" label
- Email: les4sixstm@gmail.com

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.

## Recognition

Contributors will be recognized in:
- README.md acknowledgments section
- CHANGELOG.md for each release
- GitHub contributors page

Thank you for making SampoNLP better! 🎉
