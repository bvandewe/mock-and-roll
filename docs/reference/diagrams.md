# Diagrams and Visualizations

This page demonstrates the various types of diagrams available in the Mock-and-Roll documentation using Mermaid.

## Architecture Diagrams

### System Overview

```mermaid
graph TB
    subgraph "Client Layer"
        Client[API Client]
        Swagger[Swagger UI]
    end
    
    subgraph "Application Layer"
        FastAPI[FastAPI Server]
        Auth[Authentication Middleware]
        Routes[Dynamic Route Handler]
        Logging[Logging Middleware]
    end
    
    subgraph "Configuration Layer"
        Loader[Config Loader]
        Basic[Basic Profile]
        Persistence[Persistence Profile]
        vManage[vManage Profile]
    end
    
    subgraph "Storage Layer"
        Redis[(Redis)]
        Logs[Log Files]
    end
    
    Client --> FastAPI
    Swagger --> FastAPI
    FastAPI --> Auth
    Auth --> Routes
    Routes --> Logging
    
    Loader --> Basic
    Loader --> Persistence
    Loader --> vManage
    
    Routes --> Redis
    Logging --> Logs
    
    FastAPI <--> Loader
```

### CLI Architecture

```mermaid
graph LR
    subgraph "Interface Layer"
        CLI[mockctl CLI]
        Commands[Command Parser]
    end
    
    subgraph "Application Layer"
        ServerMgmt[Server Management]
        LogSearch[Log Search]
        ProcessMgmt[Process Management]
    end
    
    subgraph "Domain Layer"
        Entities[Server Entities]
        Services[Domain Services]
    end
    
    subgraph "Infrastructure Layer"
        FileSystem[File System]
        ProcessAPI[Process API]
        LogParser[Log Parser]
    end
    
    CLI --> Commands
    Commands --> ServerMgmt
    Commands --> LogSearch
    Commands --> ProcessMgmt
    
    ServerMgmt --> Entities
    LogSearch --> Services
    ProcessMgmt --> Entities
    
    ServerMgmt --> FileSystem
    LogSearch --> LogParser
    ProcessMgmt --> ProcessAPI
```

## Request Flow Diagrams

### API Request Processing

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Auth
    participant Router
    participant Handler
    participant Redis
    participant Templates
    
    Client->>FastAPI: HTTP Request
    FastAPI->>Auth: Validate Authentication
    
    alt Authentication Success
        Auth->>Router: Forward Request
        Router->>Handler: Route to Handler
        
        alt Persistence Enabled
            Handler->>Redis: Check/Store Data
            Redis->>Handler: Data Response
        end
        
        Handler->>Templates: Process Templates
        Templates->>Handler: Rendered Response
        Handler->>FastAPI: Response Data
        FastAPI->>Client: HTTP Response
    else Authentication Failed
        Auth->>FastAPI: 401 Unauthorized
        FastAPI->>Client: Error Response
    end
```

### CLI Server Management

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Config
    participant Process
    participant Server
    
    User->>CLI: mockctl start
    CLI->>Config: Load Configuration
    Config->>CLI: Configuration Data
    
    CLI->>Process: Check Existing Servers
    Process->>CLI: Process Status
    
    alt Port Available
        CLI->>Process: Start New Server
        Process->>Server: Launch FastAPI
        Server->>Process: PID & Status
        Process->>CLI: Success Response
        CLI->>User: Server Started
    else Port Occupied
        CLI->>User: Port Conflict Error
    end
```

## State Diagrams

### Server Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Stopped
    Stopped --> Starting: mockctl start
    Starting --> Running: Success
    Starting --> Error: Configuration Error
    Error --> Stopped: Fix Configuration
    Running --> Stopping: mockctl stop
    Stopping --> Stopped: Process Terminated
    Running --> Error: Runtime Error
    Error --> Running: Auto Recovery
```

### Authentication Flow

```mermaid
stateDiagram-v2
    [*] --> Unauthenticated
    Unauthenticated --> Checking: Credentials Provided
    Checking --> Authenticated: Valid Credentials
    Checking --> Unauthenticated: Invalid Credentials
    Authenticated --> Processing: Request Processing
    Processing --> Response: Success
    Processing --> Error: Processing Error
    Response --> [*]
    Error --> [*]
```

## Data Flow Diagrams

### Configuration Loading

```mermaid
flowchart TD
    Start([Start Application]) --> LoadEnv[Load Environment Variables]
    LoadEnv --> CheckProfile{Profile Specified?}
    
    CheckProfile -->|Yes| LoadProfile[Load Specified Profile]
    CheckProfile -->|No| SelectProfile[Interactive Profile Selection]
    
    LoadProfile --> ValidateConfig[Validate Configuration]
    SelectProfile --> ValidateConfig
    
    ValidateConfig --> ConfigValid{Configuration Valid?}
    ConfigValid -->|Yes| InitializeApp[Initialize FastAPI App]
    ConfigValid -->|No| ShowError[Show Configuration Error]
    
    InitializeApp --> StartServer[Start Server]
    ShowError --> End([Exit])
    StartServer --> End
```

### Log Search Process

```mermaid
flowchart LR
    Input[Search Query] --> Parse[Parse Parameters]
    Parse --> Files[Scan Log Files]
    Files --> Filter[Apply Filters]
    
    subgraph "Filtering"
        Filter --> TimeFilter[Time Range Filter]
        TimeFilter --> PathFilter[Path Pattern Filter]
        PathFilter --> StatusFilter[Status Code Filter]
    end
    
    StatusFilter --> Group[Group Results]
    Group --> Format[Format Output]
    Format --> Display[Display Results]
```

## Component Diagrams

### Plugin Architecture

```mermaid
graph TB
    subgraph "Core System"
        App[FastAPI Application]
        Router[Route Manager]
        Config[Configuration System]
    end
    
    subgraph "Authentication Plugins"
        APIKey[API Key Plugin]
        OAuth[OAuth Plugin]
        Basic[Basic Auth Plugin]
        CSRF[CSRF Plugin]
    end
    
    subgraph "Storage Plugins"
        Memory[Memory Storage]
        Redis[Redis Storage]
        File[File Storage]
    end
    
    subgraph "Template Plugins"
        Jinja[Jinja2 Templates]
        Static[Static Responses]
        Dynamic[Dynamic Values]
    end
    
    App --> Router
    Router --> Config
    
    Router --> APIKey
    Router --> OAuth
    Router --> Basic
    Router --> CSRF
    
    Router --> Memory
    Router --> Redis
    Router --> File
    
    Router --> Jinja
    Router --> Static
    Router --> Dynamic
```

## Class Relationships

### Domain Model

```mermaid
classDiagram
    class Server {
        +String name
        +Integer port
        +String config_profile
        +ProcessStatus status
        +start()
        +stop()
        +restart()
    }
    
    class ServerManager {
        +List~Server~ servers
        +start_server(profile)
        +stop_server(port)
        +list_servers()
        +find_by_port(port)
    }
    
    class LogSearchEngine {
        +String log_directory
        +search(query, filters)
        +parse_log_entry(line)
        +apply_filters(entries)
    }
    
    class ConfigurationProfile {
        +String name
        +Dict api_config
        +Dict auth_config
        +Dict endpoints_config
        +load()
        +validate()
    }
    
    ServerManager --> Server : manages
    Server --> ConfigurationProfile : uses
    LogSearchEngine --> Server : searches logs
```

## Timeline Diagrams

### Development Timeline

```mermaid
timeline
    title Mock-and-Roll Development Timeline
    
    section Version 0.1.0
        August 2024 : Initial Release
                    : FastAPI Foundation
                    : Basic Configuration System
                    : API Key Authentication
    
    section Version 0.2.0
        September 2024 : CLI Enhancement
                       : Advanced Log Search
                       : Clean Architecture
                       : Multiple Auth Methods
    
    section Future Releases
        Q4 2024 : Plugin System
                : Advanced Templating
                : Performance Optimization
        
        Q1 2025 : Web UI
                : Monitoring Dashboard
                : Cloud Deployment
```

## Usage Examples

### Basic Mermaid Syntax

To add a Mermaid diagram to your documentation, use the following syntax:

````markdown
```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```
````

### Supported Diagram Types

The following Mermaid diagram types are supported:

- **Flowcharts**: `graph TD`, `graph LR`
- **Sequence Diagrams**: `sequenceDiagram`
- **State Diagrams**: `stateDiagram-v2`
- **Class Diagrams**: `classDiagram`
- **Entity Relationship**: `erDiagram`
- **User Journey**: `journey`
- **Gantt Charts**: `gantt`
- **Pie Charts**: `pie`
- **Timeline**: `timeline`

### Theme Support

Mermaid diagrams automatically adapt to the documentation theme:

- **Light Mode**: Clean, professional appearance
- **Dark Mode**: Optimized colors for dark backgrounds
- **Auto Theme**: Automatically switches based on user preference

The `theme: auto` configuration ensures diagrams look great in both light and dark modes!
