# Mock-and-Roll

A highly configurable and extensible mock REST API server built with FastAPI.

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/bvandewe/mock-and-roll)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## What is Mock-and-Roll?

Mock-and-Roll is a powerful and flexible mock API server that allows you to quickly create realistic API endpoints for testing, development, and demonstration purposes. Built with FastAPI, it provides high performance and automatic API documentation.

- 📚 Full documentation at [https://bvandewe.github.io/mock-and-roll/](https://bvandewe.github.io/mock-and-roll/)
- ⚠️ Public Repository at [https://github.com/bvandewe/mock-and-roll](https://github.com/bvandewe/mock-and-roll)

## ✨ Key Features

### 🚀 **Quick Setup**

- **Zero Configuration**: Get started with pre-built configuration profiles
- **CLI Tool**: Easy server management with `mockctl` command
- **Docker Support**: Run anywhere with Docker containers

### 🔧 **Highly Configurable**

- **Configuration Profiles**: Basic, Persistence, and vManage simulation profiles
- **Dynamic Endpoints**: Define custom endpoints through JSON configuration
- **Flexible Authentication**: Support for API keys, OAuth, and custom auth methods

### 📊 **Advanced Features**

- **Log Searching**: Built-in search functionality with regex pattern support
- **Redis Persistence**: Optional data persistence with Redis integration
- **Real-time Monitoring**: Comprehensive logging and request tracking
- **Template System**: Dynamic response generation with variable substitution

### 🔍 **Developer Experience**

- **Interactive Documentation**: Automatic OpenAPI/Swagger documentation
- **CLI Management**: Start, stop, and monitor servers with simple commands
- **Alpine Linux Support**: Optimized for minimal container deployments

## 🎯 Quick Start

### Install and Run

```bash
# Clone the repository
git clone https://github.com/bvandewe/mock-and-roll.git
cd mock-and-roll

# Quick setup (choose your platform)
./setup/alpine_minimal.sh    # For Alpine Linux
./setup/add_to_path.sh       # Add mockctl to your PATH

# or use Docker
docker-compose up

# Start a mock server
./mockctl start basic        # Basic configuration
./mockctl start vmanage      # Cisco vManage simulation
./mockctl start persistence  # With Redis persistence
```

### Example Usage

```bash
# Start a basic mock server
mockctl start basic

# Search logs for authentication requests
mockctl --json search "/auth" | jq .

# List running servers
mockctl list

# Stop all servers
mockctl stop --all
```

## 📋 Use Cases

### 🧪 **Testing & Development**

- Mock external APIs during development
- Create consistent test environments
- Simulate various response scenarios

### 🎓 **Training & Demonstrations**

- API training workshops
- Product demonstrations
- Educational environments

### 🔌 **Integration Testing**

- Test client applications against known API responses
- Validate error handling scenarios
- Performance testing with realistic data

### 🌐 **Network Simulation**

- Cisco vManage API simulation
- Custom enterprise API mocking
- Protocol testing environments

## 🏗️ Architecture

Mock-and-Roll follows a clean, modular architecture:

- **Configuration-driven**: All behavior defined through JSON files
- **Plugin Architecture**: Extensible authentication and response handlers
- **Domain-driven Design**: Clean separation of concerns
- **FastAPI Foundation**: High-performance async API framework

## 🚀 What's Next?

<!-- markdownlint-disable MD007 MD030 MD032 -->
<!-- prettier-ignore-start -->
<div class="grid cards" markdown="1">

- :rocket: **Get Started**

    ---

    Jump right in with our quick installation guide

    [:octicons-arrow-right-24: Installation](installation.md)

- :gear: **Configuration**

    ---

    Learn about configuration profiles and customization

    [:octicons-arrow-right-24: Configuration](configuration.md)

- :computer: **CLI Reference**

    ---

    Master the mockctl command-line tool

    [:octicons-arrow-right-24: CLI Commands](user-guide/cli-commands.md)

- :books: **Examples**

    ---

    Explore real-world usage examples

    [:octicons-arrow-right-24: Examples](examples/basic-usage.md)

</div>
<!-- prettier-ignore-end -->
<!-- markdownlint-enable MD007 MD030 MD032 -->

## 📞 Support & Community

- **GitHub Issues**: [Report bugs or request features](https://github.com/bvandewe/mock-and-roll/issues)
- **Documentation**: Comprehensive guides and API reference
- **Examples**: Real-world configuration examples and use cases

---

Mock-and-Roll empowers developers to create realistic API environments quickly and efficiently, making testing and development workflows smoother and more reliable.
