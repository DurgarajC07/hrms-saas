# Contributing to HRMS SaaS

Thank you for your interest in contributing to HRMS SaaS! We welcome contributions from the community.

## 🚀 How to Contribute

### Reporting Issues

1. **Search existing issues** to avoid duplicates
2. **Use the issue template** when creating new issues
3. **Provide detailed information** including:
   - Operating system and version
   - Python version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages or logs

### Development Setup

1. **Fork the repository**

   ```bash
   git clone https://github.com/yourusername/hrms-saas.git
   cd hrms-saas
   ```

2. **Set up development environment**

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Guidelines

#### Code Style

- Follow **PEP 8** Python style guide
- Use **type hints** for all function parameters and return values
- Write **docstrings** for all public functions and classes
- Keep line length under **88 characters** (Black formatter)

#### Testing

- Write tests for all new features
- Maintain **90%+ test coverage**
- Run tests before submitting PR:
  ```bash
  pytest --cov=app --cov-report=html
  ```

#### Commit Guidelines

- Use **conventional commits** format:
  ```
  feat: add employee expense tracking
  fix: resolve payroll calculation bug
  docs: update API documentation
  test: add attendance tracking tests
  ```

#### Pull Request Process

1. **Update documentation** if needed
2. **Add/update tests** for your changes
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** with your changes
5. **Submit pull request** with:
   - Clear description of changes
   - Link to related issues
   - Screenshots (if UI changes)

### Code Review Process

- All PRs require **at least one approval**
- Maintainers will review within **48 hours**
- Address feedback promptly
- Keep PRs **focused and small** when possible

### Feature Requests

1. **Open an issue** with the `enhancement` label
2. **Describe the feature** and use case
3. **Discuss implementation** approach
4. **Wait for approval** before starting work

## 🏗️ Architecture Guidelines

### Database Changes

- Create **migration scripts** for schema changes
- Ensure **backward compatibility** when possible
- Test migrations on sample data

### API Design

- Follow **RESTful principles**
- Use appropriate **HTTP status codes**
- Implement proper **error handling**
- Add **comprehensive documentation**

### Security

- **Never commit secrets** or credentials
- Follow **OWASP security guidelines**
- Implement **input validation**
- Use **secure coding practices**

## 📚 Development Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM Guide](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

## 🤔 Questions?

- **General questions**: Use GitHub Discussions
- **Bug reports**: Create GitHub Issues
- **Feature requests**: Create GitHub Issues with enhancement label
- **Security issues**: Email security@hrms-saas.com

## 📝 License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to HRMS SaaS! 🎉
