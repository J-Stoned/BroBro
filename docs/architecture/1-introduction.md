# 1. Introduction

This document outlines the complete system architecture for **GHL Wiz**, a comprehensive AI assistant with deep GoHighLevel domain expertise, powered by Retrieval-Augmented Generation (RAG) technology and integrated with Claude Code via the Model Context Protocol (MCP).

### 1.1 Project Context

**Starter Template:** N/A - Greenfield project with custom MCP server development

**Architectural Approach:** Local-first, modular microservices architecture using MCP protocol for component communication, designed for Windows desktop deployment with future cloud migration path.

### 1.2 Design Philosophy

- **Local-First**: All components run on user's Windows machine, no cloud dependencies for MVP
- **Modular**: MCP servers as independent microservices, independently deployable and testable
- **Knowledge-Centric**: RAG architecture with comprehensive knowledge base at the core
- **Developer Experience**: Fast setup, clear documentation, extensible design
- **Performance**: <2 second query response time, optimized embeddings and search
- **Security**: Encrypted OAuth storage, secure API key management, no secrets in version control

---
