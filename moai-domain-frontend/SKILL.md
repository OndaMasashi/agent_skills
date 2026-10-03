---
name: "moai-domain-frontend"
description: |
  Frontend development specialist covering React 19, Next.js 16, Vue 3.5, and modern UI/UX patterns with component architecture. Use when building web UIs, implementing components, optimizing frontend performance, or integrating state management. 日本語トリガー: フロントエンド開発、UIコンポーネントを実装、Reactコンポーネントを作って、Next.jsアプリを構築、Vueコンポーネント作成、状態管理を実装。ビジュアルデザイン・配色・スタイル選定のみが目的ならui-ux-pro-maxやfrontend-designを使う。Reactのコンポーネント合成パターンのみの相談ならcomposition-patternsを使う。
version: 2.0.0
category: "domain"
modularized: true
user-invocable: false
tags: ['frontend', 'react', 'nextjs', 'vue', 'ui', 'components']
context7-libraries: ['/facebook/react', '/vercel/next.js', '/vuejs/vue']
updated: 2026-01-11
allowed-tools:
  - Read
  - Grep
  - Glob
  - mcp__context7__resolve-library-id
  - mcp__context7__get-library-docs
status: "active"
author: "MoAI-ADK Team"
triggers:
  keywords:
    - frontend
    - UI
    - component
    - React
    - Next.js
    - Vue
    - user interface
    - responsive
    - TypeScript
    - JavaScript
    - state management
    - hooks
    - props
    - JSX
    - TSX
    - client-side
    - browser
    - DOM
    - CSS
    - Tailwind
---
# Frontend Development Specialist

## Quick Reference

Modern Frontend Development - Comprehensive patterns for React 19, Next.js 16, Vue 3.5.

Core Capabilities:

- React 19: Server components, concurrent features, cache(), Suspense
- Next.js 16: App Router, Server Actions, ISR, Route handlers
- Vue 3.5: Composition API, TypeScript, Pinia state management
- Component Architecture: Design systems, compound components, CVA
- Performance: Code splitting, dynamic imports, memoization

When to Use:

- Modern web application development
- Component library creation
- Frontend performance optimization
- UI/UX with accessibility

---

## Module Index

Load specific modules for detailed patterns:

### Framework Patterns

React 19 Patterns in modules/react19-patterns.md:

- Server Components, Concurrent features, cache() API, Form handling

Next.js 16 Patterns in modules/nextjs16-patterns.md:

- App Router, Server Actions, ISR, Route Handlers, Parallel Routes

Vue 3.5 Patterns in modules/vue35-patterns.md:

- Composition API, Composables, Reactivity, Pinia, Provide/Inject

### Architecture Patterns

Component Architecture in modules/component-architecture.md:

- Design tokens, CVA variants, Compound components, Accessibility

State Management in modules/state-management.md:

- Zustand, Redux Toolkit, React Context, Pinia

Performance Optimization in modules/performance-optimization.md:

- Code splitting, Dynamic imports, Image optimization, Memoization

Vercel React Best Practices:

- Performance rules from Vercel Engineering are maintained in the `react-best-practices` skill; use it for performance optimization work.

---

## Works Well With

- moai-domain-backend - Full-stack development
- moai-library-shadcn - Component library integration
- moai-domain-uiux - UI/UX design principles
- moai-lang-typescript - TypeScript patterns
- moai-workflow-testing - Frontend testing

---

## Technology Stack

Frameworks: React 19, Next.js 16, Vue 3.5, Nuxt 4

Languages: TypeScript, JavaScript

Styling: Tailwind CSS 4, CSS Modules, shadcn/ui

State: Zustand, Redux Toolkit, Pinia

Testing: Vitest, Testing Library, Playwright

---

## Resources

Module files in the modules directory contain detailed patterns.

For working code examples, see [examples.md](examples.md).

Official documentation:

- React: <https://react.dev/>
- Next.js: <https://nextjs.org/docs>
- Vue: <https://vuejs.org/>

---

Version: 2.0.0
Last Updated: 2026-01-11
