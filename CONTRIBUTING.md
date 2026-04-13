# Contributing to Stock Analyzer

Thank you for your interest in contributing to the Stock Analyzer project! Here are some guidelines to help you get started.

## Code of Conduct

- Be respectful and inclusive
- Avoid offensive language or behavior
- Focus on constructive feedback

## How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Provide clear details:**
   - Python version and OS
   - Steps to reproduce the bug
   - Expected vs. actual behavior
   - Error messages or screenshots

### Suggesting Features

1. Describe the feature clearly
2. Explain the use case and benefits
3. Provide examples if possible
4. Check if a similar feature exists

### Submitting Code

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/stock-analyzer.git
   cd stock-analyzer
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Keep commits atomic and descriptive
   - Follow PEP 8 style guidelines
   - Add comments for complex logic
   - Test your code thoroughly

4. **Commit your changes**
   ```bash
   git commit -m "Add brief description of changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**
   - Describe what changes you made
   - Link related issues
   - Explain the rationale

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Code Style

- Follow **PEP 8** standards
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and DRY (Don't Repeat Yourself)

## Testing

- Write tests for new features
- Ensure all tests pass before submitting
- Test with Python 3.10, 3.11, and 3.12

## Documentation

- Update README.md if adding features
- Add docstrings to new functions
- Update setup.py if adding dependencies

## License

By contributing, you agree that your contributions will be licensed under the project's license.

## Questions?

Feel free to open an issue or contact the maintainers at aryan.maurya@example.com

---

Thank you for making Stock Analyzer better! 🚀
