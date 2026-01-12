# Contributing to HambaLang

Terima kasih atas minat Anda untuk berkontribusi pada HambaLang! 🎉

## Ways to Contribute

### 1. 🐛 Bug Reports
- Gunakan GitHub Issues
- Sertakan code snippet yang error
- Jelaskan expected vs actual behavior
- Include error messages

### 2. ✨ Feature Requests
- Gunakan GitHub Issues dengan label "enhancement"
- Jelaskan use case
- Berikan contoh syntax yang diinginkan

### 3. 📝 Code Contributions

#### New Features
- New keywords (satire atau functional)
- New built-in functions
- Performance improvements
- New examples

#### Bug Fixes
- Fix interpreter bugs
- Fix web interface issues
- Documentation fixes

### 4. 📚 Documentation
- Improve README
- Add tutorials
- Translate documentation
- Add code comments

### 5. 🎨 Examples
- Real-world applications
- Tutorial examples
- Algorithm implementations
- Creative satire programs

## Development Setup

```bash
# Fork repository
git clone https://github.com/yourusername/hambalang.git
cd hambalang

# Create branch
git checkout -b feature/your-feature-name

# Install dependencies
pip install -r requirements.txt

# For web development
cd web
npm install
```

## Code Style Guidelines

### Python Code
- Follow PEP 8
- Use meaningful variable names
- Add docstrings for functions
- Comment complex logic

### HambaLang Code (.hl)
- Use descriptive variable names
- Add comments untuk logic yang kompleks
- Follow existing syntax patterns
- Test code sebelum submit

### JavaScript/Svelte
- Use ES6+ syntax
- Follow existing code patterns
- Add comments for complex logic

## Pull Request Process

1. **Create Issue First** (untuk major changes)
2. **Fork & Create Branch**
   ```bash
   git checkout -b feature/feature-name
   ```
3. **Make Changes**
   - Write clean code
   - Add tests (jika applicable)
   - Update documentation
4. **Test Your Changes**
   ```bash
   python interpreter/hamba_v2.py examples/your_example.hl
   ```
5. **Commit**
   ```bash
   git commit -m "Add: description of feature"
   ```
6. **Push & Create PR**
   ```bash
   git push origin feature/feature-name
   ```
7. **Describe Your Changes**
   - What was changed
   - Why it was changed
   - How to test

## Commit Message Format

```
Type: Short description

Longer description if needed

Types:
- Add: New feature
- Fix: Bug fix
- Update: Improve existing feature
- Docs: Documentation only
- Style: Formatting, no code change
- Refactor: Code restructuring
- Test: Adding tests
- Chore: Build process, dependencies
```

Examples:
```
Add: Database connection pooling support

Implement connection pooling for MySQL and PostgreSQL
to improve performance for multiple concurrent queries.
```

## Satire Guidelines

HambaLang adalah satire language. Ketika menambah fitur satire:

1. **Relevan dengan konteks Indonesia**
   - Birokrasi
   - Korupsi
   - Proyek infrastruktur
   - Politik

2. **Lucu tapi tidak offensive**
   - Satir, bukan hate speech
   - Critical tapi constructive
   - Memorable

3. **Tetap functional**
   - Satire harus tetap berguna sebagai programming feature
   - Jangan pure joke tanpa fungsi

## Testing

### Interpreter Tests
```bash
# Test basic features
python interpreter/hamba_v2.py examples/full_demo.hl

# Test database
python interpreter/hamba_v2.py examples/database_example.hl

# Test file I/O
python interpreter/hamba_v2.py examples/file_io_example.hl
```

### Web Tests
```bash
cd web
npm run dev
# Test di browser
```

## Questions?

- Open a GitHub Issue
- Email: your@email.com
- Twitter: [@yourhandle](https://twitter.com/yourhandle)

## Code of Conduct

- Be respectful
- Be constructive
- Welcome newcomers
- Focus on the code, not the person
- Remember: this is satire, not serious politics

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Terima kasih atas kontribusi Anda!** 🙏

Every contribution, no matter how small, helps make HambaLang better.
