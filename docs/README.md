# Mock-and-Roll Documentation

Welcome to the Mock-and-Roll documentation. This directory contains detailed documentation organized by topic.

## 📁 Documentation Structure

### 🏗️ Architecture

- [Clean Architecture Overview](architecture/mockctl_clean_code.md) - Clean architecture implementation details
- [Refactoring Summary](architecture/REFACTORING_SUMMARY.md) - History of architectural changes and improvements

### ✨ Features

Mock-and-Roll currently provides a **robust, production-ready mock API server** with comprehensive features for:

- **Configuration-driven API development** with multiple profiles
- **Multiple authentication methods** including advanced session management
- **Dynamic response generation** with conditional logic and templates
- **Data persistence** with Redis integration and CRUD operations
- **Comprehensive logging** with powerful search and analysis capabilities
- **Professional CLI tools** for server management and operations

See [Features](./features.md).

### 🛠️ Development

- [Cleanup Summary](notes/CLEANUP_SUMMARY.md) - Recent code cleanup and version updates
- [Demo Files Cleanup](notes/DEMO_CLEANUP.md) - Removal of obsolete demo scripts
- [Documentation Organization](DOCUMENTATION_ORGANIZATION.md) - How the documentation is structured and organized

### 📦 Installation

- [Complete Installation Guide](INSTALLATION.md) - Detailed installation instructions for all platforms

## 📖 Main Documentation

For general usage, installation, and getting started, see the main [README.md](../README.md) in the project root.

### 📚 Complete Reference

- [Complete Reference Guide](COMPLETE_REFERENCE.md) - The original comprehensive documentation with all details (2800+ lines)

## 🔄 Version History

- **v0.2.0**: Added search functionality and cleaned up CLI architecture
- **v0.1.0**: Initial release with basic mock server functionality

## 🤝 Contributing

When adding new documentation:

1. **Features**: Add feature-specific documentation to `features/`
2. **Architecture**: Add architectural decisions and design docs to `architecture/`
3. **Development**: Add development process and maintenance docs to `development/`
4. **Update this index**: Add links to new documentation in the appropriate section above

## 📋 Documentation Standards

- Use clear, descriptive filenames
- Include a brief description in this index
- Follow Markdown best practices
- Include code examples where applicable
- Update the main README.md if the feature affects user-facing functionality
